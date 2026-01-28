# System Prerequisites

Before installing VoxRay AI, ensure your system meets the following requirements.

## Hardware Requirements

| Component   | Minimum | Recommended | Notes                                 |
| ----------- | ------- | ----------- | ------------------------------------- |
| **CPU**     | 4 Cores | 8+ Cores    | Modern AMD Ryzen / Intel Core i7+     |
| **RAM**     | 8 GB    | 16 GB+      | 16GB required for TFX training        |
| **Storage** | 10 GB   | 50 GB       | SSD recommended for data loading      |
| **GPU**     | None    | NVIDIA GPU  | 6GB+ VRAM for faster inference (CUDA) |

## Software Requirements

### Core Runtime

- **Node.js**: Version 18.0 or higher.
- **Python**: Version 3.10 to 3.12 (3.12 recommended for backend).

### External Accounts

- **Stack Auth**: Required for user management and authentication.
- **OpenRouter**: Required for accessing the Gemini 2.0 LLM.

### Optional Tools

- **WSL2 (Windows Subsystem for Linux)**: Required only if you plan to run the TFX training pipeline.
- **VS Code**: Recommended IDE with Python and React extensions.
