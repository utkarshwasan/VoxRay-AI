# VoxRay AI

**An advanced multimodal medical console combining Computer Vision and Conversational AI to streamline clinical workflows.**

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](./CHANGELOG_V1_TO_V2.md)
[![Documentation](https://img.shields.io/badge/docs-view-blue)](./docs/README.md)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

---

## 🏥 Project Overview

In high-pressure medical environments, clinicians face two critical challenges: **diagnostic fatigue** and the need for **sterile workflows**.

**VoxRay AI** solves this by acting as a hands-free, intelligent assistant. It synergizes visual analysis with a voice-first interface, offering:

- **Touchless Control:** Voice commands to analyze images.
- **Explainable AI:** Grad-CAM heatmaps showing where the model "looks".
- **Intelligent Consult:** Chat with an LLM that "sees" the diagnosis context.

> 📚 **[Read the Full Documentation](./docs/README.md)** for detailed architecture and guides.

## 🆕 What's New in v2.0

VoxRay AI v2 is a production-hardened release with versioned APIs, feature flags, and multilingual support:

- **API Versioning:** V1 and V2 endpoints with deprecation headers
- **Feature Flags:** 16 configurable `FF_*` flags for gradual rollout
- **Multilingual Support:** 5 active languages (EN, ES, FR, DE, ZH)
- **DICOM Support:** Native DICOM file handling with anonymization
- **Ensemble Predictions:** Uncertainty quantification for predictions
- **Medical Vocabulary:** Automatic correction of medical terminology
- **Prometheus Metrics:** Built-in `/metrics` endpoint for monitoring

See [CHANGELOG_V1_TO_V2.md](./CHANGELOG_V1_TO_V2.md) for full details.

## 🚀 Key Features

### 🔒 Secure Authentication

- Integrated **Stack Auth** for enterprise-grade security.
- Role-based access protecting patient data types and API endpoints.

### 👁️ VoxRay Vision

- **Pathology Detection:** Custom ResNet50V2 model detecting Pneumonia, Fractures, and more.
- **Visual Explainability:** Real-time Grad-CAM heatmap overlays.
- **Pro Tools:** Window/Level (Brightness/Contrast) controls natively in browser.
- **DICOM Support (v2):** Native DICOM file parsing with metadata anonymization.

### 🎙️ VoxRay Voice

- **Sterile Workflow:** Hands-free operation using **OpenAI Whisper**.
- **Natural Response:** Neural TTS (Edge-TTS) for lifelike audio briefings.
- **Multilingual (v2):** Support for 5 languages with automatic detection.
- **Medical Vocabulary (v2):** Automatic correction of medical terminology.

### 🧠 VoxRay Intelligence

- **Context-Aware Chat:** Powered by **Gemini 2.0 Flash**.
- **RAG-Lite:** Injects diagnosis context into the chat automatically.
- **Multilingual Chat (v2):** Language enforcement for consistent responses.

## 📦 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Stack Auth Account

### Installation

1.  **Clone & Setup Backend**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r backend/requirements.txt
    ```

2.  **Setup Frontend**

    ```bash
    cd frontend
    npm install
    ```

3.  **Run Application**

    ```bash
    # Terminal 1: Backend
    uvicorn backend.api.main:app --reload

    # Terminal 2: Frontend
    npm run dev
    ```

[View Detailed Installation Guide](./docs/getting-started/installation.md)

## 🏭 MLOps Pipeline

The project includes a TFX pipeline for model training.
See [Architecture Documentation](./docs/architecture/README.md) for details.

## 🤝 Contributing

We welcome contributions! Please check [CONTRIBUTING](./docs/contributing/README.md).

---

_Built for the Future of Healthcare._
