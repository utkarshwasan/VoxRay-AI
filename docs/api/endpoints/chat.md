# Chat API

## Medical Consultant Chat (V1)

Provides an intelligent conversational interface for second opinions.

```http
POST /chat
```

### Request Body (JSON)

```json
{
  "message": "What are the common treatments for this condition?",
  "context": "Diagnosis: PNEUMONIA, Confidence: 98.7%",
  "history": [
    { "role": "user", "text": "Is this pneumonia?" },
    { "role": "assistant", "text": "Yes, the scan suggests pneumonia." }
  ]
}
```

### Response

```json
{
  "response": "Common treatments for pneumonia include antibiotics, rest, and fluids..."
}
```

---

## Multilingual Chat (V2)

Enhanced chat with multilingual support and language enforcement.

```http
POST /v2/chat
```

### Request Body (JSON)

```json
{
  "message": "What are the common treatments for this condition?",
  "context": "Diagnosis: PNEUMONIA, Confidence: 98.7%",
  "history": [
    { "role": "user", "text": "Is this pneumonia?" },
    { "role": "assistant", "text": "Yes, the scan suggests pneumonia." }
  ],
  "language": "es"
}
```

### Supported Languages

| Code | Language |
| ---- | -------- |
| `en` | English  |
| `es` | Spanish  |
| `fr` | French   |
| `de` | German   |
| `zh` | Chinese  |

### Response

```json
{
  "response": "Los tratamientos comunes para la neumonía incluyen antibióticos, reposo y líquidos..."
}
```

**Note:** Hindi (`hi`) is disabled due to STT limitations with whisper-base.
