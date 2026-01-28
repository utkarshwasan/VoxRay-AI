# Quick Start Guide

Get up and running with VoxRay AI in under 10 minutes.

## Prerequisites

Before you begin, ensure you have:

- [ ] Node.js 18+ ([Download](https://nodejs.org))
- [ ] Python 3.10+ ([Download](https://python.org))
- [ ] Git
- [ ] A [Stack Auth](https://stack-auth.com/) account (Project ID & Keys)
- [ ] An [OpenRouter](https://openrouter.ai/) API Key

## Step 1: Clone the Repository

```bash
git clone https://github.com/utkarshwasan/VoxRay-AI.git
cd VoxRay-AI
```

## Step 2: Backend Setup

The backend serves the AI models (Vision, TTS, STT) and specific API endpoints.

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (Mac/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Configure Backend

Create a `backend/.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_key_here
STACK_PROJECT_ID=your_stack_project_id
STACK_SECRET_SERVER_KEY=your_stack_secret_key
# Optional: Text-to-Speech Voice
TTS_VOICE=en-US-ChristopherNeural
```

## Step 3: Frontend Setup

The frontend is a React application providing the medical console interface.

```bash
cd frontend
npm install
```

### Configure Frontend

Create a `frontend/.env` file:

```env
VITE_STACK_PUBLISHABLE_CLIENT_KEY=your_stack_publishable_key
VITE_STACK_PROJECT_ID=your_stack_project_id
```

## Step 4: Start the System

You need to run two terminals.

**Terminal 1 (Backend):**

```bash
# Ensure venv is active and you are in the root directory
uvicorn backend.api.main:app --reload
```

You should see: `Uvicorn running on http://127.0.0.1:8000`

**Terminal 2 (Frontend):**

```bash
cd frontend
npm run dev
```

You should see: `Local: http://localhost:5173`

## Step 5: Verify Setup

1. Open http://localhost:5173 in your browser.
2. Sign up/Login using the Stack Auth interface.
3. Once logged in, upload a chest X-ray image (sample images in `consolidated_medical_data/test/`).
4. Click "Analyze" to test the Computer Vision model.
5. Click the "Explain" button to test Grad-CAM.

## 🎉 Success!

You have a running instance of VoxRay AI.

## Next Steps

- 📖 [Detailed Installation Guide](./installation.md)
- 🏗️ [Understand the Architecture](../architecture/README.md)
- 📚 [Explore the API](../api/README.md)
