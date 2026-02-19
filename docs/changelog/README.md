# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-19

### Added

- **V2 API Layer:** Versioned endpoints with deprecation headers
- **Feature Flags:** 16 configurable `FF_*` environment variables
- **Multilingual Support:** 5 active languages (EN, ES, FR, DE, ZH)
- **DICOM Support:** Native DICOM file handling with anonymization
- **Ensemble Predictions:** Uncertainty quantification for predictions
- **Medical Vocabulary:** Automatic correction of medical terminology
- **Prometheus Metrics:** Built-in `/metrics` endpoint for monitoring
- **Wake Word Detection:** Stub endpoint for hands-free activation

### Changed

- Replaced deprecated `@app.on_event("startup")` with lifespan context manager
- Updated API deprecation date to 2026-12-31
- Enhanced chat with language enforcement for multilingual responses

### Fixed

- API documentation accuracy for v2 endpoints
- Missing documentation files created
- Test suite reliability improvements

### Removed

- Internal development artifacts (`Implementation_v2/`, `shared_context/`)
- Temporary test scripts from root directory
- Unused deployment documentation

See [CHANGELOG_V1_TO_V2.md](../../CHANGELOG_V1_TO_V2.md) for full details.

## [1.0.0] - 2025-01-01

### Added

- Initial release of VoxRay AI.
- Computer Vision module (ResNet50V2).
- Voice Interface (Whisper + Edge-TTS).
- Conversational AI (Gemini 2.0).
- TFX Training Pipeline.
