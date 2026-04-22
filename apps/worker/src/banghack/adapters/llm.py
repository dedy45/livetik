"""LLM adapter — LiteLLM Router: 9router primary + DeepSeek/Claude fallback."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from litellm import Router
from litellm.utils import ModelResponse

log = logging.getLogger(__name__)


@dataclass(slots=True)
class LLMResult:
    text: str
    tier: str  # ninerouter | deepseek | claude_haiku | error
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int


def _build_router() -> Router:
    """Build LiteLLM Router with 3-tier fallback."""
    ninerouter_base = os.getenv("NINEROUTER_BASE_URL", "http://localhost:20128/v1")
    ninerouter_key = os.getenv("NINEROUTER_API_KEY", "sk-dummy-9router")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    model_list: list[dict] = [
        {
            "model_name": "chat",
            "litellm_params": {
                "model": "openai/claude-3-5-sonnet-20241022",
                "api_base": ninerouter_base,
                "api_key": ninerouter_key,
                "timeout": 15,
            },
            "model_info": {"id": "ninerouter"},  # Removed tier - not needed for routing
        },
    ]
    if deepseek_key:
        model_list.append({
            "model_name": "chat",
            "litellm_params": {
                "model": "deepseek/deepseek-chat",
                "api_key": deepseek_key,
                "timeout": 20,
            },
            "model_info": {"id": "deepseek"},
        })
    if anthropic_key:
        model_list.append({
            "model_name": "chat",
            "litellm_params": {
                "model": "anthropic/claude-3-5-haiku-latest",
                "api_key": anthropic_key,
                "timeout": 20,
            },
            "model_info": {"id": "claude_haiku"},
        })

    return Router(
        model_list=model_list,
        fallbacks=[{"chat": ["chat"]}],
        num_retries=1,
        routing_strategy="simple-shuffle",
        allowed_fails=2,
        cooldown_time=60,
    )


class LLMAdapter:
    def __init__(self) -> None:
        self.router = _build_router()

    def get_model_list(self) -> list[dict]:
        """Return list of configured models with their tier info."""
        models = []
        for deployment in self.router.model_list:
            model_info = deployment.get("model_info", {})
            litellm_params = deployment.get("litellm_params", {})
            models.append({
                "id": model_info.get("id", "unknown"),
                "model": litellm_params.get("model", "unknown"),
                "api_base": litellm_params.get("api_base", ""),
                "timeout": litellm_params.get("timeout", 0),
            })
        return models

    async def reply(self, persona: str, user_text: str, max_tokens: int = 80) -> LLMResult:
        import time
        t0 = time.monotonic()
        try:
            resp: ModelResponse = await self.router.acompletion(
                model="chat",
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            latency_ms = int((time.monotonic() - t0) * 1000)
            text = (resp.choices[0].message.content or "").strip()
            model_id = resp.model or "unknown"
            # Map model to tier (LiteLLM attaches deployment info)
            tier = "ninerouter"
            if "deepseek" in model_id.lower():
                tier = "deepseek"
            elif "haiku" in model_id.lower() or "anthropic" in model_id.lower():
                tier = "claude_haiku"
            usage = resp.usage or {}
            return LLMResult(
                text=text,
                tier=tier,
                model=model_id,
                prompt_tokens=getattr(usage, "prompt_tokens", 0),
                completion_tokens=getattr(usage, "completion_tokens", 0),
                latency_ms=latency_ms,
            )
        except Exception as e:
            log.error("LLM all tiers failed: %s", e)
            return LLMResult(
                text="", tier="error", model="none",
                prompt_tokens=0, completion_tokens=0,
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
