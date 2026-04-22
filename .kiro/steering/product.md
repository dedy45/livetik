# Product Context — Bang Hack TikTok Live AI

## Goal
Build a zero-cost AI co-pilot for TikTok Live @interiorhack.id that replies to viewer comments in real-time using the persona "Bang Hack".

## Persona
- Name: Bang Hack
- Brand: @interiorhack.id
- Language: Indonesian (santai/casual)
- Max reply length: 2 short sentences
- Focus: interior design, furniture, rangka baja (steel frame)
- Never mention exact prices or contact info

## Core Loop
1. TikTok Live comment arrives via TikTokLive library
2. Guardrail filters spam/forbidden content
3. LLM generates reply (9router → DeepSeek → Claude Haiku fallback)
4. Cartesia TTS synthesizes audio (Sonic-3, pcm_f32le @ 44100)
5. ffplay plays audio to VB-CABLE → OBS → TikTok Live stream

## Budget Constraint
- Hard cap: Rp 5,000/day (configurable via UI)
- 9router subscription = Rp 0 per reply (primary)
- Fallback tiers only used when 9router fails

## Zero-Restart Config
All configuration must be editable via /config UI without restarting the worker.
