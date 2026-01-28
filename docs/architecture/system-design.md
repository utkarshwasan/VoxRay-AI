# System Design

## Data Flow

### 1. Image Analysis Flow

1. **User** uploads X-Ray via Frontend.
2. Image is sent to `POST /predict/image` as multipart/form-data.
3. **Backend** preprocesses image (resize to 224x224, normalize).
4. **ResNet50V2 Model** predicts class probabilities (Pneumonia, etc.).
5. **Grad-CAM module** uses gradients to generate heatmaps.
6. JSON response (Diagnosis + Confidence) returned to Frontend.

### 2. Voice Command Flow

1. **User** presses "Hold to Speak".
2. Audio recorded in browser (Web Audio API).
3. Audio blob sent to `POST /transcribe/audio`.
4. **Whisper Model** converts Audio -> Text.
5. Frontend interprets text (e.g., "Analyze", "Explain").

### 3. Conversational AI Flow

1. **User** asks "What does this mean?".
2. Frontend sends message + _Diagnosis Context_ to `POST /chat`.
3. **Backend** constructs prompt with System Instructions + Medical Guidelines.
4. Request forwarded to **OpenRouter (Gemini 2.0)**.
5. Response returned and read aloud via `POST /generate/speech`.

## Database Schema

Currently, VoxRay AI is stateless for simplicity.

- **Micro-DB**: Use `consolidated_medical_data` for training files.
- **User Data**: Managed externally by Stack Auth.

## Security Design

- **Headers**: All protected endpoints require `x-stack-access-token`.
- **Validation**: Backend uses JWKS (JSON Web Key Sets) to verify signatures from Stack Auth.
- **CORS**: Restricted to allowed origins (localhost).
