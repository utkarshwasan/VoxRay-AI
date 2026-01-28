# Chat API

## Medical Consultant Chat

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
