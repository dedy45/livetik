# 🚨 06 · Error Handling Matrix

> **Canonical**: setiap error punya code, penyebab, file pertama yang dibuka, dan strategi recovery.  
> Controller UI halaman `/errors` baca dari doc ini.

---

## 1. Error Code Schema

Format: `<DOMAIN>_<SPECIFIC>`  
Contoh: `LLM_RATE_LIMIT`, `TIKTOK_DISCONNECT`

| Domain | Prefix | File pertama dibuka |
|--------|--------|---------------------|
| TikTok | TIKTOK_ | adapters/tiktok.py |
| LLM | LLM_ | adapters/llm.py |
| TTS | TTS_ | adapters/tts.py |
| Guardrail | GUARDRAIL_ | core/guardrail.py |
| OBS | OBS_ | adapters/obs.py |
| IPC | IPC_ | ipc/ws_server.py atau ipc/http_api.py |
| Config | CONFIG_ | config/settings.py |
| Queue | QUEUE_ | core/queue.py |

---

## 2. Master Matrix

| Code | Domain | Penyebab | Severity | Recovery | File pertama | User action |
|------|--------|----------|----------|----------|--------------|-------------|
| TIKTOK_DISCONNECT | TikTok | WS dropped | High | Auto-reconnect 3× exp backoff | adapters/tiktok.py | Monitor /errors |
| TIKTOK_ROOM_NOT_LIVE | TikTok | Room offline | High | Stop worker, alert | adapters/tiktok.py | Mulai Live dulu |
| TIKTOK_AUTH_FAIL | TikTok | Session expired | High | Re-auth manual | adapters/tiktok.py | Login ulang TikTok |
| TIKTOK_RATE_LIMIT | TikTok | Too many requests | Medium | Backoff 60s | adapters/tiktok.py | Tunggu |
| LLM_RATE_LIMIT | LLM | DeepSeek 429 | Medium | Fallback Claude, backoff | adapters/llm.py | Cek quota DeepSeek |
| LLM_TIMEOUT | LLM | Response >10s | Medium | Retry 2×, skip comment | adapters/llm.py | Cek internet |
| LLM_FALLBACK_FAIL | LLM | Claude juga fail | High | Skip comment, log DLQ | adapters/llm.py | Cek API keys |
| LLM_INVALID_KEY | LLM | API key salah | Critical | Stop worker | adapters/llm.py | Fix .env |
| TTS_NETWORK | TTS | Edge-TTS unreachable | Medium | Retry 3×, skip audio | adapters/tts.py | Cek internet |
| TTS_FFPLAY_NOT_FOUND | TTS | ffplay not in PATH | Critical | Stop TTS, text-only mode | adapters/tts.py | Install FFmpeg |
| TTS_AUDIO_OVERLAP | TTS | Queue backed up | Low | Serial queue enforced | adapters/tts.py | Normal, auto-handled |
| GUARDRAIL_INPUT_BLOCKED | Guardrail | Comment mengandung URL/brand | Info | Skip comment, log | core/guardrail.py | Normal |
| GUARDRAIL_OUTPUT_BLOCKED | Guardrail | Reply LLM mengandung forbidden | Warning | Regenerate atau skip | core/guardrail.py | Review persona |
| OBS_WRITE_FAIL | OBS | Permission denied / disk full | High | Retry 3×, log error | adapters/obs.py | Cek disk space |
| IPC_WS_DISCONNECT | IPC | Controller disconnected | Low | Auto-reconnect | ipc/ws_server.py | Normal |
| IPC_HTTP_BIND_FAIL | IPC | Port 8766 sudah dipakai | Critical | Stop worker | ipc/http_api.py | Kill proses lain |
| CONFIG_INVALID | Config | .env value invalid | Critical | Stop worker | config/settings.py | Fix .env |
| QUEUE_OVERFLOW | Queue | >100 pending events | Warning | Drop oldest, log | core/queue.py | Kurangi traffic |

---

## 3. Recovery Pattern Reusable

### 3a. Exponential backoff (untuk network retry)

```python
async def retry_with_backoff(func, max_attempts=3, base=1.0, factor=2.0):
    for attempt in range(max_attempts):
        try:
            return await func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(base * (factor ** attempt))
```

### 3b. Circuit breaker (untuk provider failing)

State: closed → open (trip setelah N fail) → half-open (trial after cooldown)

```python
class CircuitBreaker:
    def __init__(self, fail_threshold=5, cooldown=60):
        self.fails = 0
        self.state = "closed"
        ...
```

### 3c. Dead-letter queue

Error events yang tidak bisa di-recover masuk `logs/dlq-YYYY-MM-DD.jsonl` untuk review manual.

---

## 4. On-Call Runbook (Dedy saat Live)

| Gejala | Cek pertama | Aksi |
|--------|-------------|------|
| Status merah, tidak ada reply | /errors → TIKTOK_ | Cek koneksi internet, restart worker |
| Reply lambat >10s | /errors → LLM_TIMEOUT | Cek DeepSeek status page |
| Tidak ada suara | /errors → TTS_ | Cek VB-CABLE, ffplay |
| Reply mengandung link | /errors → GUARDRAIL_ | Review persona.md, tambah blocklist |
| Controller tidak connect | Status dot merah | Restart controller, cek port 8765 |
| Biaya melonjak | /cost | Cek token per reply, turunkan max_tokens |

---

## 5. Error Budget & SLO

| SLO | Target | Measurement |
|-----|--------|-------------|
| Reply success rate | ≥95% | replies_sent / comments_received |
| Reply latency p95 | ≤8s | dari comment_received ke reply_generated |
| Guardrail false negative | 0% | manual audit per session |
| Worker uptime per Live | ≥99% | downtime / total_live_duration |
