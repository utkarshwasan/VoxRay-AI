# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) documenting significant technical decisions made during the development of VoxRay AI.

## What is an ADR?

An Architecture Decision Record captures the context, decision, and consequences of a significant architectural choice. ADRs help future developers understand _why_ the system is built the way it is.

## Decision Log

| ID    | Title                                       | Status   | Date       |
| ----- | ------------------------------------------- | -------- | ---------- |
| ADR-1 | Use FastAPI for backend framework           | Accepted | 2025-01-01 |
| ADR-2 | Use Stack Auth for authentication           | Accepted | 2025-01-01 |
| ADR-3 | Use Edge-TTS for text-to-speech             | Accepted | 2025-01-01 |
| ADR-4 | Disable Hindi STT (whisper-base limitation) | Accepted | 2026-01-01 |
| ADR-5 | Feature flags for v2 gradual rollout        | Accepted | 2026-01-01 |

## ADR-4: Disable Hindi STT

**Context:** The `whisper-base` model cannot reliably distinguish spoken Hindi from Urdu due to phonetic similarity. Both languages share the same phoneme set when spoken.

**Decision:** Disable Hindi (`hi`) from the active language list. Hindi TTS voice (`hi-IN-SwaraNeural`) is also disabled to maintain consistency.

**Consequences:** Hindi-speaking users must use English. Re-enabling requires upgrading to `faster-whisper-medium` or higher, which has better language discrimination.

**Re-enable path:** Uncomment all lines marked `# hi-disabled` in:

- `backend/voice/multilingual.py`
- `backend/api/main.py`
- `frontend/src/components/VoiceSection.jsx`

## ADR-5: Feature Flags for V2 Rollout

**Context:** V2 introduces ML ensemble models, DICOM support, FHIR integration, and other features that require careful production rollout.

**Decision:** All v2 features are gated behind `FF_*` environment variables. Default is `false` (disabled). Features are enabled explicitly per deployment.

**Consequences:** Zero-risk deployment. New features can be enabled/disabled without code changes. See [Environment Variables](../../reference/environment-variables.md) for the full list.

## Template

See [template.md](template.md) for the ADR template format.
