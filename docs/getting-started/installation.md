# Installation Guide

This guide covers the complete installation process for VoxRay AI, including optional TFX pipeline setup.

## System Requirements

- **OS**: Windows (tested), macOS, or Linux.
- **RAM**: 8GB minimum (16GB recommended for ML training).
- **GPU**: Optional but recommended for inference/training (NVIDIA CUDA).

## 1. Backend Installation

VoxRay's backend is built with FastAPI and handles all AI processing.

### Python Environment

We recommend Python 3.12 for performance, though 3.10+ is supported.

```bash
# Project root
python -m venv venv
.\venv\Scripts\activate
```

### Dependencies

The backend requires several ML libraries (Torch, TensorFlow, Transformers).

```bash
pip install -r backend/requirements.txt
```

### Environment Variables

The backend relies on `backend/.env`.

| Variable                  | Description                                       | Required |
| ------------------------- | ------------------------------------------------- | -------- |
| `OPENROUTER_API_KEY`      | Key for accessing Gemini 2.0 via OpenRouter       | Yes      |
| `STACK_PROJECT_ID`        | Project ID from Stack Auth console                | Yes      |
| `STACK_SECRET_SERVER_KEY` | Secret key for backend auth verification          | Yes      |
| `TTS_VOICE`               | Edge-TTS voice (default: en-US-ChristopherNeural) | No       |

## 2. Frontend Installation

The frontend is a Vite + React application.

### Node.js Setup

Install dependencies using npm.

```bash
cd frontend
npm install
```

### Environment Variables

The frontend relies on `frontend/.env`.

| Variable                            | Description                               | Required |
| ----------------------------------- | ----------------------------------------- | -------- |
| `VITE_STACK_PUBLISHABLE_CLIENT_KEY` | Public key for Stack Auth login component | Yes      |
| `VITE_STACK_PROJECT_ID`             | Project ID matching backend               | Yes      |

## 3. TFX Pipeline Setup (Optional)

The TensorFlow Extended (TFX) pipeline is used for retraining the medical model.
**Note:** TFX is highly sensitive to platform. We recommend **WSL2 (Ubuntu)** on Windows.

### WSL2 Setup

1. Open Ubuntu terminal.
2. Clone repo inside WSL.
3. Create a separate venv (Python 3.9 recommended for TFX compatibility).

```bash
python3.9 -m venv tfx_env
source tfx_env/bin/activate
pip install -r pipeline/requirements.txt
```

### Running the Pipeline

```bash
# Convert raw images to TFRecords
python pipeline/tfx/convert_to_tfrecords.py

# Run the full pipeline
python pipeline/tfx/run_pipeline.py
```

## Troubleshooting

### "Module not found"

Ensure your `venv` is active. In VS Code, select the correct Python interpreter (`./venv/Scripts/python.exe`).

### "Auth Failed"

Check that `STACK_PROJECT_ID` is identical in both `frontend/.env` and `backend/.env`.
