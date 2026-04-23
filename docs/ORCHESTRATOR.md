# 🧠 Orchestrator Implementation Plan — Python Worker + Svelte Control Center

> Terakhir diedit: 2026-04-23 | [Buka di Notion](https://www.notion.so/Orchestrator-Implementation-Plan-Python-Worker-Svelte-Control-Center-ebeaa1b997794405bad652a133f2afbe)

> 🎯 **Tujuan dokumen ini**: blueprint implementasi langsung untuk membangun **AI live orchestrator**: Python worker sebagai otak operasional, Svelte dashboard sebagai pusat kontrol realtime, OBS sebagai panggung, Cartesia/edge-tts sebagai suara, dan guardrail kuat supaya hemat token serta aman saat live.

## 0 · Reality Check

**Bisa dibangun**, tapi jangan mulai dari full autonomous.

Target realistis:

```
Phase 1: manual cockpit
Phase 2: AI suggested reply
Phase 3: semi-auto co-host
Phase 4: orchestrator scene + audio + comment
Phase 5: autonomous terbatas dengan guardrail keras
```

**Prinsip utama:**

- Svelte bukan otak. Svelte = cockpit.

- Python worker = orchestrator.

- LLM = pembuat bahasa, bukan pengambil keputusan tunggal.

- Rule engine = pengaman biaya, policy, dan flow live.

- Cartesia clip pre-generated = hemat token.

- LLM hanya dipakai jika komentar benar-benar layak dijawab.

---

## 1 · Arsitektur Final

```
TikTokLive comment listener
        ↓
Python Worker Orchestrator
        ↓
Decision Engine + Guardrail + Budget Gate
        ↓
┌───────────────────────┬───────────────────────┐
│ Pre-generated Audio    │ Dynamic AI Reply       │
│ Cartesia clip library  │ LLM → TTS → audio      │
└───────────────────────┴───────────────────────┘
        ↓
Audio Queue → VB-CABLE / ffplay → OBS / TikTok Studio
        ↓
OBS Scene + Overlay last comment / last reply
        ↑
Svelte Control Center via WebSocket
```

---

## 2 · Folder Structure Implementasi

```
apps/worker/src/banghack/
├── orchestrator/
│   ├── live_state.py          # state sesi live: produk, segmen, waktu, mode
│   ├── scheduler.py           # pilih audio idle / script berikutnya
│   ├── decision_engine.py     # keputusan: skip, overlay, voice, manual approve
│   ├── comment_classifier.py  # klasifikasi komentar murah tanpa LLM dulu
│   ├── budget_guard.py        # token, API key, cost, cooldown
│   └── health.py              # health check semua service
│
├── guardrails/
│   ├── text_filter.py         # link, nomor HP, toxic, forbidden topics
│   ├── commerce_policy.py     # harga, garansi, klaim, link luar
│   ├── rate_limit.py          # per user / per menit / per produk
│   └── output_validator.py    # validasi jawaban sebelum TTS
│
├── llm/
│   ├── router.py              # multi API key round-robin + fallback
│   ├── prompts.py             # prompt pendek per kategori
│   ├── cache.py               # cache komentar mirip → jawaban reusable
│   └── local_stub.py          # fallback rule-based tanpa LLM
│
├── audio/
│   ├── clip_library.py        # scan 160–220 audio Cartesia pregen
│   ├── audio_queue.py         # priority queue audio
│   ├── tts_cartesia.py        # dynamic reply voice
│   ├── tts_edge.py            # fallback gratis
│   └── player.py              # ffplay / VB-CABLE output
│
├── obs/
│   ├── obs_client.py          # obs-websocket scene switch
│   ├── overlays.py            # update last_comment.txt / last_reply.txt
│   └── scene_map.py           # produk → scene OBS
│
├── tiktok/
│   ├── listener.py            # TikTokLive read-only
│   └── events.py              # normalized Comment/Gift/Like/Follow
│
├── ipc/
│   ├── ws_server.py           # bidirectional WebSocket ke Svelte
│   └── commands.py            # command handler dashboard
│
└── telemetry/
    ├── logger.py              # JSON logs
    ├── metrics.py             # latency, queue, token, cost
    └── errors.py              # structured error codes
```

Svelte:

```
apps/controller/src/routes/
├── +page.svelte               # mission control
├── audio/+page.svelte         # clip library + queue
├── comments/+page.svelte      # inbox komentar + approve reply
├── scenes/+page.svelte        # OBS scene control
├── brain/+page.svelte         # AI decisions + reason
├── health/+page.svelte        # health checks
└── errors/+page.svelte        # error log + troubleshooting
```

---

## 3 · Data Model Minimal

### LiveState

```python
@dataclass
class LiveState:
    session_id: str
    mode: str  # manual | assisted | semi_auto | autonomous_safe
    started_at: float
    max_duration_s: int = 7200
    current_product: str = "PALOMA"
    current_segment: str = "opening"
    current_scene: str = "scene_opening"
    reply_enabled: bool = False
    auto_voice_enabled: bool = False
    llm_enabled: bool = True
    tts_enabled: bool = True
    token_budget_remaining: int = 0
```

### CommentDecision

```python
@dataclass
class CommentDecision:
    action: str  # skip | overlay | suggest_reply | voice_reply | manual_review
    priority: int
    reason: str
    needs_llm: bool
    safe_category: str
```

### AudioJob

```python
@dataclass
class AudioJob:
    kind: str  # pregen | dynamic_reply | alert | closing
    priority: int
    text: str | None
    file_path: str | None
    user: str | None
    product: str
```

---

## 4 · Guardrail Hemat Token

### Urutan filter sebelum LLM

```
1. Normalize text
2. Hard block: link, nomor HP, WA, IG, Telegram, SARA, adult, gambling
3. Dedup komentar mirip
4. Rate limit per user
5. Intent classifier murah berbasis regex
6. Cache lookup jawaban
7. Baru LLM jika komentar bernilai
```

### Kapan LLM boleh dipakai

| Komentar | Aksi | LLM? |
| --- | --- | --- |
| “halo” | pakai template greeting | ❌ |
| “harga?” | template harga aman | ❌ |
| “bisa buat pintu kontrakan?” | LLM short answer + guardrail | ✅ |
| “wa dong” | skip | ❌ |
| komentar panjang teknis | manual review / LLM | ✅ terbatas |
| spam berulang | skip + rate limit | ❌ |

### Token saving rule

```
LLM max 1 request / 8–15 detik
LLM max 3 reply / user / 10 menit
LLM max 30 dynamic replies / 30 menit test
Cache jawaban mirip 24 jam
Prompt pendek per produk, bukan system prompt panjang setiap request
```

---

## 5 · Multi API Key Round-Robin

### Tujuan

Saat ini pakai LLM gratisan multiple API key. Jadi perlu router yang:

- round-robin key

- cooldown saat rate limit

- matikan key yang error

- catat token per key

- fallback ke template kalau semua gagal

### Model sederhana

```python
class LLMKeyPool:
    def __init__(self, keys: list[str]):
        self.keys = [KeySlot(k) for k in keys]
        self.idx = 0

    def acquire(self) -> KeySlot:
        for _ in self.keys:
            slot = self.keys[self.idx]
            self.idx = (self.idx + 1) % len(self.keys)
            if slot.is_available():
                return slot
        raise NoLLMKeyAvailable()
```

### Fallback chain

```
1. free API key pool
2. second provider free/cheap
3. local rule-based answer
4. overlay only, no voice
5. skip
```

**Catatan realistis:** kalau live mulai menghasilkan, baru pertimbangkan:

- langganan LLM provider stabil

- sewa GPU untuk model lokal

- lokal LLM hanya untuk classifier / template expansion dulu, bukan semua jawaban

---

## 6 · Decision Engine

### Pseudocode inti

```python
def decide(comment, state):
    if hard_block(comment.text):
        return skip("forbidden")

    if is_duplicate(comment):
        return skip("duplicate")

    if rate_limited(comment.user):
        return skip("rate_limited")

    intent = classify_intent(comment.text)

    if intent in ["greeting", "price"]:
        return overlay_or_template_voice(intent, needs_llm=False)

    if intent in ["product_question", "compatibility", "installation"]:
        if state.mode == "manual":
            return manual_review("product question")
        return suggest_reply(needs_llm=True)

    if intent == "buying_intent":
        return voice_reply(needs_llm=True, priority=80)

    return overlay("low value comment")
```

---

## 7 · Audio Orchestration

### Prioritas audio

```
100 Emergency stop / operator
90  Closing / warning
80  Dynamic voice reply penting
70  Gift / follow alert
60  Segment transition
40  Pregen product context
20  Idle filler
```

### Rule saat sedang membaca naskah

```
Jika komentar penting masuk:
- tunggu audio clip selesai
- jeda 1 detik
- sebut username
- jawab voice
- update overlay
- lanjut audio segment berikutnya
```

### Jangan dilakukan

- Jangan potong audio di tengah kata.

- Jangan tumpuk dua TTS bersamaan.

- Jangan jawab semua komentar dengan voice.

- Jangan membuat live seperti call center otomatis.

---

## 8 · Svelte Dashboard: Fitur Wajib

### Mission Control

- [ ] Start session

- [ ] Pause AI

- [ ] Resume AI

- [ ] Emergency stop

- [ ] End live in 2 minutes

- [ ] Timer 2 jam

- [ ] Current product / segment

### Audio Queue

- [ ] Now playing

- [ ] Next audio

- [ ] Dynamic reply queue

- [ ] Skip / replay / move up / delete

- [ ] Filter audio by category

### Comment Inbox

- [ ] Comment realtime

- [ ] Username

- [ ] Intent classification

- [ ] Decision reason

- [ ] Button: reply voice

- [ ] Button: overlay only

- [ ] Button: skip

- [ ] Button: manual approve

### Brain Panel

- [ ] AI suggested reply

- [ ] Why AI chose this action

- [ ] Token estimate

- [ ] Safety status

- [ ] Approve / regenerate / shorter / warmer / more cautious

### OBS Control

- [ ] Scene list

- [ ] Active scene

- [ ] Switch scene

- [ ] Update last comment

- [ ] Update last reply

### Health Panel

- [ ] TikTok listener connected

- [ ] OBS websocket connected

- [ ] VB-CABLE output OK

- [ ] Cartesia OK

- [ ] Edge-TTS OK

- [ ] LLM key pool status

- [ ] Queue size

- [ ] Latency p95

---

## 9 · WebSocket Event Contract

### Worker → Svelte

```json
{ "type": "metrics", "queue_size": 3, "latency_p95_ms": 2400, "llm_calls": 12 }
```

```json
{ "type": "comment", "user": "Rina", "text": "bisa buat pintu kontrakan?", "intent": "compatibility" }
```

```json
{ "type": "decision", "action": "suggest_reply", "reason": "compatibility question", "needs_llm": true }
```

```json
{ "type": "audio_now", "kind": "dynamic_reply", "user": "Rina", "text": "Kak Rina..." }
```

```json
{ "type": "health", "obs": true, "tiktok": true, "tts": true, "llm_pool": "degraded" }
```

### Svelte → Worker

```json
{ "type": "cmd", "name": "pause_ai" }
```

```json
{ "type": "cmd", "name": "approve_reply", "comment_id": "c_123" }
```

```json
{ "type": "cmd", "name": "switch_product", "product": "CCTV_V380" }
```

```json
{ "type": "cmd", "name": "play_clip", "clip_id": "C_paloma_014" }
```

---

## 10 · Error Handling Matrix

| Error Code | Gejala | File pertama dicek | Fallback |
| --- | --- | --- | --- |
| TIKTOK_DISCONNECTED | Comment tidak masuk | `tiktok/listener.py` | reconnect backoff, dashboard warning |
| OBS_WS_DOWN | Scene tidak bisa ganti | `obs/obs_client.py` | lanjut audio, manual scene di OBS |
| LLM_KEYS_EXHAUSTED | AI reply gagal | `llm/router.py` | template reply / overlay only |
| TTS_CARTESIA_FAIL | Voice dynamic gagal | `audio/tts_cartesia.py` | edge-tts fallback |
| AUDIO_DEVICE_FAIL | Suara tidak masuk OBS | `audio/player.py` | switch output device, show text overlay |
| GUARDRAIL_BLOCK | Komentar tidak dijawab | `guardrails/text_filter.py` | log reason, no action |
| BUDGET_LIMIT | LLM stop otomatis | `orchestrator/budget_guard.py` | pregen audio only |
| QUEUE_OVERFLOW | Audio telat / menumpuk | `audio/audio_queue.py` | drop idle, keep high priority |

---

## 11 · Health Check Command

### Command wajib di dashboard

```
test_tiktok_listener
test_obs_connection
test_audio_output
test_cartesia_key_pool
test_edge_tts
test_llm_key_pool
test_guardrail
test_overlay_write
test_full_pipeline_dry_run
```

### Full pipeline dry run

```
Dummy comment
→ classify
→ decision
→ generate reply
→ validate guardrail
→ synth TTS
→ queue audio
→ write overlay
→ no TikTok live required
```

Acceptance:

- [ ] semua command punya status hijau / merah

- [ ] error punya reason jelas

- [ ] dashboard tahu file pertama yang harus dicek

---

## 12 · Telemetry dan Audit

Log JSON per event:

```json
{
  "ts": 1770000000,
  "session_id": "live_2026_04_23_a",
  "event": "decision",
  "user": "Rina",
  "intent": "compatibility",
  "action": "suggest_reply",
  "needs_llm": true,
  "tokens_est": 180,
  "guardrail": "pass",
  "latency_ms": 1430
}
```

Wajib dicatat:

- komentar masuk

- keputusan action

- alasan skip

- LLM key dipakai

- token estimasi

- audio diputar

- scene aktif

- error code

- latency

---

## 13 · Implementation Phases

### Phase 1 — Manual Cockpit

- [ ] scan audio library

- [ ] play/pause/skip audio dari Svelte

- [ ] timer 2 jam

- [ ] current product / segment

- [ ] OBS scene switch manual

### Phase 2 — Comment Inbox

- [ ] TikTokLive comment masuk dashboard

- [ ] rule-based classifier

- [ ] skip spam/link/nomor

- [ ] overlay last comment

### Phase 3 — AI Suggested Reply

- [ ] klik komentar → generate reply

- [ ] guardrail output

- [ ] approve → TTS → audio queue

- [ ] no auto voice dulu

### Phase 4 — Semi-Auto Co-host

- [ ] auto reply untuk kategori aman

- [ ] manual approval untuk harga/komplain/teknis

- [ ] token budget gate

- [ ] LLM key round-robin

### Phase 5 — Orchestrator Flow

- [ ] scheduler pilih idle clip

- [ ] auto reset viewer baru

- [ ] auto scene sesuai produk

- [ ] closing otomatis 2 jam

### Phase 6 — Autonomous Safe Mode

- [ ] AI boleh memilih segmen berikutnya

- [ ] AI boleh menyarankan produk berikutnya

- [ ] semua tetap dibatasi guardrail, budget, dan emergency stop

---

## 14 · Definition of Done MVP

MVP dianggap siap test 30 menit jika:

- [ ] audio pregen bisa diputar dari dashboard

- [ ] komentar real masuk dashboard

- [ ] 1 komentar bisa dijawab voice dengan approve manual

- [ ] overlay last comment / last reply update

- [ ] OBS scene bisa diganti dari dashboard

- [ ] health check utama hijau

- [ ] LLM budget limit aktif

- [ ] spam/link/nomor tidak masuk LLM

- [ ] emergency stop bekerja

> ✅ **Bottom line**: bangun ini sebagai **semi-autonomous live control system**, bukan bot liar. Hemat token dengan pregen audio, classifier murah, cache, dan LLM hanya untuk komentar bernilai. Dashboard Svelte menjadi cockpit realtime; Python worker menjadi orchestrator; guardrail dan health check harus dibuat lebih dulu sebelum mode autonomous.

---
*Sync otomatis dari Notion. Jangan edit manual.*