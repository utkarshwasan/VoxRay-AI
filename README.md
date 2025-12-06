# VoxRay AI

**An advanced multimodal medical console combining Computer Vision and Conversational AI to streamline clinical workflows.**

## 🏥 Project Overview

In high-pressure medical environments, clinicians face two critical challenges: **diagnostic fatigue** from analyzing thousands of images and the need to maintain **sterile conditions**, which makes manual data entry cumbersome.

**VoxRay AI** solves this by acting as a hands-free, intelligent assistant. It synergizes visual analysis with a voice-first interface, allowing doctors to interact with X-ray data, receive audio briefings, and access AI-driven second opinions without breaking focus. Built on a scalable **TFX (TensorFlow Extended)** pipeline, VoxRay AI offers a production-grade architecture for automated, explainable, and accessible medical diagnostics.

## 🚀 Key Features

- **👁️ VoxRay Vision (Computer Vision):**

  - **Instant Pathology Detection:** Uses a custom-trained **ResNet50V2** model to classify 6+ chest and bone abnormalities (Pneumonia, Lung Cancer, Fractures, etc.) with real-time confidence scoring.
  - **Visual Explainability:** Provides clear diagnostic confidence metrics to support clinical decision-making.

- **🎙️ VoxRay Voice (Hands-Free Interface):**

  - **Sterile Workflow Support:** Eliminates the need for keyboards using **OpenAI Whisper** (STT) for accurate medical dictation and **Facebook MMS-TTS** for natural voice responses.
  - **Audio Briefings:** allowing doctors to "hear" the diagnosis while scrubbing in or examining patients.

- **🧠 VoxRay Intelligence (Contextual AI):**

  - **Intelligent Second Opinions:** Integrated with **Google Gemini 2.0 Flash** to explain diagnoses in natural language and answer complex medical follow-up questions.
  - **Context-Aware:** The LLM understands the specific context of the current X-ray analysis, reducing hallucination and increasing relevance.

- **🏭 Production MLOps Pipeline:**

  - **End-to-End Automation:** A full **TFX (TensorFlow Extended)** pipeline manages data ingestion, validation, transformation, and model training, ensuring reproducibility and scalability.

- **✨ Modern Clinical UI:**
  - A premium, responsive interface built with **React, Vite, and TailwindCSS**, featuring real-time audio visualization and interactive image handling.

---

## 🛠️ Tech Stack

- **Frontend:** React, Vite, TailwindCSS, Framer Motion
- **Backend:** FastAPI, Uvicorn, Python 3.12 (API) / Python 3.9 (TFX Pipeline)
- **AI/ML:** TensorFlow, PyTorch, Transformers (Hugging Face), TFX
- **Models:** ResNet50V2 (Custom trained), Whisper Base (STT), MMS-TTS (TTS), Gemini 2.0 Flash (LLM)

---

## 📦 Installation & Setup

### Prerequisites

- Node.js & npm
- Python 3.12 (for Backend) & Python 3.9 (for TFX in WSL)
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
mkdir -p ~/projects/voxray-ai
# Replace /path/to/voxray-ai with your actual project location
cp -r /path/to/voxray-ai/* ~/projects/voxray-ai/
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
# cp -r /path/to/voxray-ai/tfx_pipeline/* ~/projects/voxray-ai/tfx_pipeline/

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
