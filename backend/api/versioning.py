import logging
from fastapi import FastAPI, APIRouter
from typing import Callable, Any

logger = logging.getLogger(__name__)


class APIVersionMiddleware:
    """
    Middleware to attach version headers and deprecation warnings.
    Does not change routing behavior, only headers.
    """

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")

        async def send_wrapper(message: dict):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])

                # Add version headers
                if path.startswith("/v1/"):
                    headers.append((b"x-api-version", b"1.0"))
                    headers.append((b"x-api-deprecation-date", b"2026-12-31"))
                    headers.append(
                        (
                            b"warning",
                            b"299 - 'V1 API is deprecated. Please migrate to /v2 endpoints.'",
                        )
                    )
                elif path.startswith("/v2/"):
                    headers.append((b"x-api-version", b"2.0"))
            await send(message)

        await self.app(scope, receive, send_wrapper)


def setup_versioning(app: FastAPI) -> None:
    """
    Configure versioned routing:

    - Root endpoints (/predict/image, /chat, etc.) remain V1 (backward compat).
    - /v1/* provides explicit stable aliases.
    - /v2/* hosts the new enhanced endpoints.

    This function MUST be called after all V1 endpoints are defined in main.py.
    """
    # Import v2 router (will create placeholder if doesn't exist)
    try:
        from backend.api import v2

        v2_router_exists = True
    except ImportError:
        v2_router_exists = False
        logger.warning("backend.api.v2 module not found, skipping v2 router inclusion")

    # Import V1 handlers from main.py
    from backend.api.main import (
        predict_image,
        transcribe_audio,
        generate_speech,
        chat_endpoint,
        health_check,
    )

    # 1. /v1 aliases pointing to existing handlers (no logic duplication)
    v1_router = APIRouter(prefix="/v1", tags=["v1-stable"])
    v1_router.add_api_route("/predict/image", predict_image, methods=["POST"])
    v1_router.add_api_route("/transcribe/audio", transcribe_audio, methods=["POST"])
    v1_router.add_api_route("/generate/speech", generate_speech, methods=["POST"])
    v1_router.add_api_route("/chat", chat_endpoint, methods=["POST"])
    v1_router.add_api_route("/health", health_check, methods=["GET"])

    app.include_router(v1_router)

    # 2. /v2 enhanced router (if exists)
    if v2_router_exists:
        app.include_router(v2.router, prefix="/v2", tags=["v2"])
        logger.info(
            "✅ API versioning configured: /v1/*, /v2/*, and root-level V1 endpoints"
        )
    else:
        logger.info(
            "✅ API versioning configured: /v1/* and root-level V1 endpoints (v2 pending)"
        )
