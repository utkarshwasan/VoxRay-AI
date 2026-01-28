# Prediction API

## Predict Image

Analyzes a medical image for pathologies.

```http
POST /predict/image
```

### Headers

| Header                 | Value | Description       |
| ---------------------- | ----- | ----------------- |
| `x-stack-access-token` | JWT   | Required for auth |

### Request Body (Multipart)

| Field        | Type | Description               |
| ------------ | ---- | ------------------------- |
| `image_file` | File | The X-ray image (PNG/JPG) |

### Response

```json
{
  "diagnosis": "06_PNEUMONIA",
  "confidence": 0.985
}
```

---

## Explain Prediction (Grad-CAM)

Generates a heatmap overlay explaining _why_ the model made its decision.

```http
POST /predict/explain
```

### Response

```json
{
  "heatmap_b64": "data:image/png;base64,iVBORw0KGgo..."
}
```
