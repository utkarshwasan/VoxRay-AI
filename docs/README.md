# VoxRay AI Documentation

> An advanced multimodal medical console combining Computer Vision and Conversational AI to streamline clinical workflows.

## Welcome

Welcome to the VoxRay AI documentation. VoxRay AI acts as a hands-free, intelligent assistant for radiologists and clinicians, synergizing visual analysis with a voice-first interface. It offers instant pathology detection, visual explainability (Grad-CAM), and intelligent second opinions via LLMs.

## Quick Navigation

| Section                                  | Description                                          |
| ---------------------------------------- | ---------------------------------------------------- |
| [🚀 Getting Started](./getting-started/) | Installation, prerequisites, and first project setup |
| [🏗️ Architecture](./architecture/)       | System design, components, and TFX pipeline          |
| [📚 API Reference](./api/)               | REST API endpoints (prediction, transcription, chat) |
| [📖 Guides](./guides/)                   | User guides, development workflows, and operations   |
| [🔧 Reference](./reference/)             | Configuration, environment variables, and SDKs       |
| [❓ Troubleshooting](./troubleshooting/) | Common issues, FAQ, and debugging                    |
| [🤝 Contributing](./contributing/)       | How to contribute to the codebase                    |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/utkarshwasan/VoxRay-AI.git
cd VoxRay-AI

# Backend Setup
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt

# Frontend Setup
cd frontend
npm install
npm run dev
```

[Full Quick Start Guide →](./getting-started/quick-start.md)

## Features

- **🔒 Secure Authentication:** Role-based access via Stack Auth.
- **👁️ Computed Vision:** Real-time X-ray analysis (ResNet50V2) with Grad-CAM explainability.
- **🎙️ Voice Interface:** Hands-free control with Whisper STT and Edge-TTS.
- **🧠 Conversational AI:** Context-aware medical chat powered by Gemini 2.0.
- **🏭 Production MLOps:** End-to-end TFX pipeline for model training.

## Requirements

- **Node.js**: >= 18.0
- **Python**: >= 3.10 (3.12 recommended)
- **Stack Auth Account**: For authentication keys.
- **OpenRouter API Key**: For LLM features.

## Support

- 📧 Email: support@voxray.ai
- 🐛 Issues: [GitHub Issues](https://github.com/utkarshwasan/VoxRay-AI/issues)

## License

MIT License - see [LICENSE](../LICENSE) for details.
