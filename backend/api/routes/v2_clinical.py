from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from backend.core.feature_flags import require_feature, FeatureFlag
from backend.api.deps import get_current_user
from backend.clinical.dicom.dicom_handler import DICOMHandler
from backend.security.anonymizer import DicomAnonymizer
from backend.audit.audit_logger import AuditLogger
from tensorflow.keras.applications.resnet_v2 import preprocess_input
from PIL import Image
import numpy as np

router = APIRouter()
dicom_handler = DICOMHandler()
anonymizer = DicomAnonymizer()
audit_logger = AuditLogger()

IMG_HEIGHT = 224
IMG_WIDTH = 224


@router.post("/predict/dicom")
@require_feature(FeatureFlag.DICOM_SUPPORT)
async def predict_dicom(
    dicom_file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
):
    """
    Predict diagnosis from DICOM file.
    Feature encoded: FF_DICOM_SUPPORT
    """
    # Runtime import to avoid circular dependency
    import backend.api.main as main_app
    from backend.api.main import MEDICAL_CLASS_NAMES

    if main_app.medical_model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    # 1. Read and Parse DICOM
    file_bytes = await dicom_file.read()
    extract_result = dicom_handler.read_and_extract(file_bytes)

    if not extract_result.ok:
        raise HTTPException(
            status_code=422, detail=f"DICOM processing failed: {extract_result.message}"
        )

    # 2. Preprocess for ResNet50V2 (224x224, preprocessed)
    try:
        rgb_array = extract_result.image_rgb
        img = Image.fromarray(rgb_array)
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))
        img_arr = np.array(img).astype(np.float32)
        img_preprocessed = preprocess_input(img_arr)
        img_batch = np.expand_dims(img_preprocessed, 0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image preprocessing failed: {e}")

    # 3. Predict
    try:
        # Use existing v1 model
        prediction_scores = main_app.medical_model.predict(img_batch)[0]
        diagnosis_idx = np.argmax(prediction_scores)
        diagnosis = MEDICAL_CLASS_NAMES[diagnosis_idx]
        confidence = float(np.max(prediction_scores))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

    # 4. Handle Metadata (Anonymization)
    metadata = extract_result.metadata or {}
    from backend.core.feature_flags import check_flag

    anonymization_applied = False
    if check_flag(FeatureFlag.DATA_ANONYMIZATION):
        metadata = anonymizer.anonymize_metadata(metadata)
        anonymization_applied = True

    # 5. Audit Logging
    if check_flag(FeatureFlag.AUDIT_LOGGING):
        import uuid

        request_id = str(uuid.uuid4())

        import hashlib

        input_hash = hashlib.sha256(file_bytes).hexdigest()

        user_id = user.get("sub", "unknown")

        try:
            audit_logger.log_prediction(
                user_id=user_id,
                request_id=request_id,
                model_version="v1_resnet50v2",
                prediction={"diagnosis": diagnosis, "confidence": confidence},
                input_hash=input_hash,
                extra={
                    "modality": metadata.get("modality"),
                    "anonymized": anonymization_applied,
                },
            )
        except Exception as e:
            print(f"Audit log failed: {e}")

    return {
        "diagnosis": diagnosis,
        "confidence": confidence,
        "dicom_metadata": metadata,
        "image_extracted": True,
        "anonymization_applied": anonymization_applied,
    }
