# Transcription API

## Transcribe Audio (V1)

Converts spoken medical dictation into text using OpenAI Whisper.

```http
POST /transcribe/audio
```

### Request Body (Multipart)

| Field        | Type | Description         |
| ------------ | ---- | ------------------- |
| `audio_file` | File | WAV/WebM audio blob |

### Response

```json
{
  "transcription": "Patient shows signs of consolidation in the lower right lobe."
}
```

---

## Generate Speech (TTS)

Converts text responses back into lifelike audio.

```http
POST /generate/speech
```

### Request Body (JSON)

```json
{
  "text": "The analysis suggests pneumonia with 98% confidence."
}
```

### Response

- **Content-Type**: `audio/mpeg`
- **Body**: Binary audio stream.

---

## Medical Vocabulary Enhancement (V2)

Corrects medical terminology in transcribed text.

```http
POST /v2/voice/enhance-transcription
```

**Requires:** `FF_MEDICAL_VOCABULARY=true`

### Request Body (JSON)

```json
{
  "text": "Patient has ammonia in the lower lobe"
}
```

### Response

```json
{
  "original": "Patient has ammonia in the lower lobe",
  "corrected": "Patient has pneumonia in the lower lobe",
  "corrections": [
    {
      "original": "ammonia",
      "corrected": "pneumonia"
    }
  ]
}
```

---

## Wake Word Detection (V2)

Detects wake words in audio for hands-free activation.

```http
POST /v2/voice/wake-word-detect
```

**Requires:** `FF_WAKE_WORD_DETECTION=true`

### Request Body (Multipart)

| Field        | Type | Description         |
| ------------ | ---- | ------------------- |
| `audio_file` | File | WAV/WebM audio blob |

### Response

```json
{
  "detected": true,
  "wake_word": "hey voxray"
}
```
