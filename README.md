---
title: VoxRay AI
emoji: 🩻
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# VoxRay AI

**An advanced multimodal medical console combining Computer Vision and Conversational AI to streamline clinical workflows.**

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

## 🚀 Key Features

### 🔒 Secure Authentication

- Integrated **Stack Auth** for enterprise-grade security.
- Role-based access protecting patient data types and API endpoints.

### 👁️ VoxRay Vision

- **Pathology Detection:** Custom ResNet50V2 model detecting Pneumonia, Fractures, and more.
- **Visual Explainability:** Real-time Grad-CAM heatmap overlays.
- **Pro Tools:** Window/Level (Brightness/Contrast) controls natively in browser.

### 🎙️ VoxRay Voice

- **Sterile Workflow:** Hands-free operation using **OpenAI Whisper**.
- **Natural Response:** Neural TTS (Edge-TTS) for lifelike audio briefings.

### 🧠 VoxRay Intelligence

- **Context-Aware Chat:** Powered by **Gemini 2.0 Flash**.
- **RAG-Lite:** Injects diagnosis context into the chat automatically.

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
