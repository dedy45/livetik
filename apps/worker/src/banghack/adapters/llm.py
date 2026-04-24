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
                "model": os.getenv("NINEROUTER_MODEL", "openai/opencode-nvidia-ollama"),
                "api_base": ninerouter_base,
                "api_key": ninerouter_key,
                "timeout": 15,
            },
            "model_info": {"id": "ninerouter"},
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

    def update_tier_model(self, tier_id: str, model: str) -> None:
        """Update the model string for a specific tier and rebuild router.

        Args:
            tier_id: one of 'ninerouter' | 'deepseek' | 'claude_haiku'
            model: LiteLLM model string e.g. 'openai/gpt-4o-mini'
        """
        # Patch the in-memory model_list then rebuild
        for deployment in self.router.model_list:
            info = deployment.get("model_info", {})
            if info.get("id") == tier_id:
                deployment["litellm_params"]["model"] = model
                log.info("updated tier %s model → %s", tier_id, model)
                break
        else:
            raise ValueError(f"tier_id '{tier_id}' not found in router")
        # Rebuild router with updated list
        self.router = Router(
            model_list=self.router.model_list,
            fallbacks=[{"chat": ["chat"]}],
            num_retries=1,
            routing_strategy="simple-shuffle",
            allowed_fails=2,
            cooldown_time=60,
        )

    async def test_with_model(
        self, model: str, api_base: str, api_key: str, prompt: str = "Jawab 1 kata: halo"
    ) -> LLMResult:
        """One-shot test with arbitrary model/base/key — does NOT affect main router.

        LiteLLM requires a provider prefix (e.g. 'openai/') to know which SDK to use.
        For OpenAI-compatible proxies like 9router, always use 'openai/<model_id>'.

        Auto-prefix rules:
        - If model already has a known provider prefix → use as-is
        - If api_base is set (proxy) and no prefix → prepend 'openai/'
        - Bare model IDs like 'KIRO' → 'openai/KIRO'
        """
        import time

        from litellm import acompletion  # type: ignore[import-not-found]

        # Known LiteLLM provider prefixes — if none present, auto-add 'openai/'
        known_prefixes = (
            "openai/", "anthropic/", "deepseek/", "google/", "cohere/",
            "mistral/", "groq/", "together_ai/", "huggingface/", "ollama/",
            "azure/", "bedrock/", "vertex_ai/", "replicate/",
        )
        effective_model = model.strip()
        if not any(effective_model.startswith(p) for p in known_prefixes):
            # No provider prefix — for proxy (api_base set) use openai/
            effective_model = f"openai/{effective_model}"
            log.info("auto-prefixed model: %s → %s", model, effective_model)

        # Resolve api_base and api_key from env if not provided
        effective_base = api_base.strip() or os.getenv("NINEROUTER_BASE_URL", "")
        effective_key = api_key.strip() or os.getenv("NINEROUTER_API_KEY", "sk-dummy")

        t0 = time.monotonic()
        try:
            kwargs: dict = {
                "model": effective_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 20,
                "timeout": 20,
            }
            if effective_base:
                kwargs["api_base"] = effective_base
            if effective_key:
                kwargs["api_key"] = effective_key
            resp: ModelResponse = await acompletion(**kwargs)
            latency_ms = int((time.monotonic() - t0) * 1000)
            text = (resp.choices[0].message.content or "").strip()
            return LLMResult(
                text=text, tier="custom", model=effective_model,
                prompt_tokens=getattr(resp.usage, "prompt_tokens", 0),
                completion_tokens=getattr(resp.usage, "completion_tokens", 0),
                latency_ms=latency_ms,
            )
        except Exception as e:
            log.error("test_with_model failed (model=%s): %s", effective_model, e)
            # Re-raise with clear message so cmd_result shows useful error
            raise RuntimeError(
                f"model={effective_model!r} → {type(e).__name__}: {str(e)[:200]}"
            ) from e

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
