import uvicorn
import io
import librosa
import soundfile as sf
import torch
import tensorflow as tf
import numpy as np
from pathlib import Path
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from backend.api.deps import get_current_user
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from datasets import load_dataset
from tensorflow.keras.applications.resnet_v2 import preprocess_input
from typing import List, Optional
from backend.api.medical_context import (
    get_condition_info,
    format_context_for_prompt,
    get_knowledge_base_info,
)

medical_model = None
IMG_HEIGHT = 224
IMG_WIDTH = 224

stt_processor = None
stt_model = None

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Edge TTS Configuration (cloud-based, no local model)
import edge_tts
import re
import os

TTS_VOICE = os.getenv("TTS_VOICE", "en-US-ChristopherNeural")

# --- Stack Auth Manual Verification ---
import jwt
import requests
from jwt import PyJWKClient

# Stack Auth Configuration
STACK_PROJECT_ID = os.getenv("STACK_PROJECT_ID", "your-project-id")


def verify_stack_token(token: str):
    """
    Manually verify Stack Auth JWT token using JWKS.
    Replacing the deprecated stack-auth-python SDK.
    """
    # This URL is standard for Stack Auth
    url = f"https://api.stack-auth.com/api/v1/projects/{STACK_PROJECT_ID}/.well-known/jwks.json"

    try:
        jwks_client = PyJWKClient(url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=STACK_PROJECT_ID,
            leeway=60,  # Add leeway for clock skew
        )
        return payload  # Returns user info (sub, email, etc.)
    except Exception as e:
        print(f"❌ Token validation failed: {str(e)}")
        return None


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


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "version": "1.0.0"}


@app.on_event("startup")
def load_models():
    global medical_model, stt_processor, stt_model

    # Load class names first
    load_class_names()

    # Model path using pathlib (models moved to backend/models)
    model_path = BASE_DIR / "backend" / "models" / "medical_model_final.keras"
    try:
        medical_model = tf.keras.models.load_model(str(model_path))
        print(
            f"✅ Model loaded from {model_path}. Expected {len(MEDICAL_CLASS_NAMES)} classes"
        )
    except Exception as e:
        print(
            f"WARNING: Could not load F1 model from {model_path}. /predict/image will fail. Error: {e}"
        )

    print("⏳ Loading STT Model (Whisper)...")
    stt_processor = AutoProcessor.from_pretrained("openai/whisper-base")
    stt_model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-base").to(
        device
    )

    print("✅ TTS Engine: Edge-TTS (cloud-based, no local loading required).")
    print("✅ All models loaded successfully.")


# ... (keep existing code)


def preprocess_image_from_bytes(file_bytes: bytes):
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
    if medical_model is None:
        raise HTTPException(status_code=503, detail="F1 Diagnosis model not loaded.")
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


@app.post("/transcribe/audio", response_model=TranscriptionResponse)
async def transcribe_audio(audio_file: UploadFile = File(...)):
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
        input_features = stt_processor(
            audio_data, sampling_rate=16000, return_tensors="pt"
        ).input_features.to(device)
        predicted_ids = stt_model.generate(input_features, max_length=448)
        transcription = stt_processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )
        return JSONResponse(content={"transcription": transcription[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


class TTSRequest(BaseModel):
    text: str


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
    """
    text = (request.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        # 1. Normalize text (fixes pronunciation & skipping)
        clean_text = normalize_medical_text(text)

        # 2. Safe length cap (avoid cutting mid-word)
        max_chars = 2000
        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars].rsplit(" ", 1)[0] + "..."

        # 3. Setup Edge TTS
        communicate = edge_tts.Communicate(
            text=clean_text,
            voice=TTS_VOICE,
        )

        # 4. Stream generator
        async def audio_stream():
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]

        # 5. Return Stream (MP3 format)
        return StreamingResponse(audio_stream(), media_type="audio/mpeg")

    except Exception as e:
        print(f"TTS Generation Error: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Voice generation failed: {str(e)}"
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
                conf_str = conf_part.replace("%", "").replace(")", "").strip()
                confidence = float(conf_str)
            elif "%" in context_str:
                match = re.search(r"(\d+\.?\d*)%", context_str)
                if match:
                    confidence = float(match.group(1))

            # Get grounded medical context
            condition_info = get_condition_info(diagnosis_label)
            medical_context = format_context_for_prompt(
                condition_info, diagnosis_label, confidence
            )

            print(
                f"📋 Context parsed - Diagnosis: {diagnosis_label}, Confidence: {confidence}%"
            )

        except Exception as e:
            print(f"⚠️ Context parsing warning: {e}")
            medical_context = f"\nDiagnosis context provided: {request.context}\n"

    # Build system prompt with grounding
    system_prompt = f"""You are VoxRay, an AI radiology assistant designed to help healthcare professionals understand imaging findings.

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


app.mount(
    "/",
    StaticFiles(directory=str(BASE_DIR / "frontend" / "dist"), html=True),
    name="static",
)

if __name__ == "__main__":
    print("uvicorn backend.api.main:app --reload")
