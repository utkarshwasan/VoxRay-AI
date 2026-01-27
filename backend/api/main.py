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
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq, VitsModel, AutoTokenizer
from datasets import load_dataset
from tensorflow.keras.applications.resnet_v2 import preprocess_input

medical_model = None
IMG_HEIGHT = 224
IMG_WIDTH = 224

stt_processor = None
stt_model = None

tts_processor = None
tts_model = None
# tts_vocoder and speaker_embeddings are not needed for MMS

device = "cuda:0" if torch.cuda.is_available() else "cpu"

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
        if TRAIN_DIR.exists():
            MEDICAL_CLASS_NAMES = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir()])
            print(f"✅ Loaded {len(MEDICAL_CLASS_NAMES)} classes from {TRAIN_DIR}")
        else:
            # Fallback: Based on typical medical datasets, likely has 6 classes
            MEDICAL_CLASS_NAMES = [
                "01_NORMAL_LUNG",
                "02_NORMAL_BONE",
                "03_NORMAL_PNEUMONIA",
                "04_LUNG_CANCER",
                "05_FRACTURED",
                "06_PNEUMONIA"
            ]
            print(f"⚠️ Training directory not found. Using fallback with {len(MEDICAL_CLASS_NAMES)} classes")
    except Exception as e:
        print(f"❌ Error loading class names: {e}")
        MEDICAL_CLASS_NAMES = [
            "01_NORMAL_LUNG",
            "02_NORMAL_BONE",
            "03_NORMAL_PNEUMONIA",
            "04_LUNG_CANCER",
            "05_FRACTURED",
            "06_PNEUMONIA"
        ]

app = FastAPI(
    title="Intelligent Medical Diagnosis Assistant API",
    description="Serves F1 (Image) and F2 (Voice) models via REST API."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175", 
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_models():
    global medical_model, stt_processor, stt_model
    global tts_processor, tts_model
    
    # Load class names first
    load_class_names()
    
    # Model path using pathlib (models moved to backend/models)
    model_path = BASE_DIR / "backend" / "models" / "medical_model_final.keras"
    try:
        medical_model = tf.keras.models.load_model(str(model_path))
        print(f"✅ Model loaded from {model_path}. Expected {len(MEDICAL_CLASS_NAMES)} classes")
    except Exception as e:
        print(f"WARNING: Could not load F1 model from {model_path}. /predict/image will fail. Error: {e}")
    
    print("⏳ Loading STT Model (Whisper)...")
    stt_processor = AutoProcessor.from_pretrained("openai/whisper-base")
    stt_model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-base").to(device)
    
    print("⏳ Loading TTS Model (MMS-TTS)...")
    tts_processor = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")
    tts_model = VitsModel.from_pretrained("facebook/mms-tts-eng").to(device)
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
async def predict_image(image_file: UploadFile = File(...), user: dict = Depends(get_current_user)):
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
            print(f"  {idx}: {class_name}: {float(prob)*100:.2f}%")
        
        diagnosis = MEDICAL_CLASS_NAMES[np.argmax(score)]
        confidence = float(np.max(score))
        print(f"✅ Top prediction: {diagnosis} ({confidence*100:.1f}%)\n")
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
        last_conv_layer = base_model.get_layer('conv5_block3_out')
        
        # Create a model for the base that returns both conv output and final base output
        # mapping: input -> [conv_out, base_out]
        base_multi_model = tf.keras.models.Model(
            inputs=base_model.inputs,
            outputs=[last_conv_layer.output, base_model.output]
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
        grad_model = tf.keras.models.Model(inputs=inputs, outputs=[conv_out, predictions])

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


def create_heatmap_overlay(heatmap, original_img_bytes):
    """
    Create a colored heatmap overlay image.
    Returns base64 encoded PNG.
    """
    # Load original image
    img = Image.open(io.BytesIO(original_img_bytes)).convert("RGB")
    img = img.resize((IMG_WIDTH, IMG_HEIGHT))
    img_array = np.array(img)
    
    # Resize heatmap to match image size
    heatmap_resized = cv2.resize(heatmap, (IMG_WIDTH, IMG_HEIGHT))
    
    # Convert to colormap (use JET for medical imaging - red = high attention)
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    # Blend with original image
    superimposed = cv2.addWeighted(img_array, 0.6, heatmap_colored, 0.4, 0)
    
    # Convert to base64
    pil_img = Image.fromarray(superimposed)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


class ExplainResponse(BaseModel):
    heatmap_b64: str


@app.post("/predict/explain", response_model=ExplainResponse)
async def explain_prediction(image_file: UploadFile = File(...), user: dict = Depends(get_current_user)):
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
            raise HTTPException(status_code=500, detail="Failed to generate Grad-CAM heatmap")
        
        # Create overlay image
        heatmap_b64 = create_heatmap_overlay(heatmap, file_bytes)
        
        print("✅ Grad-CAM explanation generated successfully!")
        return JSONResponse(content={"heatmap_b64": heatmap_b64})
        
    except Exception as e:
        print(f"❌ Explanation error: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")


class TranscriptionResponse(BaseModel):
    transcription: str

@app.post("/transcribe/audio", response_model=TranscriptionResponse)
async def transcribe_audio(audio_file: UploadFile = File(...)):
    if not stt_model or not stt_processor:
        raise HTTPException(status_code=503, detail="F2 (STT) models are not loaded.")
    try:
        audio_data, original_samplerate = sf.read(io.BytesIO(await audio_file.read()))
        if original_samplerate != 16000:
            audio_data = librosa.resample(y=audio_data, orig_sr=original_samplerate, target_sr=16000)
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        input_features = stt_processor(audio_data, sampling_rate=16000, return_tensors="pt").input_features.to(device)
        predicted_ids = stt_model.generate(input_features, max_length=448)
        transcription = stt_processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return JSONResponse(content={"transcription": transcription[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

class TTSRequest(BaseModel):
    text: str

@app.post("/generate/speech")
async def generate_speech(request: TTSRequest = Body(...)):
    if not tts_model or not tts_processor:
        raise HTTPException(status_code=503, detail="F2 (TTS) models are not loaded.")
    try:
        # Truncate text to avoid model limit
        max_chars = 500
        text_to_speak = request.text[:max_chars]
        if len(request.text) > max_chars:
            print(f"⚠️ Text truncated for TTS: {len(request.text)} -> {max_chars} chars")
            
        inputs = tts_processor(text=text_to_speak, return_tensors="pt").to(device)
        
        with torch.no_grad():
            output = tts_model(**inputs)
        
        waveform = output.waveform[0].cpu().numpy()
        
        buffer = io.BytesIO()
        sf.write(buffer, waveform, samplerate=16000, format='WAV')
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")

# --- Conversational AI (OpenRouter) ---
from openai import OpenAI
from dotenv import load_dotenv
import os

# Explicitly load from backend/.env
env_path = BASE_DIR / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

class ChatRequest(BaseModel):
    message: str
    context: str = None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest = Body(...), user: dict = Depends(get_current_user)):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenRouter API Key not found. Please set OPENROUTER_API_KEY in .env")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    system_prompt = "You are a helpful, professional medical assistant. Answer the user's questions clearly and concisely. Keep your responses short (under 50 words) suitable for voice readout."
    if request.context:
        system_prompt += f"\n\nContext from X-Ray Analysis: {request.context}\nUse this context to answer if relevant."

    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message},
            ],
        )
        return JSONResponse(content={"response": completion.choices[0].message.content})
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

app.mount("/", StaticFiles(directory=str(BASE_DIR / "frontend" / "dist"), html=True), name="static")

if __name__ == "__main__":
    print("uvicorn backend.api.main:app --reload")