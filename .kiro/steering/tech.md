---
inclusion: always
---
# Tech Stack — Bang Hack Worker

## Stack Lock (do not change without explicit approval)

### Backend Worker
- Python 3.11+ with UV package manager
- WebSocket server: websockets 12+ on port 8765
- HTTP API: FastAPI + uvicorn on port 8766
- LLM: LiteLLM Router 3-tier (9router → DeepSeek → Claude Haiku)
- TTS: Cartesia AsyncCartesia (5-key pool) + edge-tts fallback
- Audio: ffplay subprocess (pcm_f32le @ 44100 → VB-CABLE)
- TikTok: TikTokLive library with TikTokSupervisor hot-swap
- Persistence: .env (atomic write with backup) + .state.json (runtime toggles)

### Frontend Controller
- SvelteKit with Svelte 5 runes ($state, $derived, $effect)
- Tailwind CSS v4
- No external chart libraries — SVG polyline for cost chart

### Key Ports
- WS: ws://127.0.0.1:8765 (bidirectional commands + metrics broadcast)
- HTTP: http://127.0.0.1:8766 (FastAPI config/model API)

### Audio Format
- Cartesia output: container=wav, encoding=pcm_f32le, sample_rate=44100
- This matches the tested working script — do NOT change to pcm_s16le/22050

### Cartesia Emotions
Valid values: neutral | happy | sad | angry | dramatic | comedic
Sent via: voice.experimental_controls.emotions = [emotion]
