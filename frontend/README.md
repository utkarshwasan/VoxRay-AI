# VoxRay AI Frontend

**Version: 2.0.0**

The React-based medical console UI for VoxRay AI. Provides a hands-free, voice-first interface for radiologists and clinicians.

## Features

- **X-Ray Analysis:** Upload and analyze X-ray images with Grad-CAM explainability
- **Voice Interface:** Hands-free control via speech recognition and TTS playback
- **Multilingual Support:** 5 languages (EN, ES, FR, DE, ZH)
- **Interactive Viewer:** Window/Level controls, zoom, pan for DICOM/images
- **Real-time Chat:** Context-aware medical consultation with LLM

## Tech Stack

- **React 18** with Vite for fast development
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Stack Auth** for authentication

## Getting Started

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_STACK_PUBLISHABLE_CLIENT_KEY=your_key
VITE_STACK_PROJECT_ID=your_project_id
VITE_API_URL=http://localhost:8000
```

## Scripts

| Command           | Description              |
| ----------------- | ------------------------ |
| `npm run dev`     | Start dev server         |
| `npm run build`   | Production build         |
| `npm run lint`    | Run ESLint               |
| `npm run preview` | Preview production build |

## Project Structure

```
src/
├── components/      # React components
│   ├── ui/          # Reusable UI components
│   ├── VoiceSection.jsx
│   └── XRaySection.jsx
├── contexts/        # React contexts
├── hooks/           # Custom hooks
├── pages/           # Page components
└── utils/           # Utility functions
```

## Documentation

See the main [project documentation](../docs/README.md) for full details.
