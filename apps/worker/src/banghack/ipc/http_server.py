"""HTTP API server untuk config dan model discovery."""
from __future__ import annotations

import logging
import os
from typing import Any

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)


def create_app(
    llm_adapter: Any,
    audio_lib_manager: Any = None,
    classifier_rules_count: int = 0,
    live_director: Any = None,
    cost_tracker: Any = None,
) -> FastAPI:
    """Create FastAPI app with config and model endpoints.

    Args:
        llm_adapter: LLMAdapter instance to query configuration
        audio_lib_manager: AudioLibraryManager instance (v0.4)
        classifier_rules_count: Number of classifier rules loaded (v0.4)
        live_director: LiveDirector instance (v0.4)
        cost_tracker: CostTracker instance (v0.4)

    Returns:
        FastAPI application instance
    """
    app = FastAPI(title="Bang Hack API", version="0.4.0")

    # CORS for local development (Svelte controller)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4321",
            "http://127.0.0.1:4321",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/models")
    async def get_available_models() -> dict[str, Any]:
        """Fetch available models from 9router."""
        ninerouter_base = os.getenv("NINEROUTER_BASE_URL", "http://localhost:20128/v1")
        try:
            resp = requests.get(f"{ninerouter_base}/models", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("data", [])
                return {
                    "success": True,
                    "source": "9router",
                    "base_url": ninerouter_base,
                    "count": len(models),
                    "models": models,
                }
            return {
                "success": False,
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
            }
        except Exception as e:
            log.error("Failed to fetch models from 9router: %s", e)
            return {"success": False, "error": str(e)}

    @app.get("/api/config/llm")
    async def get_llm_config() -> dict[str, Any]:
        """Get current LLM tier configuration."""
        return {
            "success": True,
            "tiers": llm_adapter.get_model_list(),
            "env": {
                "NINEROUTER_BASE_URL": os.getenv("NINEROUTER_BASE_URL", ""),
                "DEEPSEEK_API_KEY": "***" if os.getenv("DEEPSEEK_API_KEY") else "",
                "ANTHROPIC_API_KEY": "***" if os.getenv("ANTHROPIC_API_KEY") else "",
            },
        }

    @app.get("/health")
    async def health() -> Any:
        """Health check endpoint — v0.4 extended."""
        # Audio library
        audio_ready = False
        clip_count = 0
        if audio_lib_manager is not None:
            audio_ready = audio_lib_manager.is_ready
            clip_count = audio_lib_manager.clip_count

        # Classifier
        classifier_ready = classifier_rules_count > 0

        # Director
        director_ready = False
        director_state = "IDLE"
        if live_director is not None:
            director_ready = live_director.is_ready
            director_state = live_director.mode.value

        # Budget
        budget_remaining = 0.0
        if cost_tracker is not None:
            snap = cost_tracker.snapshot()
            budget_remaining = snap.get("budget_idr", 0) - snap.get("total_idr", 0)

        all_ready = audio_ready and classifier_ready and director_ready
        status_code = 200 if all_ready else 503

        body = {
            "status": "ok" if all_ready else "degraded",
            "audio_library_ready": audio_ready,
            "audio_library_clip_count": clip_count,
            "classifier_ready": classifier_ready,
            "classifier_rules_count": classifier_rules_count,
            "director_ready": director_ready,
            "director_state": director_state,
            "budget_remaining_idr": round(budget_remaining, 2),
            "worker_version": "0.4.0",
            "static_url": "http://localhost:8766/static",  # URL untuk akses static files
        }
        return JSONResponse(content=body, status_code=status_code)

    return app
