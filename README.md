# VoxRay AI

**An advanced multimodal medical console combining Computer Vision and Conversational AI to streamline clinical workflows.**

## 🏥 Project Overview

In high-pressure medical environments, clinicians face two critical challenges: **diagnostic fatigue** from analyzing thousands of images and the need to maintain **sterile conditions**, which makes manual data entry cumbersome.

**VoxRay AI** solves this by acting as a hands-free, intelligent assistant. It synergizes visual analysis with a voice-first interface, allowing doctors to interact with X-ray data, receive audio briefings, and access AI-driven second opinions without breaking focus. Built on a scalable **TFX (TensorFlow Extended)** pipeline, VoxRay AI offers a production-grade architecture for automated, explainable, and accessible medical diagnostics.
<<<<<<< HEAD

## 🚀 Key Features

- ** Secure Authentication:**
  - **Role-Based Access:** Integrated **Stack Auth** for secure user management, protecting patient data and API endpoints.
  - **Seamless Login:** Auto-redirect flows and secure session management via JWT.

- **👁️ VoxRay Vision (Computer Vision):**
  - **Instant Pathology Detection:** Uses a custom-trained **ResNet50V2** model to classify 6+ chest and bone abnormalities (Pneumonia, Lung Cancer, Fractures, etc.) with real-time confidence scoring.
  - **Visual Explainability:** Provides **Grad-CAM heatmaps** to visualize exactly where the model is looking.
  - **DICOM-Style Viewer:** Interactive Window/Level (Brightness/Contrast) controls for professional grade analysis.

- **🎙️ VoxRay Voice (Hands-Free Interface):**
  - **Sterile Workflow Support:** Eliminates the need for keyboards using **OpenAI Whisper** (STT) for accurate medical dictation and **Facebook MMS-TTS** for natural voice responses.
  - **Audio Briefings:** allowing doctors to "hear" the diagnosis while scrubbing in or examining patients.

- **🧠 VoxRay Intelligence (Contextual AI):**
  - **Intelligent Second Opinions:** Integrated with **Google Gemini 2.0 Flash** to explain diagnoses in natural language and answer complex medical follow-up questions.
  - **Context-Aware:** The LLM understands the specific context of the current X-ray analysis, reducing hallucination and increasing relevance.

- **🏭 Production MLOps Pipeline:**
  - **End-to-End Automation:** A full **TFX** pipeline manages data ingestion, validation, and model training.

## 🛠️ Tech Stack

- **Frontend:** React 18, Vite, TailwindCSS, Framer Motion, Stack Auth (Frontend SDK)
- **Backend:** FastAPI, Uvicorn, Python 3.12, Stack Auth (Backend SDK/PyJWT)
- **AI/ML:** TensorFlow/Keras (ResNet50V2), TFX, PyTorch (Whisper), MMS-TTS, Gemini 2.0

---

## 📦 Installation & Setup

### Prerequisites

- Node.js & npm
- Python 3.10+ (Python 3.12 recommended for Backend)
- **Stack Auth Account:** Create a project at [stack-auth.com](https://stack-auth.com/) and get your keys.

### 1. Backend Setup

The backend serves the AI models and API.

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate
# (Linux/Mac: source venv/bin/activate)

# Install dependencies
pip install -r backend/requirements.txt
```

**Configuration (`backend/.env`):**
Create a `backend/.env` file with your secret keys:

```env
OPENROUTER_API_KEY=your_openrouter_key
STACK_PROJECT_ID=your_stack_project_id
STACK_SECRET_SERVER_KEY=your_stack_secret_key
```

### 2. Frontend Setup

The frontend is the user interface.

```bash
cd frontend

# Install dependencies
npm install
```

**Configuration (`frontend/.env`):**
Create a `frontend/.env` file with your public keys:

```env
VITE_STACK_PUBLISHABLE_CLIENT_KEY=your_stack_publishable_key
VITE_STACK_PROJECT_ID=your_stack_project_id
```

---

## 🏃‍♂️ Running the Application

### Start the Backend

Open a terminal in the project root:

```bash
# Make sure venv is active
uvicorn backend.api.main:app --reload
```

_Server will start at `http://127.0.0.1:8000`_

### Start the Frontend

Open a new terminal in `frontend`:

```bash
npm run dev
```

_App will be available at `http://localhost:5173`_

---

## 🏭 MLOps: TFX Pipeline (Training)

This project includes a production-grade **TFX Pipeline** for training the medical model. Due to library compatibility, **this must be run in a WSL2 (Ubuntu) environment**.

### 1. WSL Setup & Execution

```bash
# In Ubuntu Terminal (WSL)
python3.9 -m venv tfx_env
source tfx_env/bin/activate
pip install -r pipeline/requirements.txt

# Convert Data
python pipeline/tfx/convert_to_tfrecords.py

# Run Pipeline
python pipeline/tfx/run_pipeline.py
```

After a successful run, the trained model is saved to `backend/models/serving/`.

---

## 🤝 Contribute & Support

1.  Fork the repository.
2.  Create a feature branch.
3.  Submit a Pull Request.

---

_Built with ❤️ for the Future of Healthcare._
