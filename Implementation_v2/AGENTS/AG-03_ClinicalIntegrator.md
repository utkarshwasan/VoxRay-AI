## File 14: `Implementation_v2/AGENTS/AG-03_ClinicalIntegrator.md`

````markdown
# AG-03: Clinical Integrator (DICOM / FHIR / Audit / Anonymization)

**Role:** Healthcare IT + Clinical Safety  
**Phase:** 2  
**Duration:** Days 7–13  
**Dependencies:** AG-00 complete (feature flags + v2 router exists)  
**Blocking:** YES for clinical features to be enabled in v2

---

## Mission

Add clinical-grade integrations **without breaking v1**:

- DICOM file upload + extraction for inference (feature-gated)
- DICOM anonymization (HIPAA Safe Harbor style) (feature-gated)
- Audit logging (prediction events, model version, hashed identifiers) (feature-gated)
- FHIR DiagnosticReport output (feature-gated)
- Draft compliance docs (ISO 13485 / HIPAA / GDPR pointers)

---

## Required Reading

- `Implementation_v2/SHARED/01_MUST_PRESERVE.md`
- `Implementation_v2/SHARED/02_QUALITY_GATES.md` (Gate 2)
- `Implementation_v2/SHARED/03_API_CONTRACTS.md`
- `Implementation_v2/SHARED/06_FEATURE_FLAGS.md`
- `shared_context/CTX_SYNC.md`

---

## Constraints (Do Not Break)

- Never store raw PHI in logs
- Do not modify Stack Auth logic
- Do not change v1 API responses
- If DICOM libs not installed or unsupported file, return clear 400/422 without crashing server
- All clinical endpoints must be under `/v2/*` and feature-gated:
  - FF_DICOM_SUPPORT
  - FF_DATA_ANONYMIZATION
  - FF_FHIR_INTEGRATION
  - FF_AUDIT_LOGGING

---

## Outputs

- `backend/clinical/dicom/dicom_handler.py`
- `backend/security/anonymizer.py`
- `backend/audit/audit_logger.py`
- `backend/clinical/fhir/fhir_client.py`
- Update `backend/api/v2.py` to include:
  - POST `/v2/predict/dicom`
  - GET/POST `/v2/fhir/...` (as needed)
- Docs:
  - `docs/regulatory/ISO13485.md`
  - `docs/regulatory/HIPAA_Compliance.md`
  - `docs/regulatory/GDPR_Compliance.md`

---

## Task 3.1 — Create Directories

```bash
mkdir -p backend/clinical/{dicom,fhir,decision_support}
mkdir -p backend/security backend/audit docs/regulatory tests/integration
Task 3.2 — DICOM Handler (Parsing + Image Extraction)
Create backend/clinical/dicom/dicom_handler.py

Rules:

Must handle non-DICOM gracefully
Must support pixel array extraction if present
Must normalize pixel values into 0–255 and convert to PIL Image
If compressed DICOM and codecs missing: return error with guidance
Python

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np

@dataclass
class DicomExtractResult:
    ok: bool
    message: str
    image_rgb: Optional[np.ndarray] = None  # HxWx3 uint8
    metadata: Optional[Dict[str, Any]] = None

class DICOMHandler:
    def read_and_extract(self, file_bytes: bytes) -> DicomExtractResult:
        try:
            import pydicom
        except ImportError:
            return DicomExtractResult(False, "pydicom not installed")

        try:
            from io import BytesIO
            ds = pydicom.dcmread(BytesIO(file_bytes), force=True)

            metadata = {
                "study_instance_uid": str(ds.get((0x0020, 0x000D), "")),
                "modality": str(ds.get((0x0008, 0x0060), "")),
                "study_date": str(ds.get((0x0008, 0x0020), "")),
                "patient_id": str(ds.get((0x0010, 0x0020), "")),  # must be hashed before logging/returning
            }

            if not hasattr(ds, "pixel_array"):
                return DicomExtractResult(False, "DICOM has no pixel data", metadata=metadata)

            arr = ds.pixel_array.astype(np.float32)

            # Normalize to 0..255
            arr = arr - np.min(arr)
            denom = np.max(arr) if np.max(arr) > 0 else 1.0
            arr = (arr / denom) * 255.0
            arr = arr.astype(np.uint8)

            # Convert grayscale to RGB
            if arr.ndim == 2:
                rgb = np.stack([arr, arr, arr], axis=-1)
            elif arr.ndim == 3 and arr.shape[-1] == 3:
                rgb = arr
            else:
                # Fallback: attempt squeeze
                arr2 = np.squeeze(arr)
                if arr2.ndim == 2:
                    rgb = np.stack([arr2, arr2, arr2], axis=-1)
                else:
                    return DicomExtractResult(False, f"Unsupported pixel array shape: {arr.shape}", metadata=metadata)

            return DicomExtractResult(True, "OK", image_rgb=rgb, metadata=metadata)

        except Exception as e:
            return DicomExtractResult(False, f"DICOM parsing failed: {e}")
Task 3.3 — Anonymizer (HIPAA-Safe-ish baseline)
Create backend/security/anonymizer.py

Rule:

This is a baseline de-identification tool. In real clinical deployment, add burned-in pixel PHI detection.
Must hash patient_id before returning metadata.
Python

from __future__ import annotations
import os, hashlib
from typing import Dict, Any

class DicomAnonymizer:
    def __init__(self, salt: str | None = None):
        self.salt = salt or os.getenv("ANONYMIZATION_SALT", "voxray_default_salt")

    def hash_identifier(self, value: str) -> str:
        return hashlib.sha256(f"{self.salt}{value}".encode()).hexdigest()[:16]

    def anonymize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        meta = dict(metadata or {})
        pid = str(meta.get("patient_id", ""))
        if pid:
            meta["patient_id_hash"] = self.hash_identifier(pid)
        meta.pop("patient_id", None)
        return meta
Task 3.4 — Audit Logger
Create backend/audit/audit_logger.py

Rule:

Never write raw patient_id
Use user_id from Stack token, but store hashed value only
Store request_id and model_version
Python

from __future__ import annotations
import os, json, hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class AuditLogger:
    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.salt = os.getenv("AUDIT_SALT", "voxray_audit_salt")

    def _hash(self, value: str) -> str:
        return hashlib.sha256(f"{self.salt}{value}".encode()).hexdigest()[:16]

    def log_event(self, event: Dict[str, Any]) -> None:
        ts = datetime.utcnow().isoformat() + "Z"
        event["timestamp"] = ts
        filename = self.log_dir / f"audit-{datetime.utcnow().date().isoformat()}.jsonl"
        with filename.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def log_prediction(
        self,
        user_id: str,
        request_id: str,
        model_version: str,
        prediction: Dict[str, Any],
        input_hash: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        event = {
            "event_type": "prediction",
            "user_id_hash": self._hash(user_id),
            "request_id": request_id,
            "model_version": model_version,
            "input_hash": input_hash,
            "prediction": prediction,
        }
        if extra:
            event["extra"] = extra
        self.log_event(event)
Task 3.5 — FHIR DiagnosticReport (Minimal JSON Template)
Create backend/clinical/fhir/fhir_client.py

Rule:

If fhir.resources isn't installed, output JSON templates only.
Do not hard-require a live FHIR server.
Python

from __future__ import annotations
from typing import Dict, Any, Optional

class FHIRTransformer:
    """
    Minimal transformer: VoxRay result -> FHIR DiagnosticReport JSON.
    """

    def diagnosis_to_snomed(self, diagnosis: str) -> Optional[Dict[str, str]]:
        # Minimal mapping (extend later)
        mapping = {
            "06_PNEUMONIA": {"system": "http://snomed.info/sct", "code": "233604007", "display": "Pneumonia"},
            "04_LUNG_CANCER": {"system": "http://snomed.info/sct", "code": "363346000", "display": "Malignant neoplasm of lung"},
            "05_FRACTURED": {"system": "http://snomed.info/sct", "code": "125605004", "display": "Fracture of bone"},
        }
        return mapping.get(diagnosis)

    def to_diagnostic_report(self, patient_ref: str, conclusion: str, diagnosis: str) -> Dict[str, Any]:
        snomed = self.diagnosis_to_snomed(diagnosis)
        report: Dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "status": "final",
            "subject": {"reference": patient_ref},
            "conclusion": conclusion,
        }
        if snomed:
            report["conclusionCode"] = [{"coding": [snomed]}]
        return report
Task 3.6 — Wire Clinical Endpoints into /v2 Router
Modify the v2 router file created by AG-00 (backend/api/v2.py) to implement:

POST /v2/predict/dicom behind @require_feature(FeatureFlag.DICOM_SUPPORT)
Implementation guidance:

Read bytes from UploadFile
Use DICOMHandler to extract image
Convert to same preprocessing used by v1 inference (224x224 + preprocess_input)
Call existing v1 model for prediction (do not break)
Anonymize metadata (FF_DATA_ANONYMIZATION)
Log audit event (FF_AUDIT_LOGGING)
Task 3.7 — Tests (Integration)
Create minimal tests in tests/integration/test_dicom.py that:

skip if pydicom not installed or fixture missing
assert endpoint returns 503 if flag disabled
assert endpoint returns 200 if flag enabled (requires real DICOM fixture)
Task 3.8 — Regulatory Docs (Draft)
Create:

docs/regulatory/ISO13485.md
docs/regulatory/HIPAA_Compliance.md
docs/regulatory/GDPR_Compliance.md
These can be drafts, but must exist to satisfy Gate 2 checklist.

Handoff
Update:

shared_context/CTX_SYNC.md (status + outputs)
Create shared_context/AG-03_handoff.md:
which endpoints exist
which flags must be enabled to test them
what fixtures are needed
```
````
