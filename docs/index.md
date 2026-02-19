# VoxRay AI Documentation

**Version:** 2.0  
**Last Updated:** 2026-02-19

---

## Overview

VoxRay AI is an intelligent radiology assistant that combines computer vision, natural language processing, and voice interfaces to help healthcare professionals analyze medical imaging.

## Key Features

### Core Capabilities

- **X-Ray Analysis**: AI-powered chest X-ray classification with Grad-CAM explainability
- **Voice Interface**: Speech-to-text input and text-to-speech output for hands-free operation
- **Multilingual Support**: 5 languages supported (English, Spanish, French, German, Chinese)
- **Clinical Chat**: AI assistant for radiological findings explanation

### V2 Enhancements

- **Ensemble Model**: Multi-model predictions with uncertainty quantification
- **DICOM Support**: Native DICOM file handling with anonymization
- **FHIR Integration**: Healthcare interoperability standard support
- **Audit Logging**: HIPAA-compliant operation tracking
- **Feature Flags**: Zero-risk deployment with gradual rollout capability

## Quick Links

- [Getting Started](getting-started/quick-start.md)
- [Installation Guide](getting-started/installation.md)
- [API Reference](api/README.md)
- [Architecture Overview](architecture/README.md)

## Supported Languages

| Language | Code | Status                       |
| -------- | ---- | ---------------------------- |
| English  | en   | ✅ Active                    |
| Spanish  | es   | ✅ Active                    |
| French   | fr   | ✅ Active                    |
| German   | de   | ✅ Active                    |
| Chinese  | zh   | ✅ Active                    |
| Hindi    | hi   | ❌ Disabled (STT limitation) |

## API Versions

- **v1**: Stable production endpoints (backward compatible)
- **v2**: Enhanced endpoints with feature flag gating

## Documentation Structure

```
docs/
├── api/              # API endpoint documentation
├── architecture/     # System design and decisions
├── getting-started/  # Installation and setup
├── guides/           # Development guides
├── mlops/            # ML operations
├── operations/       # Deployment and maintenance
├── reference/        # Configuration reference
├── security/         # Security documentation
└── troubleshooting/  # Common issues and solutions
```

## License

See [LICENSE](../LICENSE) for details.
