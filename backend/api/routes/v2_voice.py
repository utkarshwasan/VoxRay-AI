from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.core.feature_flags import require_feature, FeatureFlag
from pydantic import BaseModel
from backend.voice.medical_vocabulary import MedicalVocabulary
from backend.voice.wake_word import WakeWordDetector

router = APIRouter()


class EnhancementRequest(BaseModel):
    text: str


@router.post("/voice/enhance-transcription")
@require_feature(FeatureFlag.MEDICAL_VOCABULARY)
async def enhance_transcription(request: EnhancementRequest):
    """
    Corrects medical terms in transcribed text.
    Example: 'patient has ammonia' -> 'patient has pneumonia'
    """
    vocab = MedicalVocabulary()
    # In a real scenario, we might inject this dependency or cache it
    enhanced_text = vocab.post_process(request.text)
    return {"original": request.text, "enhanced": enhanced_text}


@router.post("/voice/wake-word-detect")
@require_feature(FeatureFlag.WAKE_WORD_DETECTION)
async def wake_word_detect(file: UploadFile = File(...)):
    """
    Detects wake word in an audio file.
    Gated by feature flag. Currently a stub.
    """
    detector = WakeWordDetector()
    # Read first chunk of bytes just to simulate processing
    audio_bytes = await file.read(1024)
    result = detector.detect(audio_bytes)
    return result
