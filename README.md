# VoxRay AI

An advanced AI-powered medical console that combines **Vox** (Voice) and **Ray** (X-Ray) technologies to assist medical professionals.

![Project Banner](https://via.placeholder.com/1200x400?text=VoxRay+AI)

## 🚀 Features

- **VoxRay Vision (F1):** Instantly diagnoses 6 types of conditions from X-Ray images (Normal, Pneumonia, Lung Cancer, Fractures, etc.) using a ResNet-based model.
- **VoxRay Voice (F2):** Hands-free interaction using OpenAI Whisper (STT) and Facebook MMS-TTS for natural voice responses.
- **VoxRay Intelligence:** Integrated with Google Gemini 2.0 Flash to explain diagnoses and answer medical questions in context.
- **MLOps Pipeline:** Full TFX (TensorFlow Extended) pipeline for reproducible data processing and model training.
- **Modern UI:** A premium, responsive React frontend with real-time audio visualization.

---

## 🛠️ Tech Stack

- **Frontend:** React, Vite, TailwindCSS, Framer Motion
- **Backend:** FastAPI, Uvicorn, Python 3.12
- **AI/ML:** TensorFlow, PyTorch, Transformers (Hugging Face), TFX
- **Models:** ResNet50V2 (Custom trained), Whisper Base (STT), MMS-TTS (TTS), Gemini 2.0 Flash (LLM)

---

## 📦 Installation & Setup

### Prerequisites

- Node.js & npm
- Python 3.10+ (Python 3.12 recommended for Backend)
- WSL2 (Ubuntu) for TFX Pipeline (Optional, for training only)

### 1. Backend Setup

The backend serves the AI models and API.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file and add your OpenRouter API key:
# OPENROUTER_API_KEY=your_key_here
```

### 2. Frontend Setup

The frontend is the user interface.

```bash
cd voxray-ai

# Install dependencies
npm install

# Build the project (optional, for production)
npm run build
```

---

## 🏃‍♂️ Running the Application

### Start the Backend

Open a terminal in the project root:

```bash
# Make sure venv is active
uvicorn api.main:app --reload
```

_Server will start at `http://127.0.0.1:8000`_

### Start the Frontend

Open a new terminal in `voxray-ai`:

```bash
npm run dev
```

_App will be available at `http://localhost:5173`_

---

## 🏭 MLOps: TFX Pipeline (Training)

This project includes a production-grade **TFX Pipeline** for training the medical model. Due to library compatibility, **this must be run in a WSL2 (Ubuntu) environment**.

### 1. WSL Setup (One-time)

Ensure you have copied the project to your WSL environment:

```bash
# In Ubuntu Terminal
mkdir -p ~/projects/medical\ console
cp -r "/mnt/c/Users/witty/OneDrive/Desktop/Projects/medical console/"* ~/projects/medical\ console/
```

### 2. Environment Setup

Create a separate Python environment for TFX (Python 3.9 is recommended for compatibility):

```bash
# In WSL
sudo apt-get install python3.9-venv
python3.9 -m venv tfx_env
source tfx_env/bin/activate

# Install TFX dependencies
pip install -r tfx_requirements.txt
```

### 3. Data Preparation

The pipeline requires raw images in `consolidated_medical_data/train`.

**Step A: Convert to TFRecord**
Run this inside WSL to prepare the data:

```bash
# Ensure tfx_env is active
python tfx_pipeline/convert_to_tfrecords.py
```

_Output: `tfx_data/train/data.tfrecord`_

### 4. Run the Pipeline

Execute the full training pipeline:

```bash
# Important: Sync latest code changes from Windows if needed
# cp -r "/mnt/c/Users/witty/OneDrive/Desktop/Projects/medical console/tfx_pipeline/"* ~/projects/medical\ console/tfx_pipeline/

python tfx_pipeline/run_pipeline.py
```

### 📍 Model Artifacts

After a successful run, TFX saves the trained models in:

- **Serving Model (Production):** `tfx_pipeline/serving_model/`
  - Contains numbered folders (e.g., `1712345678/`) with the `saved_model.pb`. This is the model you should use for inference.
- **Training Checkpoints:** `tfx_pipeline/pipeline_root/Trainer/model/`

---

## 🧠 Model Training (Manual / No TFX)

If you prefer to train the model without TFX (e.g., for quick experiments on Windows), you can use the standalone script:

```bash
python tfx_pipeline/verify_training_standalone.py
```

This script mocks the TFX environment and runs the training logic directly using the generated TFRecords.

---

## 🤝 Contribute & Support

We welcome contributions! If you'd like to improve this project:

1.  Fork the repository.
2.  Create a feature branch.
3.  Submit a Pull Request.

---

_Built with ❤️ for the Future of Healthcare._
