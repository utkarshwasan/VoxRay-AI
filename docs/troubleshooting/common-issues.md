# Common Issues & Solutions

## Installation Issues

### `pip install` fails on Windows

**Error:** `Microsoft Visual C++ 14.0 is required.`
**Solution:** Install "Desktop development with C++" workload via Visual Studio Build Tools.

### TFX "Platform not supported"

**Issue:** TensorFlow Extended (TFX) often has issues on pure Windows.
**Solution:** Use WSL2 (Ubuntu) for the pipeline folder functionality. The backend API works fine on native Windows.

## Runtime Issues

### "Model not loaded" (503 Error)

**Symptom:** API returns 503 when calling `/predict`.
**Cause:** The file `backend/models/serving/medical_model_final.keras` is missing.
**Solution:**

1. You must run the TFX pipeline to generate the model.
2. OR: Ask the team for the pre-trained `.keras` file and place it in `backend/models/`.

### "Auth Error: Missing Project ID"

**Cause:** `STACK_PROJECT_ID` is missing in `.env`.
**Solution:** Ensure your `.env` file has the correct Stack Auth keys.
