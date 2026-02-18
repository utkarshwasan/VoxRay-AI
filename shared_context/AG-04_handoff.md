# AG-04 Voice Specialist Handoff

## Status

**Completed** (Phase 3 Voice Enhancements)

## Feature Implementation

1. **Core Modules** (`backend/voice/`):
   - `medical_vocabulary.py`: Implemented medical term correction (e.g., "ammonia" -> "pneumonia").
   - `multilingual.py`: Added language config (English/Spanish).
   - `noise_handler.py`: Added noise estimation and adaptive thresholds.
   - `wake_word.py`: Implemented stub for wake word detection (safe fallback).

2. **API Integration** (`backend/api/routes/v2_voice.py`):
   - Created dedicated router for voice endpoints (clean separation).
   - Added `/v2/voice/enhance-transcription` (Guarded by `FF_MEDICAL_VOCABULARY`).
   - Added `/v2/voice/wake-word-detect` (Guarded by `FF_WAKE_WORD_DETECTION`).
   - Wired into `backend/api/v2.py` via `include_router`.

3. **Dependencies**:
   - Updated `backend/requirements.txt`.
   - Installed `fastapi`, `uvicorn`, `librosa`, etc.
   - Note: `backend/serving/model_server.py` relies on AG-01 modules being present.

## Verification

- **Unit Tests**: `tests/voice/test_medical_vocabulary.py` (Passes).
- **Integration Tests**: `tests/voice/test_api_flags.py` (Passes with `load_models` mocked).
- **Regression**: `tests/migration/test_backward_compatibility.py` (Passes).

## Known Issues / Notes

- **Startup Time**: Tests involving `app` startup trigger heavy model download. Recommended to use a fixture to mock `load_models` in `conftest.py` (Action for AG-08).
- **Architecture**: Compliant with v2 router pattern (voice routes isolated).

## Next Steps

- AG-03 (Clinical) should verify clinical routes integration in `v2.py`.
- AG-08 (QA) should centralize startup mocking.
