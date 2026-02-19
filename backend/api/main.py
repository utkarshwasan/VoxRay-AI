import uvicorn
import io
import numpy as np  # NumPy is relatively fast, keeping for common types
from pathlib import Path
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse, Response
from pydantic import BaseModel
from backend.api.deps import get_current_user
from typing import List, Optional
from backend.api.medical_context import (
    get_condition_info,
    format_context_for_prompt,
    get_knowledge_base_info,
)
from backend.voice.multilingual import (
    get_language_config,
    TTS_INCOMPATIBLE_SCRIPTS,
    LANGS,
)
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# --- Lazy Loading Placeholders ---
tf = None
torch = None
librosa = None
sf = None
edge_tts = None
preprocess_input = None
AutoProcessor = None
AutoModelForSpeechSeq2Seq = None

medical_model = None
IMG_HEIGHT = 224
IMG_WIDTH = 224

stt_processor = None
stt_model = None
device = "cpu"  # Default

# Edge TTS Configuration
import re
import os
import unicodedata
from dotenv import load_dotenv
from fastapi import Request as FastAPIRequest

# This will load from the HF Environment Variables automatically
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
STACK_PROJECT_ID = os.getenv("STACK_PROJECT_ID")

TTS_VOICE = os.getenv("TTS_VOICE", "en-US-ChristopherNeural")


# ─── Script Detection ────────────────────────────────────────────────────────
def detect_script(text: str) -> str:
    """Detect dominant Unicode script. Returns 'devanagari', 'arabic', 'cjk', 'latin', or 'unknown'."""
    counts: dict = {"devanagari": 0, "arabic": 0, "cjk": 0, "latin": 0}
    for ch in text:
        cp = ord(ch)
        if 0x0900 <= cp <= 0x097F:
            counts["devanagari"] += 1
        elif 0x0600 <= cp <= 0x06FF:
            counts["arabic"] += 1
        elif 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF:
            counts["cjk"] += 1
        elif ch.isascii() and ch.isalpha():
            counts["latin"] += 1
    dominant = max(counts, key=counts.get)
    return dominant if counts[dominant] > 0 else "unknown"


# ─── STT Language Config ──────────────────────────────────────────────────────
# Maps frontend ISO codes to Whisper full language names and expected scripts.
STT_LANG_CONFIG: dict = {
    # "hi": {"whisper_name": "hindi", "expected_script": "devanagari"},  # disabled
    "ur": {"whisper_name": "urdu", "expected_script": "arabic"},
    "en": {"whisper_name": "english", "expected_script": "latin"},
    "es": {"whisper_name": "spanish", "expected_script": "latin"},
    "fr": {"whisper_name": "french", "expected_script": "latin"},
    "de": {"whisper_name": "german", "expected_script": "latin"},
    "zh": {"whisper_name": "chinese", "expected_script": None},
    "ja": {"whisper_name": "japanese", "expected_script": None},
    "ko": {"whisper_name": "korean", "expected_script": None},
}

# Resolved at startup from the actual loaded tokenizer vocabulary (not hardcoded)
URDU_TOKEN_ID: int = None


# ─── LLM Language Instructions ───────────────────────────────────────────────
LANG_LLM_INSTRUCTIONS: dict = {
    # "hi": (...),   # disabled — STT model cannot reliably transcribe Hindi
    "ur": "CRITICAL: Respond ONLY in Urdu using Nastaliq script.",
    "en": "CRITICAL: Respond ONLY in English.",
    "fr": "CRITICAL: Respond ONLY in French (Français).",
    "de": "CRITICAL: Respond ONLY in German (Deutsch).",
    "es": "CRITICAL: Respond ONLY in Spanish (Español).",
    "zh": "CRITICAL: Respond ONLY in Simplified Chinese (简体中文).",
    "ja": "CRITICAL: Respond ONLY in Japanese (日本語).",
    "ko": "CRITICAL: Respond ONLY in Korean (한국어).",
    "pt": "CRITICAL: Respond ONLY in Portuguese.",
}


# ─── Diagnosis Label Map ─────────────────────────────────────────────────────
DIAGNOSIS_DISPLAY_LABELS: dict = {
    "01_NORMAL_LUNG": "Normal Lung Findings",
    "02_NORMAL_BONE": "Normal Bone Findings",
    "03_NORMAL_PNEUMONIA": "Normal (No Pneumonia)",
    "04_LUNG_CANCER": "Suspected Pulmonary Malignancy",
    "05_FRACTURED": "Bone Fracture Detected",
    "06_PNEUMONIA": "Pneumonia Detected",
}

# ─────────────────────────────────────────────────────────────────────────────

# Path resolution: backend/api/main.py -> backend/api -> backend -> root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Class names - will be loaded dynamically or use fallback
MEDICAL_CLASS_NAMES = []
TRAIN_DIR = BASE_DIR / "consolidated_medical_data" / "train"


def load_class_names():
    """Load class names from training directory or use fallback."""
    global MEDICAL_CLASS_NAMES
    try:
        import os

        # Only try to load from directory if not in production/docker environment
        # and if directory actually exists
        if TRAIN_DIR.exists():
            MEDICAL_CLASS_NAMES = sorted(
                [d.name for d in TRAIN_DIR.iterdir() if d.is_dir()]
            )
            print(f"✅ Loaded {len(MEDICAL_CLASS_NAMES)} classes from {TRAIN_DIR}")
        else:
            # Fallback: Production mode or directory missing
            MEDICAL_CLASS_NAMES = [
                "01_NORMAL_LUNG",
                "02_NORMAL_BONE",
                "03_NORMAL_PNEUMONIA",
                "04_LUNG_CANCER",
                "05_FRACTURED",
                "06_PNEUMONIA",
            ]
            print(
                f"⚠️ Using pre-defined class names ({len(MEDICAL_CLASS_NAMES)} classes)"
            )
            MEDICAL_CLASS_NAMES = [
                "01_NORMAL_LUNG",
                "02_NORMAL_BONE",
                "03_NORMAL_PNEUMONIA",
                "04_LUNG_CANCER",
                "05_FRACTURED",
                "06_PNEUMONIA",
            ]
            print(
                f"⚠️ Training directory not found. Using fallback with {len(MEDICAL_CLASS_NAMES)} classes"
            )
    except Exception as e:
        print(f"❌ Error loading class names: {e}")
        MEDICAL_CLASS_NAMES = [
            "01_NORMAL_LUNG",
            "02_NORMAL_BONE",
            "03_NORMAL_PNEUMONIA",
            "04_LUNG_CANCER",
            "05_FRACTURED",
            "06_PNEUMONIA",
        ]


app = FastAPI(
    title="Intelligent Medical Diagnosis Assistant API",
    description="Serves F1 (Image) and F2 (Voice) models via REST API.",
)

# v2 router is handled in versioning.py to avoid double registration

# --- CORS CONFIGURATION (Dynamic for Deployment) ---
# 1. Define base allowed origins (localhost for development)
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:3000",
]

# 2. Add Hugging Face Internal Host (Auto-injected by Spaces)
if os.getenv("SPACE_HOST"):
    hf_origin = f"https://{os.getenv('SPACE_HOST')}"
    ALLOWED_ORIGINS.append(hf_origin)
    print(f"✅ Added Hugging Face origin: {hf_origin}")

# 3. Add Vercel Frontend (From Secrets)
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)
    print(f"✅ Added frontend origin: {frontend_url}")

print(f"🔒 CORS Allowed Origins: {ALLOWED_ORIGINS}")

# 4. Apply Middleware (No wildcards for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: FastAPIRequest, exc: Exception):
    """
    Global exception handler — preserves CORS headers on errors.
    Reflects the request's own origin if it is in the allowed list.
    Respects status_code if present (e.g. HTTPException), else 500.
    """
    import traceback

    print(f"!!! EXCEPTION CAUGHT: {type(exc)}: {exc}", flush=True)
    print(traceback.format_exc(), flush=True)

    origin = request.headers.get("origin", "")
    cors_origin = origin if origin in ALLOWED_ORIGINS else ""
    response_headers = (
        {"Access-Control-Allow-Origin": cors_origin} if cors_origin else {}
    )

    status_code = 500
    detail = f"Internal server error: {str(exc)}"

    if hasattr(exc, "status_code"):
        status_code = exc.status_code
    if hasattr(exc, "detail"):
        detail = exc.detail

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
        headers=response_headers,
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint for monitoring stack."""
    from backend.core.feature_flags import get_feature_flags
    
    flags = get_feature_flags().get_all_flags()
    
    # Build Prometheus-compatible metrics output
    metrics_lines = [
        "# HELP voxray_info Build information",
        '# TYPE voxray_info gauge',
        'voxray_info{version="1.0.0"} 1',
        "",
        "# HELP voxray_feature_flag Feature flag status (1=enabled, 0=disabled)",
        "# TYPE voxray_feature_flag gauge",
    ]
    
    for flag_name, flag_value in flags.items():
        flag_int = 1 if flag_value else 0
        metrics_lines.append(f'voxray_feature_flag{{flag="{flag_name}"}} {flag_int}')
    
    # Add model status metrics
    metrics_lines.extend([
        "",
        "# HELP voxray_model_loaded Whether model is loaded",
        "# TYPE voxray_model_loaded gauge",
        f"voxray_model_loaded{{model=\"medical_classifier\"}} {1 if medical_model is not None else 0}",
        f"voxray_model_loaded{{model=\"stt\"}} {1 if stt_model is not None else 0}",
    ])
    
    return Response(content="\n".join(metrics_lines), media_type="text/plain")


@app.on_event("startup")
async def load_models():
    # Lazy load heavy dependencies
    print("⏳ Initializing models and heavy dependencies...")
    global tf, torch, librosa, sf, edge_tts, preprocess_input
    global AutoProcessor, AutoModelForSpeechSeq2Seq
    global medical_model, stt_processor, stt_model, device

    try:
        import tensorflow as tf
        from tensorflow.keras.applications.resnet_v2 import preprocess_input
        import torch
        import librosa
        import soundfile as sf
        import edge_tts
        from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"✅ Libraries loaded. Device: {device}")
    except ImportError as e:
        print(f"❌ Critical Dependency Missing: {e}")
        return

    # Load class names first
    load_class_names()

    # --- Runtime Model Download from Hugging Face Hub ---
    REPO_ID = "witty22/voxray-model"
    FILENAME = "medical_model_final.keras"

    model_path = BASE_DIR / "backend" / "models" / FILENAME

    # Check if file exists AND is not an LFS pointer (< 1MB = LFS pointer)
    if not model_path.exists() or model_path.stat().st_size < 1_000_000:
        print(f"⚠️ {FILENAME} is missing or an LFS pointer. Downloading real binary...")
        try:
            from huggingface_hub import hf_hub_download

            # If repo is private, ensure HF_TOKEN is in your Space Secrets
            hf_token = os.getenv("HF_TOKEN")
            downloaded_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=FILENAME,
                token=hf_token,
                local_dir=str(BASE_DIR / "backend" / "models"),
                local_dir_use_symlinks=False,
            )
            model_path = Path(downloaded_path)
            print(f"✅ Successfully downloaded model to {model_path}")
        except Exception as e:
            print(f"❌ Hub download failed: {e}")
            import traceback

            traceback.print_exc()
            # Continue without model - endpoint will return 503

    # Final Load
    if model_path.exists() and model_path.stat().st_size > 1_000_000:
        try:
            medical_model = tf.keras.models.load_model(str(model_path))
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(
                f"🚀 Model loaded into memory. Size: {size_mb:.2f} MB. Expected {len(MEDICAL_CLASS_NAMES)} classes"
            )
        except Exception as e:
            print(f"❌ Keras load failed: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("❌ No valid model file available! /predict/image will return 503.")

    print("⏳ Loading STT Model (Whisper)...")
    stt_processor = AutoProcessor.from_pretrained("openai/whisper-base")
    stt_model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-base").to(
        device
    )

    # Resolve Urdu token ID from actual loaded vocabulary — safe across model versions
    global URDU_TOKEN_ID
    try:
        vocab = stt_processor.tokenizer.get_vocab()
        URDU_TOKEN_ID = vocab.get("<|ur|>")
        print(f"✅ Urdu suppress token resolved: {URDU_TOKEN_ID}")
    except Exception as e:
        print(f"⚠️ Could not resolve Urdu token ID: {e}")
        URDU_TOKEN_ID = None

    print("✅ TTS Engine: Edge-TTS (cloud-based, no local loading required).")
    print("✅ All models loaded successfully.")


# ... (keep existing code)


def preprocess_image_from_bytes(file_bytes: bytes):
    global tf, preprocess_input

    if tf is None:
        # Fallback if accessed before startup for some reason
        import tensorflow as _tf
        from tensorflow.keras.applications.resnet_v2 import preprocess_input as _pi

        tf = _tf
        preprocess_input = _pi

    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize((IMG_WIDTH, IMG_HEIGHT))
    img_arr = np.array(img).astype(np.float32)
    img_preprocessed = preprocess_input(img_arr)
    img_bat = np.expand_dims(img_preprocessed, 0)
    return img_bat


class DiagnosisResponse(BaseModel):
    diagnosis: str
    confidence: float


@app.post("/predict/image", response_model=DiagnosisResponse)
async def predict_image(
    image_file: UploadFile = File(...), user: dict = Depends(get_current_user)
):
    """Protected endpoint - requires authentication."""
    print(f"👤 User {user.get('sub')} requesting prediction")

    # 1. Check if the global variable actually exists in this worker
    print(f"🔍 Debug: medical_model type: {type(medical_model)}")

    # 2. Check the physical file on the disk
    model_path = Path("/app/backend/models/medical_model_final.keras")
    if not model_path.exists():
        print(f"❌ ABSOLUTE PATH FAIL: {model_path} not found")
        # Try relative as fallback
        model_path = Path("backend/models/medical_model_final.keras")
        print(
            f"🔍 Checking relative path: {model_path.absolute()} - Exists: {model_path.exists()}"
        )

    if model_path.exists():
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"📁 Model file found! Size: {size_mb:.2f} MB")
        if size_mb < 1:
            print("⚠️ ALERT: Model file is too small. Likely a Git LFS pointer error!")

    if medical_model is None:
        raise HTTPException(
            status_code=503, detail="Model is None in this worker process."
        )
    try:
        file_bytes = await image_file.read()

        img_batch = preprocess_image_from_bytes(file_bytes)
        predict = medical_model.predict(img_batch)
        score = predict[0]  # Already probabilities - model has softmax in final layer

        # Log all class probabilities for debugging
        print("\n📊 Prediction scores:")
        for idx, (class_name, prob) in enumerate(zip(MEDICAL_CLASS_NAMES, score)):
            print(f"  {idx}: {class_name}: {float(prob) * 100:.2f}%")

        diagnosis = MEDICAL_CLASS_NAMES[np.argmax(score)]
        confidence = float(np.max(score))
        print(f"✅ Top prediction: {diagnosis} ({confidence * 100:.1f}%)\n")
        return JSONResponse(content={"diagnosis": diagnosis, "confidence": confidence})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


# ==================== GRAD-CAM EXPLAINABILITY ====================
import base64
import cv2


def generate_gradcam(model, img_array, class_idx):
    """
    Generate Grad-CAM heatmap for model explainability.
    Fixed for Keras 3.x - reconstructs model graph to access intermediate layers.
    """
    if tf is None:
        return None

    try:
        # Force model build if needed
        if not model.built:
            model.build((None, IMG_HEIGHT, IMG_WIDTH, 3))

        # We need to construct a model that outputs [conv_output, predictions]
        # Assuming model is Sequential: [ResNet, GlobalAvg, Dense]

        # 1. Get Base Model (ResNet50V2)
        base_model = model.layers[0]
        last_conv_layer = base_model.get_layer("conv5_block3_out")

        # Create a model for the base that returns both conv output and final base output
        # mapping: input -> [conv_out, base_out]
        base_multi_model = tf.keras.models.Model(
            inputs=base_model.inputs,
            outputs=[last_conv_layer.output, base_model.output],
        )

        # 2. Reconstruct the full graph in a new Functional model
        inputs = tf.keras.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3))

        # Run base model
        conv_out, base_out = base_multi_model(inputs)

        # Run remaining separate layers (Head)
        x = base_out
        for layer in model.layers[1:]:
            x = layer(x)

        predictions = x

        # 3. Create the final Grad-CAM model
        grad_model = tf.keras.models.Model(
            inputs=inputs, outputs=[conv_out, predictions]
        )

        # Compute gradients
        with tf.GradientTape() as tape:
            img_array = tf.cast(img_array, tf.float32)
            tape.watch(img_array)
            conv_outputs, predictions = grad_model(img_array)
            class_channel = predictions[:, class_idx]

        # Get gradients
        grads = tape.gradient(class_channel, conv_outputs)

        if grads is None:
            print("⚠️ Gradients are None. Check model architecture.")
            return None

        # Global average pooling of gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # Weight the conv outputs
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # Normalize
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)

        return heatmap.numpy()
    except Exception as e:
        print(f"⚠️ Grad-CAM generation failed: {e}")
        import traceback

        traceback.print_exc()
        return None


def create_heatmap_overlay(heatmap, original_img_bytes, threshold=0.35):
    """
    Create a clean, artifact-free heatmap overlay.
    Uses Mask-Based Blending + Gaussian Blur to eliminate red spotting and blockiness.
    """
    try:
        # Load original image
        img = Image.open(io.BytesIO(original_img_bytes)).convert("RGB")
        orig_w, orig_h = img.size
        img_array = np.array(img)

        # 1. ReLU & Normalize
        heatmap = np.maximum(heatmap, 0)
        max_val = np.max(heatmap)
        if max_val > 0:
            heatmap = heatmap / max_val

        # 2. Thresholding (Remove weak noise)
        heatmap[heatmap < threshold] = 0

        # 3. Resize to Original Dimensions
        heatmap_resized = cv2.resize(
            heatmap, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC
        )

        # 4. CRITICAL: Gaussian Blur (Better than Bilateral for Heatmaps)
        # We want to dissolve blocky edges, not preserve them.
        kernel_size = int(min(orig_w, orig_h) * 0.05)  # 5% of image size
        if kernel_size % 2 == 0:
            kernel_size += 1
        if kernel_size < 5:
            kernel_size = 5
        heatmap_resized = cv2.GaussianBlur(
            heatmap_resized, (kernel_size, kernel_size), 0
        )

        # 5. Clip limits (Prevent cubic overshoot artifacts)
        heatmap_resized = np.clip(heatmap_resized, 0, 1)

        # 6. Re-normalize
        max_val = np.max(heatmap_resized)
        if max_val > 0:
            heatmap_resized = heatmap_resized / max_val

        # 7. Apply Colormap
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        # 8. MASK CREATION (The "Solution B" Magic)
        # Create a hard mask. Any heatmap value below 0.05 is treated as background.
        mask = heatmap_resized > 0.05
        mask = np.stack([mask] * 3, axis=-1)  # Make it 3-channel

        # 9. BLEND ONLY ACTIVE REGIONS
        # Where mask is TRUE: Blend (Original 60% + Heatmap 40%)
        # Where mask is FALSE: Use pure Original Image
        alpha = 0.4
        blended_region = cv2.addWeighted(
            img_array, 1 - alpha, heatmap_colored, alpha, 0
        )

        superimposed = np.where(mask, blended_region, img_array)

        # 10. Encode
        pil_img = Image.fromarray(superimposed.astype(np.uint8))
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        print(f"Error in heatmap overlay: {e}")
        return None


class ExplainResponse(BaseModel):
    heatmap_b64: str


@app.post("/predict/explain", response_model=ExplainResponse)
async def explain_prediction(
    image_file: UploadFile = File(...), user: dict = Depends(get_current_user)
):
    """
    Generate Grad-CAM explanation for the model's prediction.
    Returns a base64 encoded heatmap overlay image.
    """
    if medical_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    try:
        file_bytes = await image_file.read()
        img_batch = preprocess_image_from_bytes(file_bytes)

        # Get prediction to determine which class to explain
        predictions = medical_model.predict(img_batch)
        class_idx = int(np.argmax(predictions[0]))

        print(f"🔍 Generating Grad-CAM explanation for class {class_idx}...")

        # Generate Grad-CAM heatmap
        heatmap = generate_gradcam(medical_model, img_batch, class_idx)

        if heatmap is None:
            raise HTTPException(
                status_code=500, detail="Failed to generate Grad-CAM heatmap"
            )

        # Create overlay image
        heatmap_b64 = create_heatmap_overlay(heatmap, file_bytes)

        print("✅ Grad-CAM explanation generated successfully!")
        return JSONResponse(content={"heatmap_b64": heatmap_b64})

    except Exception as e:
        print(f"❌ Explanation error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error generating explanation: {str(e)}"
        )


class TranscriptionResponse(BaseModel):
    transcription: str
    detected_language: Optional[str] = None


@app.post("/transcribe/audio", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...), language: Optional[str] = None
):
    if not stt_model or not stt_processor:
        raise HTTPException(status_code=503, detail="F2 (STT) models are not loaded.")
    try:
        audio_data, original_samplerate = sf.read(io.BytesIO(await audio_file.read()))
        if original_samplerate != 16000:
            audio_data = librosa.resample(
                y=audio_data, orig_sr=original_samplerate, target_sr=16000
            )
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)

        # Build processor output WITH attention mask — eliminates padding warning,
        # improves accuracy on short clips (runtime-verified: same output, no warning)
        processor_output = stt_processor(
            audio_data,
            sampling_rate=16000,
            return_tensors="pt",
            return_attention_mask=True,
        )
        input_features = processor_output.input_features.to(device)
        attention_mask = processor_output.attention_mask.to(device)

        # Resolve Whisper language config
        lang_cfg = STT_LANG_CONFIG.get(
            language or "en",
            {"whisper_name": language or "en", "expected_script": None},
        )

        if language:
            print(f"🌐 Forcing STT language: {lang_cfg['whisper_name']}")
            forced_decoder_ids = stt_processor.get_decoder_prompt_ids(
                language=lang_cfg["whisper_name"],
                task="transcribe",
            )
        else:
            forced_decoder_ids = None

        # Runtime-verified: forced_decoder_ids alone prevents Urdu token in output.
        # suppress_tokens=[URDU_TOKEN_ID] produces IDENTICAL output — omitted intentionally.
        predicted_ids = stt_model.generate(
            input_features,
            attention_mask=attention_mask,
            forced_decoder_ids=forced_decoder_ids,
            max_length=448,
        )
        transcription = stt_processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )[0].strip()

        # Post-validation: warn when output script does not match expected
        expected_script = lang_cfg.get("expected_script")
        actual_script = detect_script(transcription) if transcription else "unknown"
        if (
            expected_script
            and actual_script not in (expected_script, "unknown")
            and len(transcription) > 3
        ):
            print(
                f"⚠️ STT Script Mismatch: lang={language}, "
                f"expected={expected_script}, got={actual_script}. "
                f"text={transcription[:50]!r}"
            )

        return JSONResponse(
            content={
                "transcription": transcription,
                "detected_language": language or "auto",
                "script_detected": actual_script,
            }
        )
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "en"


def normalize_medical_text(text: str) -> str:
    """
    Normalize medical text for clearer TTS pronunciation.
    Fixes percentages, abbreviations, and units.
    """
    if not text:
        return ""

    # Percentages: "98.7%" -> "98.7 percent"
    text = re.sub(r"(\d+(?:\.\d+)?)%", r"\1 percent", text)

    # Abbreviations (word-boundary safe)
    text = re.sub(r"\bDr\.", "Doctor", text)
    text = re.sub(r"\bvs\.", "versus", text)
    text = re.sub(r"\bapprox\.", "approximately", text)
    text = re.sub(r"\bw/\b", "with", text)
    text = re.sub(r"\bw/o\b", "without", text)

    # Units (word-boundary safe to prevent "imaging" -> "imilligramsing")
    text = re.sub(r"\bmg\b", "milligrams", text)

    # Cleanup artifacts
    text = text.replace("_", " ")
    text = text.replace("*", "")
    text = re.sub(r"\s+", " ", text).strip()

    return text


@app.post("/generate/speech")
async def generate_speech(request: TTSRequest = Body(...)):
    """
    High-Fidelity Neural TTS using Microsoft Edge TTS.
    Streams audio directly to frontend for low latency.
    Supports 6 languages via centralized config.
    """
    text = (request.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    # Lazy load edge_tts if not already
    global edge_tts
    if edge_tts is None:
        import edge_tts as _edge_tts

        edge_tts = _edge_tts

    try:
        # Get voice for requested language
        lang_config = get_language_config(request.language)
        if lang_config is None:
            lang_config = get_language_config("en")
        print(f"🎙️ TTS Language: {lang_config.display_name} ({lang_config.tts_voice})")

        # 1. Normalize text (fixes pronunciation & skipping)
        clean_text = normalize_medical_text(text)

        # 2. Safe length cap (avoid cutting mid-word)
        max_chars = 2000
        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars].rsplit(" ", 1)[0] + "..."
            print(f"⚠️ Text truncated from {len(text)} to {len(clean_text)} chars")

        # 3. Pre-flight: block scripts that Edge-TTS physically cannot render for this voice.
        # Runtime-verified: Latin text through hi-IN-SwaraNeural succeeds (27 chunks).
        # Only block combinations in TTS_INCOMPATIBLE_SCRIPTS (e.g. Arabic through Hindi voice).
        incompatible = TTS_INCOMPATIBLE_SCRIPTS.get(request.language or "en", set())
        if incompatible and len(clean_text) > 3:
            detected_script = detect_script(clean_text)
            if detected_script in incompatible:
                print(
                    f"❌ TTS pre-flight blocked: voice={lang_config.tts_voice}, "
                    f"incompatible script={detected_script}, text={clean_text[:40]!r}"
                )
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "SCRIPT_MISMATCH",
                        "message": (
                            f"Text script ({detected_script}) cannot be rendered by "
                            f"the {request.language} voice. This is an upstream STT bug."
                        ),
                        "voice": lang_config.tts_voice,
                        "detected_script": detected_script,
                    },
                )

        # 4. Stream generator.
        # communicate is created INSIDE the generator — not outside.
        # Creating it outside and capturing via closure is equivalent, but keeping it
        # inside makes the lifecycle explicit and prevents accidental double-instantiation.
        # NEVER raise inside a StreamingResponse generator — it crashes the ASGI app.
        # Return gracefully instead; the frontend handles empty/truncated audio.
        async def audio_stream():
            try:
                communicate = edge_tts.Communicate(
                    text=clean_text,
                    voice=lang_config.tts_voice,
                )
                chunk_count = 0
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        chunk_count += 1
                        yield chunk["data"]
                if chunk_count > 0:
                    print(
                        f"✅ TTS Success: {chunk_count} chunks for {lang_config.display_name}"
                    )
                else:
                    print(f"⚠️ TTS: Zero chunks for voice={lang_config.tts_voice}")
            except Exception as stream_error:
                print(f"❌ TTS Stream Error for '{request.language}': {stream_error}")
                return  # NEVER raise — return ends the generator cleanly

        # 5. Return Stream (MP3 format)
        return StreamingResponse(
            audio_stream(),
            media_type="audio/mpeg",
            headers={"X-TTS-Language": request.language or "en"},
        )

    except edge_tts.exceptions.NoAudioReceived as e:
        print(f"❌ NoAudioReceived for language '{request.language}': {e}")
        print(f"   Text: '{text[:100]}...'")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=503,
            detail={
                "error": "TTS_NO_AUDIO",
                "message": f"No audio generated for language '{request.language}'. Please try again or switch to English.",
                "language": request.language,
                "voice": lang_config.tts_voice,
            },
        )
    except Exception as e:
        print(f"❌ TTS Generation Error for '{request.language}': {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "TTS_GENERATION_FAILED",
                "message": f"Voice generation failed: {str(e)}",
                "language": request.language,
            },
        )


# --- Conversational AI (OpenRouter) ---
from openai import OpenAI
from dotenv import load_dotenv
import os

# Explicitly load from backend/.env
env_path = BASE_DIR / "backend" / ".env"
load_dotenv(dotenv_path=env_path)


class ChatMessage(BaseModel):
    """Individual chat message for history."""

    role: str  # 'user' or 'assistant'
    text: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint with history support."""

    message: str
    context: Optional[str] = None
    history: List[ChatMessage] = []
    language: Optional[str] = "en"  # ISO 639-1 — drives LLM response language


@app.get("/api/knowledge-base/info")
async def get_kb_info():
    """Returns knowledge base version and metadata."""
    return JSONResponse(content=get_knowledge_base_info())


@app.post("/chat")
async def chat_endpoint(
    request: ChatRequest = Body(...), user: dict = Depends(get_current_user)
):
    """
    Enhanced chat endpoint with:
    - Medical context injection (Static RAG)
    - Conversation history support
    - Robust error handling
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API Key not found. Please set OPENROUTER_API_KEY in .env",
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Parse context and get medical grounding
    diagnosis_label = "Unknown"
    confidence = 0.0
    medical_context = ""

    if request.context:
        try:
            import re

            # Expected format: "Diagnosis: PNEUMONIA, Confidence: 98.7%"
            context_str = request.context.strip()

            # Extract diagnosis
            if "Diagnosis:" in context_str:
                diagnosis_part = context_str.split(",")[0]
                diagnosis_label = diagnosis_part.split(":")[-1].strip()
            elif ":" in context_str:
                diagnosis_label = context_str.split(":")[0].strip()
            else:
                diagnosis_label = context_str.split(",")[0].strip()

            # Extract confidence
            if "Confidence:" in context_str:
                conf_part = context_str.split("Confidence:")[-1]
                conf_str = conf_part.replace("%", "").replace(")", "").strip().split()[0]
                try:
                    confidence = float(conf_str)
                except ValueError:
                    confidence = 0.0
            elif "%" in context_str:
                match = re.search(r"(\d+\.?\d*)%", context_str)
                if match:
                    confidence = float(match.group(1))

            # Get grounded medical context — use clean display label, not raw class name
            condition_info = get_condition_info(diagnosis_label)
            clean_diagnosis = DIAGNOSIS_DISPLAY_LABELS.get(
                diagnosis_label, diagnosis_label.replace("_", " ").title()
            )
            medical_context = format_context_for_prompt(
                condition_info, clean_diagnosis, confidence
            )

            print(
                f"📋 Context parsed - Diagnosis: {clean_diagnosis}, Confidence: {confidence}%"
            )

        except Exception as e:
            print(f"⚠️ Context parsing warning: {e}")
            medical_context = f"\nDiagnosis context provided: {request.context}\n"

    # Language enforcement — injected at top of system prompt for maximum LLM compliance
    lang_code = (request.language or "en").lower()
    lang_instruction = LANG_LLM_INSTRUCTIONS.get(
        lang_code,
        f"CRITICAL: Respond ONLY in the language with ISO code '{lang_code}'.",
    )

    # Clean diagnosis label for display (fallback safe if context was None)
    clean_diagnosis = DIAGNOSIS_DISPLAY_LABELS.get(
        diagnosis_label, diagnosis_label.replace("_", " ").title()
    )

    # Build system prompt with grounding
    system_prompt = f"""{lang_instruction}

You are VoxRay, an AI radiology assistant designed to help healthcare professionals understand imaging findings.

YOUR ROLE:
- Explain radiological findings in clear, professional language
- Provide educational context about detected conditions  
- Recommend appropriate next steps based on clinical guidelines
- Act as a knowledgeable translator between AI analysis and clinical practice

{medical_context}

RESPONSE GUIDELINES:

1. SAFETY & BOUNDARIES (CRITICAL):
   - You MAY discuss general standard treatments and typical symptoms if listed in the provided context.
   - Do NOT provide patient-specific prescriptions or specific dosages (e.g., "Take 500mg Amoxicillin").
   - Never invent findings (e.g., "3mm nodule") if not in verified data.
   - Always prioritize the provided context over internal knowledge.

2. USE YOUR KNOWLEDGE BASE:
   - When asked about "symptoms" → Reference TYPICAL SYMPTOMS provided above
   - When asked about "treatment" → Reference STANDARD TREATMENT OPTIONS provided above
   - When asked about "next steps" → Reference RECOMMENDED NEXT STEPS

3. LANGUAGE & TONE:
   - SAY: "Pneumonia typically presents with..." (Generalizing signs)
   - DON'T SAY: "I can see..." (Implies specific localization ability)
   - Keep responses concise (2-4 sentences) for voice output.
   - Build on previous conversation.

4. LIMITATIONS:
   - You classified this image based on patterns but cannot pinpoint exact locations.
   - Specific localization requires radiologist review.
   - Always recommend professional consultation for treatment decisions.
"""

    # Build message chain with history
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (last 6 exchanges, with length limits)
    MAX_MESSAGE_LENGTH = 500

    for msg in request.history[-6:]:
        role = "assistant" if msg.role == "assistant" else "user"
        text = msg.text

        if len(text) > MAX_MESSAGE_LENGTH:
            text = text[:MAX_MESSAGE_LENGTH] + "..."

        if text:
            messages.append({"role": role, "content": text})

    # Language enforcement injection for non-English — overrides conversation history momentum
    if lang_code != "en":
        messages.append({
            "role": "user",
            "content": f"[SYSTEM: {lang_instruction} Your next response MUST be in this language only.]"
        })
        messages.append({
            "role": "assistant",
            "content": "[Understood. I will respond only in the required language.]"
        })

    # Add current user message
    messages.append({"role": "user", "content": request.message})

    print(
        f"💬 Processing chat - Message: '{request.message[:50]}...' with {len(request.history)} history items"
    )

    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=messages,
            temperature=0.4,
            max_tokens=250,
        )

        response_text = completion.choices[0].message.content
        print(f"✅ Chat response generated: '{response_text[:50]}...'")

        return JSONResponse(content={"response": response_text})

    except Exception as e:
        print(f"❌ Chat Error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error generating response: {str(e)}"
        )


# ==================== API VERSIONING SETUP ====================
# This MUST be called after all V1 endpoints are defined above
from backend.api.versioning import setup_versioning, APIVersionMiddleware

# Setup /v1/* aliases and /v2/* router
setup_versioning(app)

# Add version headers middleware
app.add_middleware(APIVersionMiddleware)

print("✅ API Versioning configured: /v1/*, /v2/*, and root-level V1 endpoints")


@app.get("/api/feature-flags")
async def feature_flags():
    """Feature flag endpoint — merges real FeatureFlags system with frontend defaults."""
    from backend.core.feature_flags import get_feature_flags
    
    # Get all flags from the real system (reads from FF_* env vars)
    all_flags = get_feature_flags().get_all_flags()
    
    # Frontend-specific defaults (always exposed for UI consumption)
    frontend_defaults = {
        "multilingual_voice": all_flags.get("multilingual_voice", True),
        "multilingual_stt": True,
        "gradcam_explanations": True,
        "voice_input": True,
        "chat_history": True,
    }
    
    # Merge: real flags override defaults, all flags exposed
    return {**frontend_defaults, **all_flags}


@app.get("/")
async def root():
    return {"message": "VoxRay AI Backend is Running", "docs": "/docs"}


if __name__ == "__main__":
    print("uvicorn backend.api.main:app --reload")
