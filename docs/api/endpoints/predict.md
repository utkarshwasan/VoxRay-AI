# Prediction API

## Predict Image (V1)

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

---

## Ensemble Prediction (V2)

Multi-model prediction with uncertainty quantification.

```http
POST /v2/predict/image
```

**Requires:** `FF_ENSEMBLE_MODEL=true`

### Response

```json
{
  "diagnosis": "06_PNEUMONIA",
  "confidence": 0.985,
  "uncertainty": 0.023,
  "model_votes": {
    "resnet50": "PNEUMONIA",
    "efficientnet": "PNEUMONIA",
    "densenet": "PNEUMONIA"
  }
}
```

---

## DICOM Prediction (V2)

Predict from DICOM files with optional anonymization.

```http
POST /v2/predict/dicom
```

**Requires:** `FF_DICOM_SUPPORT=true`

### Request Body (Multipart)

| Field        | Type | Description       |
| ------------ | ---- | ----------------- |
| `dicom_file` | File | DICOM file (.dcm) |

### Response

```json
{
  "diagnosis": "06_PNEUMONIA",
  "confidence": 0.985,
  "anonymized": true
}
```
