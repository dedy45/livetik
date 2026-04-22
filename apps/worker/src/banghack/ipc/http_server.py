"""HTTP API server untuk config dan model discovery."""
from __future__ import annotations

import logging
import os
from typing import Any

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

log = logging.getLogger(__name__)


def create_app(llm_adapter: Any) -> FastAPI:
    """Create FastAPI app with config and model endpoints.

    Args:
        llm_adapter: LLMAdapter instance to query configuration

    Returns:
        FastAPI application instance
    """
    app = FastAPI(title="Bang Hack API", version="0.1.0-dev")

    # CORS for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4321", "http://127.0.0.1:4321"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/models")
    async def get_available_models() -> dict[str, Any]:
        """Fetch available models from 9router.

        Returns:
            Dictionary with models list and metadata
        """
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
            return {
                "success": False,
                "error": str(e),
            }

    @app.get("/api/config/llm")
    async def get_llm_config() -> dict[str, Any]:
        """Get current LLM tier configuration.

        Returns:
            Dictionary with configured tiers and their settings
        """
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
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok"}

    return app
