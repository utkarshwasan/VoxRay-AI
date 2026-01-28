# Development Guide

## Coding Standards

### Python (Backend)

- Follow PEP 8 guidelines.
- Use type hints (`typing.List`, `typing.Optional`) for all function signatures.
- Use `pathlib` for file paths, not `os.path`.

### React (Frontend)

- Use Functional Components with Hooks.
- Avoid inline styles; use Tailwind CSS utility classes.
- Use `prop-types` for component validation.

## Git Workflow

1.  **Main Branch**: `main` contains production-ready code.
2.  **Feature Branches**: Create branches like `feature/voice-control` or `fix/auth-bug`.
3.  **Commits**: Use descriptive messages (e.g., "feat: add Grad-CAM overlay" or "fix: resolve CORS issue").
