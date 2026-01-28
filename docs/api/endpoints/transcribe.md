# Transcription API

## Transcribe Audio

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
