import pytest
import httpx

BASE_URL = "http://localhost:8000"

def test_predict_image_pneumonia_example():
    # Adjust a real image path as needed
    image_path = "consolidated_medical_data/test/03_PNEUMONIA/3 - Copy.png"
    with open(image_path, "rb") as f:
        files = {"image_file": ("sample.png", f, "image/png")}
        resp = httpx.post(f"{BASE_URL}/predict/image", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "diagnosis" in data and "confidence" in data

def test_transcribe_audio_dummy():
    # Provide a 16kHz wav file for realistic test
    audio_path = "logs/sample16k.wav"
    with open(audio_path, "rb") as f:
        files = {"audio_file": ("sample.wav", f, "audio/wav")}
        resp = httpx.post(f"{BASE_URL}/transcribe/audio", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "transcription" in data

def test_generate_speech_simple():
    payload = {"text": "Fracture detected"}
    resp = httpx.post(f"{BASE_URL}/generate/speech", json=payload)
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "audio/wav"