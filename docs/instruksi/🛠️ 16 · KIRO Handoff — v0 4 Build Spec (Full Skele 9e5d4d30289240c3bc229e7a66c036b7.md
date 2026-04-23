# 🛠️ 16 · KIRO Handoff — v0.4 Build Spec (Full Skeleton)

> 📌 **Cara pakai**: local agent (Cursor/Claude Code/Windsurf/Copilot) baca halaman ini top-down, implement file demi file sesuai urutan P0 → P3. Setiap file punya: path, skeleton code, kontrak, dan acceptance.
> 

> 
> 

> **Jangan skip fase.** P0 harus hijau sebelum P1. P1 harus hijau sebelum P2. Dst.
> 

## 0 · Manifest file (31 file total)

| # | Path | Fase | Status | 1 | apps/worker/pyproject.toml | P0 | MODIFY |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | apps/worker/config/clips_script.yaml | P0 | NEW | 3 | apps/worker/config/products.yaml | P3 | NEW |
| 4 | apps/worker/config/reply_templates.yaml | P1 | NEW | 5 | apps/worker/src/banghack/core/audio_library/**init**.py | P0 | NEW |
| 6 | apps/worker/src/banghack/core/audio_library/[manager.py](http://manager.py) | P0 | NEW | 7 | apps/worker/src/banghack/adapters/audio_[library.py](http://library.py) | P0 | NEW |
| 8 | apps/worker/src/banghack/core/classifier/**init**.py | P1 | NEW | 9 | apps/worker/src/banghack/core/classifier/[rules.py](http://rules.py) | P1 | NEW |
| 10 | apps/worker/src/banghack/core/classifier/llm_[fallback.py](http://fallback.py) | P1 | NEW | 11 | apps/worker/src/banghack/core/orchestrator/**init**.py | P2 | NEW |
| 12 | apps/worker/src/banghack/core/orchestrator/[suggester.py](http://suggester.py) | P2 | NEW | 13 | apps/worker/src/banghack/core/orchestrator/reply_[cache.py](http://cache.py) | P2 | NEW |
| 14 | apps/worker/src/banghack/core/orchestrator/budget_[guard.py](http://guard.py) | P2 | NEW | 15 | apps/worker/src/banghack/core/orchestrator/[director.py](http://director.py) | P3 | NEW |
| 16 | apps/worker/src/banghack/[main.py](http://main.py) | P0-P3 | MODIFY | 17 | scripts/gen_audio_[library.py](http://library.py) | P0 | NEW |
| 18 | scripts/gen_audio_library.bat | P0 | NEW | 19 | apps/controller/src/lib/components/AudioLibraryGrid.svelte | P0 | NEW |
| 20 | apps/controller/src/lib/components/DecisionStream.svelte | P1 | NEW | 21 | apps/controller/src/lib/components/ReplySuggestions.svelte | P2 | NEW |
| 22 | apps/controller/src/lib/components/TwoHourTimer.svelte | P3 | NEW | 23 | apps/controller/src/lib/components/EmergencyStop.svelte | P3 | NEW |
| 24 | apps/controller/src/lib/stores/live_state.ts | P3 | NEW | 25 | apps/controller/src/lib/stores/audio_library.ts | P0 | NEW |
| 26 | apps/controller/src/lib/stores/decisions.ts | P1 | NEW | 27 | apps/worker/tests/test_audio_[library.py](http://library.py) | P0 | NEW |
| 28 | apps/worker/tests/test_classifier_[rules.py](http://rules.py) | P1 | NEW | 29 | apps/worker/tests/test_reply_[cache.py](http://cache.py) | P2 | NEW |
| 30 | apps/worker/tests/test_director_[state.py](http://state.py) | P3 | NEW | 31 | .env.example | P0 | MODIFY |

## 1 · Dependencies (pyproject.toml delta)

Tambahkan ke `apps/worker/pyproject.toml` bagian `[project.dependencies]`:

```toml
"pyyaml>=6.0.1",
"rapidfuzz>=3.9.0",
"aiofiles>=24.1.0",
```

`.env.example` tambahkan:

```
AUDIO_LIBRARY_DIR=apps/worker/static/audio_library
CLIPS_SCRIPT_YAML=apps/worker/config/clips_script.yaml
PRODUCTS_YAML=apps/worker/config/products.yaml
REPLY_TEMPLATES_YAML=apps/worker/config/reply_templates.yaml
LIVE_MAX_DURATION_S=7200
REPLY_CACHE_TTL_S=300
REPLY_CACHE_SIMILARITY=0.90
CLASSIFIER_LLM_THRESHOLD=0.80
```

---

# 🔵 P0 · Audio Library (CC-LIVE-CLIP-001..005)

**Tujuan**: 160 clip Cartesia ter-generate offline, ter-index, dan bisa di-play dari dashboard <200ms tanpa LLM call.

## P0.1 · `apps/worker/config/clips_script.yaml`

Berisi 160 entry script audio. Full struktur ada di `docs/LIVE_PLAN.md` §7. Format:

- Full schema + 5 sample entry per kategori
    
    ```yaml
    meta:
      version: "0.4.0"
      total_target: 160
      voice_id_default: "a167e0f3-df7e-4d52-a9c3-f949145efdab"
      model: "sonic-3"
      language: "id"
      categories:
        - A_opening
        - B_reset_viewer
        - C_paloma_context
        - D_cctv_context
        - E_senter_context
        - F_tracker_context
        - G_question_hooks
        - H_price_safe
        - I_trust_safety
        - J_idle_human
        - K_closing
    
    clips:
      - id: A_opening_001
        category: A_opening
        text: "Halo, saya mulai pelan-pelan dulu ya. Live ini bahas keamanan rumah malam hari."
        duration_target_s: 8
        tags: [opening, warm]
      - id: A_opening_002
        category: A_opening
        text: "Kalau baru masuk, santai aja. Ini bukan live yang maksa beli."
        duration_target_s: 7
        tags: [opening, low_pressure]
    
      # === PALOMA (target 35) ===
      - id: C_paloma_001
        category: C_paloma_context
        text: "Kita mulai dari pintu dulu. Buat saya, pintu depan itu titik pertama yang harus diberesin."
        duration_target_s: 9
        tags: [paloma, anchor]
        product: PALOMA
    
      # === CCTV (target 30) ===
      - id: D_cctv_001
        category: D_cctv_context
        text: "Setelah pintu, area kedua yang sering dilupakan itu teras."
        duration_target_s: 8
        product: CCTV_V380
    
      # === Question hooks (target 25) ===
      - id: G_question_001
        category: G_question_hooks
        text: "Di rumah kamu yang paling sering bikin khawatir apa: pintu, teras, atau mati lampu?"
        duration_target_s: 10
        tags: [hook, interaction]
    
      # ... (lanjutkan hingga 160 clip, reference full text di docs/LIVE_PLAN.md §8-17)
    ```
    
    **Acceptance**: 160 entry dengan distribusi: A=10, B=20, C=35, D=30, E=25, F=20, G=25, H=15, I=15, J=20, K=10. **Catatan**: target total 225, boleh reduced ke 160 dengan prioritas A+B+C+D+G+K = 120 wajib, sisanya opsional.
    

## P0.2 · `scripts/gen_audio_library.py`

Generator offline: baca YAML, panggil Cartesia API pool round-robin, simpan `.wav`, update `index.json`.

- Full skeleton (~180 lines)
    
    ```python
    #!/usr/bin/env python
    """Generate audio library offline dari clips_script.yaml.
    
    Usage:
        uv run python scripts/gen_audio_library.py [--category A_opening] [--force]
    """
    from __future__ import annotations
    
    import argparse
    import asyncio
    import hashlib
    import json
    import os
    import sys
    import time
    from dataclasses import dataclass, asdict
    from pathlib import Path
    
    import yaml
    from cartesia import AsyncCartesia
    from dotenv import load_dotenv
    
    load_dotenv()
    
    ROOT = Path(__file__).resolve().parents[1]
    YAML_PATH = Path(os.getenv("CLIPS_SCRIPT_YAML", ROOT / "apps/worker/config/clips_script.yaml"))
    OUT_DIR = Path(os.getenv("AUDIO_LIBRARY_DIR", ROOT / "apps/worker/static/audio_library"))
    INDEX_PATH = OUT_DIR / "index.json"
    
    @dataclass
    class KeySlot:
        key: str
        calls: int = 0
        errors: int = 0
        cooldown_until: float = 0.0
    
        def available(self) -> bool:
            return time.time() >= self.cooldown_until
    
    class CartesiaPool:
        def __init__(self, keys: list[str]):
            if not keys:
                raise RuntimeError("CARTESIA_API_KEYS empty")
            self.slots = [KeySlot(k.strip()) for k in keys if k.strip()]
            self.idx = 0
    
        def acquire(self) -> KeySlot:
            for _ in range(len(self.slots)):
                slot = self.slots[self.idx]
                self.idx = (self.idx + 1) % len(self.slots)
                if slot.available():
                    slot.calls += 1
                    return slot
            raise RuntimeError("no cartesia key available")
    
        def mark_error(self, slot: KeySlot, cooldown_s: int = 60) -> None:
            slot.errors += 1
            slot.cooldown_until = time.time() + cooldown_s
    
    def clip_hash(text: str, voice_id: str, model: str) -> str:
        blob = f"{text}|{voice_id}|{model}".encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:16]
    
    async def synth_one(client: AsyncCartesia, text: str, voice_id: str, model: str) -> bytes:
        # adaptasi sesuai SDK cartesia >=2.0.0 — endpoint /tts/bytes
        chunks: list[bytes] = []
        async for chunk in client.tts.bytes(
            model_id=model,
            transcript=text,
            voice={"mode": "id", "id": voice_id},
            output_format={"container": "wav", "encoding": "pcm_s16le", "sample_rate": 44100},
            language="id",
        ):
            chunks.append(chunk)
        return b"".join(chunks)
    
    async def run(category_filter: str | None, force: bool) -> None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        spec = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
        voice_id = spec["meta"]["voice_id_default"]
        model = spec["meta"]["model"]
    
        keys = [k for k in os.getenv("CARTESIA_API_KEYS", "").split(",") if k.strip()]
        pool = CartesiaPool(keys)
    
        index: dict = {"version": spec["meta"]["version"], "clips": []}
        if INDEX_PATH.exists():
            try:
                index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        existing = {c["id"]: c for c in index.get("clips", [])}
    
        to_gen = [c for c in spec["clips"]
                  if (not category_filter or c["category"] == category_filter)
                  and (force or c["id"] not in existing)]
    
        print(f"[gen] {len(to_gen)} clip akan di-generate")
    
        ok, fail = 0, 0
        for i, clip in enumerate(to_gen):
            h = clip_hash(clip["text"], voice_id, model)
            out_file = OUT_DIR / f"{clip['id']}__{h}.wav"
            if out_file.exists() and not force:
                continue
            slot = pool.acquire()
            client = AsyncCartesia(api_key=slot.key)
            try:
                audio = await synth_one(client, clip["text"], voice_id, model)
                out_file.write_bytes(audio)
                existing[clip["id"]] = {
                    "id": clip["id"],
                    "category": clip["category"],
                    "text": clip["text"],
                    "tags": clip.get("tags", []),
                    "product": clip.get("product"),
                    "file": out_file.name,
                    "hash": h,
                    "bytes": len(audio),
                    "voice_id": voice_id,
                    "model": model,
                    "generated_at": int(time.time()),
                }
                ok += 1
                print(f"  [{i+1}/{len(to_gen)}] OK {clip['id']}")
            except Exception as e:
                pool.mark_error(slot)
                fail += 1
                print(f"  [{i+1}/{len(to_gen)}] FAIL {clip['id']}: {e}")
            finally:
                await client.close()
            await asyncio.sleep(0.2)  # gentle rate
    
        index["clips"] = list(existing.values())
        index["updated_at"] = int(time.time())
        INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[done] ok={ok} fail={fail} total={len(index['clips'])}")
    
    if __name__ == "__main__":
        ap = argparse.ArgumentParser()
        ap.add_argument("--category", default=None)
        ap.add_argument("--force", action="store_true")
        args = ap.parse_args()
        asyncio.run(run(args.category, args.force))
    ```
    
    **Local agent fix-up**:
    
    - Verifikasi signature `AsyncCartesia` sesuai SDK v2.0.0 (method name, output_format schema).
    - Tambah retry 3x dengan exponential backoff untuk error transient.
    - Optional: tambah progress bar via `tqdm`.

## P0.3 · `scripts/gen_audio_library.bat`

```
@echo off
cd /d %~dp0..
call uv run python scripts/gen_audio_library.py %*
```

## P0.4 · `apps/worker/src/banghack/core/audio_library/manager.py`

Runtime loader — baca `index.json`, expose query API.

- Full skeleton (~120 lines)
    
    ```python
    """Audio library manager — baca index.json, query by category/product/id."""
    from __future__ import annotations
    
    import json
    import logging
    import os
    from dataclasses import dataclass, field
    from pathlib import Path
    from typing import Iterable
    
    log = logging.getLogger(__name__)
    
    @dataclass(frozen=True)
    class Clip:
        id: str
        category: str
        text: str
        file: str           # filename relatif ke AUDIO_LIBRARY_DIR
        tags: tuple[str, ...] = ()
        product: str | None = None
        bytes_: int = 0
    
        @property
        def filename(self) -> str:
            return self.file
    
    @dataclass
    class LibraryStats:
        total: int
        by_category: dict[str, int]
        by_product: dict[str, int]
    
    class AudioLibraryManager:
        def __init__(self, index_path: Path | None = None, audio_dir: Path | None = None):
            self.audio_dir = audio_dir or Path(os.getenv("AUDIO_LIBRARY_DIR", "apps/worker/static/audio_library"))
            self.index_path = index_path or (self.audio_dir / "index.json")
            self._clips: dict[str, Clip] = {}
            self._last_played_ts: dict[str, float] = {}  # id -> timestamp
    
        def load(self) -> int:
            if not self.index_path.exists():
                log.warning("index.json missing at %s", self.index_path)
                return 0
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
            self._clips.clear()
            for c in data.get("clips", []):
                clip = Clip(
                    id=c["id"],
                    category=c["category"],
                    text=c["text"],
                    file=c["file"],
                    tags=tuple(c.get("tags", [])),
                    product=c.get("product"),
                    bytes_=c.get("bytes", 0),
                )
                self._clips[clip.id] = clip
            log.info("audio library loaded: %d clips", len(self._clips))
            return len(self._clips)
    
        def get(self, clip_id: str) -> Clip | None:
            return self._clips.get(clip_id)
    
        def all(self) -> list[Clip]:
            return list(self._clips.values())
    
        def by_category(self, category: str) -> list[Clip]:
            return [c for c in self._clips.values() if c.category == category]
    
        def by_product(self, product: str) -> list[Clip]:
            return [c for c in self._clips.values() if c.product == product]
    
        def file_path(self, clip_id: str) -> Path | None:
            c = self.get(clip_id)
            if not c:
                return None
            return self.audio_dir / c.file
    
        def stats(self) -> LibraryStats:
            by_cat: dict[str, int] = {}
            by_prod: dict[str, int] = {}
            for c in self._clips.values():
                by_cat[c.category] = by_cat.get(c.category, 0) + 1
                if c.product:
                    by_prod[c.product] = by_prod.get(c.product, 0) + 1
            return LibraryStats(total=len(self._clips), by_category=by_cat, by_product=by_prod)
    
        def mark_played(self, clip_id: str, ts: float) -> None:
            self._last_played_ts[clip_id] = ts
    
        def not_played_since(self, clip_id: str, now: float, window_s: int = 1200) -> bool:
            """Aturan anti-repeat 20 menit dari LIVE_PLAN §19."""
            last = self._last_played_ts.get(clip_id, 0.0)
            return (now - last) >= window_s
    ```
    

## P0.5 · `apps/worker/src/banghack/adapters/audio_library.py`

Adapter player: ambil Clip → pipe ke `ffplay` subprocess (existing pattern) → route ke VB-CABLE.

- Skeleton (~90 lines)
    
    ```python
    """Audio library playback adapter.
    
    Pakai ffplay subprocess (existing convention dari v0.3 tts adapter).
    Route output ke VB-CABLE via Windows audio device selection.
    """
    from __future__ import annotations
    
    import asyncio
    import logging
    import os
    import subprocess
    from pathlib import Path
    
    from banghack.core.audio_library.manager import AudioLibraryManager, Clip
    
    log = logging.getLogger(__name__)
    
    class AudioLibraryPlayer:
        def __init__(self, manager: AudioLibraryManager):
            self.manager = manager
            self._current: asyncio.subprocess.Process | None = None
            self._current_clip_id: str | None = None
            self._lock = asyncio.Lock()
    
        async def play(self, clip_id: str) -> dict:
            async with self._lock:
                clip = self.manager.get(clip_id)
                if not clip:
                    return {"ok": False, "error": f"clip not found: {clip_id}"}
                path = self.manager.file_path(clip_id)
                if not path or not path.exists():
                    return {"ok": False, "error": f"file missing: {clip.file}"}
                await self._stop_internal()
                cmd = [
                    "ffplay", "-nodisp", "-autoexit", "-loglevel", "error",
                    str(path),
                ]
                # optional: audio device flag untuk VB-CABLE
                device = os.getenv("AUDIO_OUTPUT_DEVICE")
                if device:
                    cmd.extend(["-audio_device_index", device])
                self._current = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                self._current_clip_id = clip_id
                self.manager.mark_played(clip_id, asyncio.get_event_loop().time())
                return {"ok": True, "clip_id": clip_id, "pid": self._current.pid}
    
        async def stop(self) -> dict:
            async with self._lock:
                await self._stop_internal()
                return {"ok": True}
    
        async def _stop_internal(self) -> None:
            if self._current and self._current.returncode is None:
                try:
                    self._current.terminate()
                    await asyncio.wait_for(self._current.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    self._current.kill()
                    await self._current.wait()
            self._current = None
            self._current_clip_id = None
    
        def current(self) -> str | None:
            return self._current_clip_id
    ```
    

## P0.6 · WS commands (tambah ke `main.py`)

Append handler-handler ini ke existing WS dispatcher:

```python
# audio.list → return index
{ "type": "audio.list" }
# response
{ "type": "audio.list.ok", "clips": [...], "stats": {...} }

# audio.play
{ "type": "audio.play", "clip_id": "C_paloma_001" }
# response
{ "type": "audio.play.ok", "clip_id": "...", "pid": 1234 }

# audio.stop
{ "type": "audio.stop" }
# response
{ "type": "audio.stop.ok" }

# audio.now (broadcast setiap mulai play)
{ "type": "audio.now", "clip_id": "...", "category": "...", "text": "..." }
```

## P0.7 · `apps/controller/src/lib/stores/audio_library.ts`

```tsx
import { writable, derived } from 'svelte/store';

export interface Clip {
  id: string;
  category: string;
  text: string;
  file: string;
  product?: string;
  tags: string[];
}

export const clips = writable<Clip[]>([]);
export const currentClipId = writable<string | null>(null);
export const filterCategory = writable<string>('ALL');

export const filteredClips = derived(
  [clips, filterCategory],
  ([$clips, $cat]) => $cat === 'ALL' ? $clips : $clips.filter(c => c.category === $cat)
);
```

## P0.8 · `apps/controller/src/lib/components/AudioLibraryGrid.svelte`

- Svelte 5 runes skeleton
    
    ```
    <script lang="ts">
      import { clips, currentClipId, filterCategory, filteredClips } from '$lib/stores/audio_library';
      import { sendCommand } from '$lib/api/ws';
    
      let search = $state('');
      const CATS = ['ALL','A_opening','B_reset_viewer','C_paloma_context','D_cctv_context','E_senter_context','F_tracker_context','G_question_hooks','H_price_safe','I_trust_safety','J_idle_human','K_closing'];
    
      const visible = $derived($filteredClips.filter(c =>
        !search || c.text.toLowerCase().includes(search.toLowerCase()) || c.id.toLowerCase().includes(search.toLowerCase())
      ));
    
      function play(id: string) { sendCommand({ type: 'audio.play', clip_id: id }); }
      function stop() { sendCommand({ type: 'audio.stop' }); }
    </script>
    
    <div class="flex gap-2 mb-4">
      <input bind:value={search} placeholder="cari..." class="border rounded px-2 py-1 flex-1" />
      <select bind:value={$filterCategory} class="border rounded px-2 py-1">
        {#each CATS as c}<option>{c}</option>{/each}
      </select>
      <button on:click={stop} class="bg-red-500 text-white px-3 py-1 rounded">⏹ Stop</button>
    </div>
    
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-[600px] overflow-auto">
      {#each visible as c (c.id)}
        <button
          on:click={() => play(c.id)}
          class="text-left border rounded p-2 hover:bg-blue-50 {$currentClipId === c.id ? 'bg-blue-100 ring-2 ring-blue-500' : ''}">
          <div class="text-xs font-mono text-gray-500">{c.id}</div>
          <div class="text-sm line-clamp-3">{c.text}</div>
          {#if c.product}<div class="text-xs text-blue-600 mt-1">🏷 {c.product}</div>{/if}
        </button>
      {/each}
    </div>
    ```
    

## P0.9 · Test `apps/worker/tests/test_audio_library.py`

```python
import json
import pytest
from pathlib import Path
from banghack.core.audio_library.manager import AudioLibraryManager

def test_load_empty(tmp_path):
    mgr = AudioLibraryManager(index_path=tmp_path / "missing.json", audio_dir=tmp_path)
    assert mgr.load() == 0

def test_load_index(tmp_path):
    idx = {"clips": [
        {"id": "A_opening_001", "category": "A_opening", "text": "halo", "file": "a.wav"},
        {"id": "C_paloma_001", "category": "C_paloma_context", "text": "pintu", "file": "c.wav", "product": "PALOMA"},
    ]}
    (tmp_path / "index.json").write_text(json.dumps(idx))
    mgr = AudioLibraryManager(index_path=tmp_path / "index.json", audio_dir=tmp_path)
    assert mgr.load() == 2
    assert len(mgr.by_category("A_opening")) == 1
    assert len(mgr.by_product("PALOMA")) == 1

def test_anti_repeat(tmp_path):
    mgr = AudioLibraryManager(index_path=tmp_path / "i.json", audio_dir=tmp_path)
    mgr._clips = {"x": object()}  # type: ignore
    mgr.mark_played("x", 1000.0)
    assert not mgr.not_played_since("x", 1500.0, window_s=1200)
    assert mgr.not_played_since("x", 3000.0, window_s=1200)
```

## P0 · Acceptance

- [ ]  `uv run python scripts/gen_audio_library.py --category A_opening` generate minimal 10 file `.wav` valid
- [ ]  `index.json` ter-update, tiap clip punya field `id`, `file`, `hash`, `category`, `text`
- [ ]  `pytest apps/worker/tests/test_audio_library.py` hijau
- [ ]  Dashboard load semua clip via `audio.list`, tombol play suara keluar <200ms di VB-CABLE
- [ ]  0 LLM call saat play clip (cek metrics)
- [ ]  Total size audio library <20MB

---

# 🟢 P1 · Comment Classifier (CC-LIVE-CLASSIFIER-001..004)

**Tujuan**: 80%+ comment ter-klasifikasi via regex rules, hanya sisanya ke LLM fallback.

## P1.1 · `apps/worker/config/reply_templates.yaml`

- Template per intent
    
    ```yaml
    greeting:
      - "Halo! Selamat datang. Lagi bahas rumah aman malam hari."
      - "Hai, santai aja. Ini bukan live yang maksa beli."
    
    price_question:
      - "Untuk harga saya tidak sebut angka pasti, cek yang muncul di keranjang kuning ya."
      - "Harga bisa berubah tergantung promo. Coba cek di keranjang kuning."
    
    forbidden_link:
      - null  # skip, jangan jawab
    
    forbidden_contact:
      - null
    
    spam:
      - null
    
    # yang butuh LLM:
    product_question:
      - _needs_llm: true
    
    compatibility:
      - _needs_llm: true
    
    buying_intent:
      - _needs_llm: true
      - _priority: 80
    ```
    

## P1.2 · `apps/worker/src/banghack/core/classifier/rules.py`

- 7 intent rules + unit-testable
    
    ```python
    """Rule-based comment classifier.
    
    Target: 80%+ comment ter-klasifikasi tanpa LLM.
    7 intents: greeting, price_question, forbidden_link, forbidden_contact,
               spam, buying_intent, product_question.
    Return (intent, confidence, reason). Confidence <0.8 → go LLM fallback.
    """
    from __future__ import annotations
    
    import re
    from dataclasses import dataclass
    
    # URL / link detector
    _LINK_RX = re.compile(r"(https?://|www\.|\.com|\.id|\.co|bit\.ly|\.tk)", re.I)
    # WA / phone / social
    _CONTACT_RX = re.compile(r"(wa\s*[:.]?\s*\d|whatsapp|0\d{9,}|\+62\d{8,}|ig\s|instagram|telegram|shopee|tokopedia|lazada)", re.I)
    # SARA / forbidden
    _BLOCK_RX = re.compile(r"(ajak|ikut live|follow.*back|sub.*back|sub for sub|bokep|porn|judi|sabung)", re.I)
    
    # Greetings
    _GREET_RX = re.compile(r"^(halo|hai|hi|hallo|assalamualaikum|pagi|siang|sore|malam)\b", re.I)
    # Price
    _PRICE_RX = re.compile(r"(harga|berapa|brp|price|ongkir|diskon|promo|murah)", re.I)
    # Buying intent
    _BUY_RX = re.compile(r"(mau beli|mau order|tolong dm|checkout|saya ambil|saya beli|minat|gimana caranya pesan)", re.I)
    # Compatibility / product question (sebelum LLM)
    _COMPAT_HINT_RX = re.compile(r"(cocok|bisa buat|muat|pas|buat rumah|buat pintu|apakah|gimana kalo|kontrakan|kos)", re.I)
    _TECH_HINT_RX = re.compile(r"(baterai|instalasi|pasang|cas|charge|resolusi|wifi|aplikasi|cara)", re.I)
    
    @dataclass(frozen=True)
    class Intent:
        name: str
        confidence: float
        reason: str
        needs_llm: bool = False
        safe_to_skip: bool = False
    
    def classify(text: str) -> Intent:
        t = (text or "").strip().lower()
        if not t:
            return Intent("empty", 1.0, "empty", safe_to_skip=True)
    
        # hard blocks
        if _LINK_RX.search(t):
            return Intent("forbidden_link", 1.0, "contains url", safe_to_skip=True)
        if _CONTACT_RX.search(t):
            return Intent("forbidden_contact", 1.0, "phone/social", safe_to_skip=True)
        if _BLOCK_RX.search(t):
            return Intent("spam", 1.0, "spam pattern", safe_to_skip=True)
    
        # greetings
        if _GREET_RX.search(t) and len(t) < 40:
            return Intent("greeting", 0.95, "greeting pattern")
        # price
        if _PRICE_RX.search(t) and len(t) < 60:
            return Intent("price_question", 0.9, "price pattern")
        # buying intent
        if _BUY_RX.search(t):
            return Intent("buying_intent", 0.85, "buy pattern", needs_llm=True)
        # compatibility
        if _COMPAT_HINT_RX.search(t) or _TECH_HINT_RX.search(t):
            return Intent("compatibility", 0.7, "compat/tech hint", needs_llm=True)
    
        # low confidence — let LLM fallback decide
        return Intent("unknown", 0.3, "no rule match", needs_llm=True)
    ```
    

## P1.3 · `apps/worker/src/banghack/core/classifier/llm_fallback.py`

- LLM fallback dengan prompt pendek + timeout
    
    ```python
    """LLM fallback classifier — dipanggil hanya saat rule confidence <threshold.
    
    Prompt pendek, max 80 tokens output, 3s timeout.
    """
    from __future__ import annotations
    
    import json
    import logging
    import os
    from typing import Any
    
    from banghack.adapters.llm import LLMRouter  # existing v0.3
    from banghack.core.classifier.rules import Intent
    
    log = logging.getLogger(__name__)
    
    PROMPT = """Klasifikasikan komentar TikTok Live ini ke SALAH SATU kategori:
    - product_question (tanya fitur, spek, cara pakai)
    - compatibility (tanya cocok/tidak untuk kasus spesifik)
    - buying_intent (niat beli)
    - complaint (keluhan produk/layanan)
    - small_talk (basa-basi, curhat ringan)
    - skip (tidak layak dijawab)
    
    Komentar: {text}
    
    Jawab HANYA JSON: "intent":"...","confidence":0.0-1.0,"reason":"singkat""""
    
    async def classify_with_llm(text: str, router: LLMRouter) -> Intent:
        try:
            resp = await router.complete(
                prompt=PROMPT.format(text=text),
                max_tokens=80,
                timeout_s=3.0,
                temperature=0.0,
            )
            data: dict[str, Any] = json.loads(resp.strip())
            return Intent(
                name=data.get("intent", "unknown"),
                confidence=float(data.get("confidence", 0.5)),
                reason=f"llm: {data.get('reason', '')}",
                needs_llm=False,  # already classified
                safe_to_skip=data.get("intent") == "skip",
            )
        except Exception as e:
            log.warning("llm classifier failed: %s", e)
            return Intent("unknown", 0.3, f"llm error: {e}", safe_to_skip=False)
    ```
    
    **Local agent fix-up**: sesuaikan signature `LLMRouter.complete(...)` dengan yang di `adapters/llm.py` v0.3.
    

## P1.4 · Integration di `main.py`

Alur saat comment masuk:

```python
from banghack.core.classifier.rules import classify
from banghack.core.classifier.llm_fallback import classify_with_llm

THRESHOLD = float(os.getenv("CLASSIFIER_LLM_THRESHOLD", "0.8"))

async def handle_comment(ev):
    intent = classify(ev.text)
    if intent.confidence < THRESHOLD and intent.needs_llm:
        intent = await classify_with_llm(ev.text, llm_router)

    await ws_broadcast({
        "type": "comment",
        "user": ev.user,
        "text": ev.text,
        "intent": intent.name,
        "confidence": intent.confidence,
        "reason": intent.reason,
    })
    if intent.safe_to_skip:
        return
    # P2 → suggester
    await suggester.handle(ev, intent)
```

## P1.5 · `apps/controller/src/lib/components/DecisionStream.svelte`

Live feed comment dengan badge intent:

- Skeleton
    
    ```
    <script lang="ts">
      import { decisions } from '$lib/stores/decisions';
      const BADGE: Record<string, string> = {
        greeting: 'bg-gray-200',
        price_question: 'bg-yellow-200',
        buying_intent: 'bg-green-300',
        compatibility: 'bg-blue-200',
        product_question: 'bg-blue-200',
        forbidden_link: 'bg-red-300',
        forbidden_contact: 'bg-red-300',
        spam: 'bg-red-200',
        unknown: 'bg-gray-100',
      };
    </script>
    
    <div class="space-y-1 max-h-[500px] overflow-auto font-mono text-xs">
      {#each $decisions as d (d.id)}
        <div class="flex gap-2 items-start border-b py-1">
          <span class="px-2 py-0.5 rounded {BADGE[d.intent] || 'bg-gray-100'}">{d.intent}</span>
          <span class="text-gray-500">@{d.user}</span>
          <span class="flex-1">{d.text}</span>
          <span class="text-gray-400">{(d.confidence*100).toFixed(0)}%</span>
        </div>
      {/each}
    </div>
    ```
    

## P1.6 · Test `test_classifier_rules.py`

```python
import pytest
from banghack.core.classifier.rules import classify

@pytest.mark.parametrize("text,expected", [
    ("halo", "greeting"),
    ("berapa harganya?", "price_question"),
    ("wa dong", "forbidden_contact"),
    ("cek https://bit.ly/x", "forbidden_link"),
    ("mau beli yang paloma", "buying_intent"),
    ("bisa buat pintu kontrakan?", "compatibility"),
    ("", "empty"),
])
def test_rules(text, expected):
    assert classify(text).name == expected
```

## P1 · Acceptance

- [ ]  `pytest test_classifier_rules.py` hijau (7+ case)
- [ ]  Dari 100 comment dummy, ≥80 ter-klasifikasi oleh rules (confidence ≥0.8) tanpa LLM call
- [ ]  Badge intent muncul di DecisionStream real-time
- [ ]  `forbidden_*` dan `spam` TIDAK pernah masuk ke suggester/LLM

---

# 🟡 P2 · Suggested Reply (CC-LIVE-ORCH-001..005)

**Tujuan**: comment valuable dapat 3-opsi reply, operator approve, voice keluar via Cartesia dynamic TTS (existing v0.3).

## P2.1 · `apps/worker/src/banghack/core/orchestrator/budget_guard.py`

- Token + IDR budget gate
    
    ```python
    """Budget guard — stop LLM kalau hit batas harian."""
    from __future__ import annotations
    
    import os
    import time
    from dataclasses import dataclass, field
    
    IDR_PER_1K_TOKENS = {
        "deepseek-chat": 3.0,
        "claude-3-haiku": 15.0,
        "9router/auto": 1.0,  # estimate
    }
    
    @dataclass
    class BudgetState:
        day: str
        tokens_in: int = 0
        tokens_out: int = 0
        idr_spent: float = 0.0
        llm_calls: int = 0
    
        @property
        def key(self) -> str:
            return self.day
    
    class BudgetGuard:
        def __init__(self):
            self.daily_limit_idr = float(os.getenv("BUDGET_IDR_DAILY", "50000"))
            self.state = BudgetState(day=time.strftime("%Y-%m-%d"))
            self._last_llm_ts = 0.0
            self._min_interval_s = float(os.getenv("LLM_MIN_INTERVAL_S", "8"))
    
        def _rollover(self):
            today = time.strftime("%Y-%m-%d")
            if today != self.state.day:
                self.state = BudgetState(day=today)
    
        def can_call(self) -> tuple[bool, str]:
            self._rollover()
            if self.state.idr_spent >= self.daily_limit_idr:
                return False, f"daily budget hit: {self.state.idr_spent:.0f}/{self.daily_limit_idr:.0f} IDR"
            if (time.time() - self._last_llm_ts) < self._min_interval_s:
                return False, f"rate limit: {self._min_interval_s}s min interval"
            return True, "ok"
    
        def record(self, model: str, tokens_in: int, tokens_out: int) -> None:
            self._rollover()
            price = IDR_PER_1K_TOKENS.get(model, 10.0)
            cost = (tokens_in + tokens_out) / 1000.0 * price
            self.state.tokens_in += tokens_in
            self.state.tokens_out += tokens_out
            self.state.idr_spent += cost
            self.state.llm_calls += 1
            self._last_llm_ts = time.time()
    
        def snapshot(self) -> dict:
            return {
                "day": self.state.day,
                "tokens_in": self.state.tokens_in,
                "tokens_out": self.state.tokens_out,
                "idr_spent": round(self.state.idr_spent, 2),
                "idr_limit": self.daily_limit_idr,
                "llm_calls": self.state.llm_calls,
                "remaining_pct": max(0.0, 100.0 - (self.state.idr_spent / self.daily_limit_idr * 100)),
            }
    ```
    

## P2.2 · `apps/worker/src/banghack/core/orchestrator/reply_cache.py`

- Cache mirip-comment pakai rapidfuzz
    
    ```python
    """Reply cache — hindari LLM call berulang untuk comment mirip.
    
    Use rapidfuzz untuk similarity (token_set_ratio). TTL default 5 menit.
    """
    from __future__ import annotations
    
    import os
    import time
    from dataclasses import dataclass
    from collections import deque
    
    from rapidfuzz import fuzz
    
    @dataclass
    class CachedReply:
        text_norm: str
        replies: list[str]
        intent: str
        created_at: float
    
    class ReplyCache:
        def __init__(self):
            self.ttl = int(os.getenv("REPLY_CACHE_TTL_S", "300"))
            self.threshold = int(float(os.getenv("REPLY_CACHE_SIMILARITY", "0.90")) * 100)
            self.store: deque[CachedReply] = deque(maxlen=500)
    
        @staticmethod
        def _norm(text: str) -> str:
            return " ".join(text.lower().split())
    
        def lookup(self, text: str, intent: str) -> list[str] | None:
            now = time.time()
            q = self._norm(text)
            for entry in self.store:
                if (now - entry.created_at) > self.ttl:
                    continue
                if entry.intent != intent:
                    continue
                score = fuzz.token_set_ratio(q, entry.text_norm)
                if score >= self.threshold:
                    return list(entry.replies)
            return None
    
        def put(self, text: str, intent: str, replies: list[str]) -> None:
            self.store.append(CachedReply(
                text_norm=self._norm(text),
                replies=list(replies),
                intent=intent,
                created_at=time.time(),
            ))
    
        def stats(self) -> dict:
            return {"size": len(self.store), "ttl": self.ttl, "threshold": self.threshold}
    ```
    

## P2.3 · `apps/worker/src/banghack/core/orchestrator/suggester.py`

- 3-option reply generator + guardrail
    
    ```python
    """Suggested reply generator.
    
    Flow:
      1. Cek cache — hit? return 3 opsi cached
      2. Cek budget_guard.can_call() — tidak? fallback template
      3. LLM → 3 variasi (singkat, sedang, hangat)
      4. Guardrail output (no link, no price, no contact)
      5. Cache result
      6. Emit ke WS untuk operator approve
    """
    from __future__ import annotations
    
    import asyncio
    import logging
    import re
    import uuid
    from dataclasses import dataclass, field
    
    from banghack.adapters.llm import LLMRouter
    from banghack.core.classifier.rules import Intent
    from banghack.core.orchestrator.budget_guard import BudgetGuard
    from banghack.core.orchestrator.reply_cache import ReplyCache
    
    log = logging.getLogger(__name__)
    
    OUTPUT_BLOCK_RX = re.compile(r"(https?://|www\.|wa\.me|whatsapp|\+62|0\d{10,}|rp\s*\d|ratusan ribu|juta\s)", re.I)
    
    PROMPT = """Kamu host TikTok Live affiliate, karakter tetangga santai yang suka ngoprek rumah.
    Komentar penonton: "{text}"
    Intent: {intent}
    Produk aktif: {product}
    
    Buat 3 variasi jawaban SINGKAT bahasa Indonesia natural (10-25 kata tiap variasi).
    Aturan:
    - Jangan sebut harga pasti, arahkan ke keranjang kuning jika perlu.
    - Jangan sebut link, WA, IG, Shopee, Tokopedia.
    - Jangan klaim mutlak (anti maling, anti rusak).
    - Sapa pelan kalau user disebut: Kak {user}.
    - Variasi 1 = singkat/padat, variasi 2 = sedang/informatif, variasi 3 = hangat/empatik.
    
    Format output JSON:
    "replies":["...","...","..."]"""
    
    @dataclass
    class Suggestion:
        suggestion_id: str
        user: str
        comment_id: str
        comment_text: str
        intent: str
        replies: list[str]
        source: str  # cache | llm | template
        priority: int = 50
    
    class Suggester:
        def __init__(self, llm: LLMRouter, cache: ReplyCache, budget: BudgetGuard, template_map: dict[str, list[str]]):
            self.llm = llm
            self.cache = cache
            self.budget = budget
            self.templates = template_map
    
        async def suggest(self, user: str, comment_id: str, text: str, intent: Intent, product: str) -> Suggestion | None:
            if intent.safe_to_skip:
                return None
    
            # 1. template lookup (e.g. greeting, price_question)
            tmpl = self.templates.get(intent.name)
            if tmpl and None not in tmpl and not intent.needs_llm:
                return Suggestion(
                    suggestion_id=str(uuid.uuid4())[:8],
                    user=user, comment_id=comment_id, comment_text=text,
                    intent=intent.name,
                    replies=tmpl[:3] or [tmpl[0]] * 3,
                    source="template",
                )
    
            # 2. cache lookup
            cached = self.cache.lookup(text, intent.name)
            if cached:
                return Suggestion(
                    suggestion_id=str(uuid.uuid4())[:8],
                    user=user, comment_id=comment_id, comment_text=text,
                    intent=intent.name, replies=cached, source="cache",
                )
    
            # 3. budget gate
            ok, reason = self.budget.can_call()
            if not ok:
                log.info("budget gate block: %s", reason)
                fallback = self.templates.get("_fallback", ["Makasih komentarnya, nanti saya bahas ya."])
                return Suggestion(
                    suggestion_id=str(uuid.uuid4())[:8],
                    user=user, comment_id=comment_id, comment_text=text,
                    intent=intent.name, replies=fallback[:3] or [fallback[0]]*3,
                    source="template",
                )
    
            # 4. LLM
            try:
                raw = await self.llm.complete(
                    prompt=PROMPT.format(text=text, intent=intent.name, product=product, user=user),
                    max_tokens=200,
                    timeout_s=5.0,
                    temperature=0.7,
                )
                import json as _json
                data = _json.loads(raw.strip())
                replies = [r for r in data.get("replies", []) if self._safe(r)][:3]
                if len(replies) < 3:
                    replies += ["Makasih ya."] * (3 - len(replies))
                self.budget.record("deepseek-chat", tokens_in=150, tokens_out=100)  # estimate
                self.cache.put(text, intent.name, replies)
                return Suggestion(
                    suggestion_id=str(uuid.uuid4())[:8],
                    user=user, comment_id=comment_id, comment_text=text,
                    intent=intent.name, replies=replies, source="llm",
                )
            except Exception as e:
                log.warning("llm suggest failed: %s", e)
                fb = ["Noted, nanti saya bahas di sesi berikutnya."] * 3
                return Suggestion(
                    suggestion_id=str(uuid.uuid4())[:8],
                    user=user, comment_id=comment_id, comment_text=text,
                    intent=intent.name, replies=fb, source="template",
                )
    
        @staticmethod
        def _safe(text: str) -> bool:
            return not OUTPUT_BLOCK_RX.search(text or "")
    ```
    

## P2.4 · WS commands (tambah di [main.py](http://main.py))

```python
# Worker broadcast saat suggestion siap
{ "type": "reply.suggestion",
  "suggestion_id": "abc123",
  "user": "Rina", "comment_id": "c_1",
  "comment_text": "bisa buat pintu kontrakan?",
  "replies": ["...", "...", "..."],
  "source": "llm" }

# Operator approve
{ "type": "reply.approve", "suggestion_id": "abc123", "variant": 1 }
# → worker: TTS Cartesia → audio queue → overlay update

# Operator reject
{ "type": "reply.reject", "suggestion_id": "abc123" }

# Regenerate
{ "type": "reply.regen", "suggestion_id": "abc123", "hint": "lebih pendek" }

# Budget snapshot
{ "type": "budget.get" }  → { "type": "budget.snapshot", ... }
```

## P2.5 · `apps/controller/src/lib/components/ReplySuggestions.svelte`

- 3-opsi card + approve
    
    ```
    <script lang="ts">
      import { suggestions } from '$lib/stores/decisions';
      import { sendCommand } from '$lib/api/ws';
      function approve(id: string, variant: number) { sendCommand({ type: 'reply.approve', suggestion_id: id, variant }); }
      function reject(id: string) { sendCommand({ type: 'reply.reject', suggestion_id: id }); }
      function regen(id: string, hint: string) { sendCommand({ type: 'reply.regen', suggestion_id: id, hint }); }
    </script>
    
    <div class="space-y-3">
      {#each $suggestions as s (s.suggestion_id)}
        <div class="border rounded p-3 bg-yellow-50">
          <div class="text-xs text-gray-600">@{s.user} · {s.intent} · via {s.source}</div>
          <div class="text-sm font-medium mb-2">"{s.comment_text}"</div>
          <div class="space-y-1">
            {#each s.replies as r, i}
              <div class="flex gap-2">
                <button on:click={() => approve(s.suggestion_id, i)} class="bg-green-500 text-white px-2 rounded text-xs">✓ {i+1}</button>
                <span class="text-sm flex-1">{r}</span>
              </div>
            {/each}
          </div>
          <div class="flex gap-1 mt-2">
            <button on:click={() => regen(s.suggestion_id, 'lebih pendek')} class="text-xs bg-blue-200 px-2 py-0.5 rounded">↻ pendek</button>
            <button on:click={() => regen(s.suggestion_id, 'lebih hangat')} class="text-xs bg-blue-200 px-2 py-0.5 rounded">↻ hangat</button>
            <button on:click={() => reject(s.suggestion_id)} class="text-xs bg-red-200 px-2 py-0.5 rounded ml-auto">✕ skip</button>
          </div>
        </div>
      {/each}
    </div>
    ```
    

## P2.6 · Test `test_reply_cache.py`

```python
from banghack.core.orchestrator.reply_cache import ReplyCache

def test_hit_similar():
    c = ReplyCache()
    c.put("bisa buat pintu kontrakan?", "compatibility", ["ya", "bisa", "cocok"])
    assert c.lookup("bisa buat pintu kontrakan", "compatibility") is not None

def test_miss_different_intent():
    c = ReplyCache()
    c.put("harga?", "price_question", ["x", "y", "z"])
    assert c.lookup("harga?", "compatibility") is None

def test_ttl(monkeypatch):
    import time
    c = ReplyCache()
    c.ttl = 1
    c.put("halo", "greeting", ["hi"])
    time.sleep(1.1)
    assert c.lookup("halo", "greeting") is None
```

## P2 · Acceptance

- [ ]  Suggestion muncul <2s setelah comment valuable masuk
- [ ]  Cache hit ratio ≥30% setelah 50 comment (lihat `budget.snapshot`)
- [ ]  `REPLY_ENABLED=false` → suggestion muncul tapi approve tidak jalankan TTS
- [ ]  Output reply tidak pernah mengandung link/nomor/harga-pasti (test guardrail)
- [ ]  Budget hit → fallback ke template, dashboard tampil warning kuning

---

# 🔴 P3 · Live Director (CC-LIVE-DIRECTOR-001..005)

**Tujuan**: state machine 2-jam auto-run, timer visible, emergency stop global.

## P3.1 · `apps/worker/config/products.yaml`

- Mapping produk → OBS scene + clip category
    
    ```yaml
    products:
      PALOMA:
        display_name: "PALOMA Smart Lock"
        obs_scene: "scene_paloma"
        clip_category: C_paloma_context
        segment_duration_s: 1500   # 25 menit
        order: 1
    
      CCTV_V380:
        display_name: "CCTV V380 Pro"
        obs_scene: "scene_cctv"
        clip_category: D_cctv_context
        segment_duration_s: 1200   # 20 menit
        order: 2
    
      SENTER_XHP160:
        display_name: "Senter XHP160"
        obs_scene: "scene_senter"
        clip_category: E_senter_context
        segment_duration_s: 1200
        order: 3
    
      DINGS_TRACKER:
        display_name: "DINGS Smart Tracker"
        obs_scene: "scene_tracker"
        clip_category: F_tracker_context
        segment_duration_s: 900    # 15 menit
        order: 4
    
    runsheet:
      - phase: opening
        duration_s: 600            # 10 menit
        categories: [A_opening]
        obs_scene: scene_opening
      - phase: anchor_1
        duration_s: 1500
        product: PALOMA
      - phase: anchor_2
        duration_s: 1200
        product: CCTV_V380
      - phase: reset
        duration_s: 600
        categories: [B_reset_viewer, G_question_hooks]
        obs_scene: scene_opening
      - phase: anchor_3
        duration_s: 1200
        product: SENTER_XHP160
      - phase: anchor_4
        duration_s: 900
        product: DINGS_TRACKER
      - phase: qa
        duration_s: 720            # 12 menit
        categories: [G_question_hooks, H_price_safe]
      - phase: closing
        duration_s: 480            # 8 menit
        categories: [K_closing]
        obs_scene: scene_closing
    ```
    
    **Total**: 10+25+20+10+20+15+12+8 = 120 menit ✓
    

## P3.2 · `apps/worker/src/banghack/core/orchestrator/director.py`

- State machine + timer + auto-advance
    
    ```python
    """Live Director — state machine 2-jam.
    
    Tugas:
    - Muat runsheet dari products.yaml
    - Advance fase otomatis tiap phase selesai
    - Pilih clip idle dari category aktif (anti-repeat 20 menit)
    - Switch OBS scene saat ganti produk
    - Hard-stop di menit 120
    - Respond ke command: live.start, live.pause, live.resume, live.stop
    """
    from __future__ import annotations
    
    import asyncio
    import logging
    import os
    import random
    import time
    from dataclasses import dataclass, field
    from enum import Enum
    from pathlib import Path
    
    import yaml
    
    from banghack.adapters.audio_library import AudioLibraryPlayer
    from banghack.adapters.obs import OBSClient  # existing v0.3
    from banghack.core.audio_library.manager import AudioLibraryManager
    
    log = logging.getLogger(__name__)
    
    class LiveMode(str, Enum):
        IDLE = "idle"
        RUNNING = "running"
        PAUSED = "paused"
        STOPPED = "stopped"
    
    @dataclass
    class Phase:
        phase: str
        duration_s: int
        product: str | None = None
        categories: list[str] = field(default_factory=list)
        obs_scene: str | None = None
    
    @dataclass
    class LiveState:
        mode: LiveMode = LiveMode.IDLE
        session_id: str | None = None
        started_at: float = 0.0
        elapsed_s: int = 0
        current_phase_idx: int = -1
        current_phase: Phase | None = None
        phase_started_at: float = 0.0
        current_product: str | None = None
        max_duration_s: int = 7200
        paused_total_s: float = 0.0
        paused_at: float | None = None
    
    class LiveDirector:
        def __init__(self,
                     library: AudioLibraryManager,
                     player: AudioLibraryPlayer,
                     obs: OBSClient | None,
                     broadcast_cb,  # async callable, emit ke WS
                     config_path: Path | None = None):
            self.library = library
            self.player = player
            self.obs = obs
            self.broadcast = broadcast_cb
            self.config_path = config_path or Path(os.getenv("PRODUCTS_YAML", "apps/worker/config/products.yaml"))
            self.state = LiveState()
            self.runsheet: list[Phase] = []
            self.products: dict[str, dict] = {}
            self._task: asyncio.Task | None = None
    
        def load_config(self) -> None:
            data = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))
            self.products = data.get("products", {})
            self.runsheet = []
            for r in data.get("runsheet", []):
                product = r.get("product")
                cats = r.get("categories", [])
                scene = r.get("obs_scene")
                if product and product in self.products:
                    p = self.products[product]
                    cats = cats or [p["clip_category"]]
                    scene = scene or p["obs_scene"]
                self.runsheet.append(Phase(
                    phase=r["phase"],
                    duration_s=r["duration_s"],
                    product=product,
                    categories=cats,
                    obs_scene=scene,
                ))
            total = sum(p.duration_s for p in self.runsheet)
            log.info("runsheet loaded: %d phases, total %ds (%.1fm)", len(self.runsheet), total, total/60)
    
        async def start(self) -> dict:
            if self.state.mode == LiveMode.RUNNING:
                return {"ok": False, "error": "already running"}
            self.load_config()
            self.state = LiveState(
                mode=LiveMode.RUNNING,
                session_id=f"live_{int(time.time())}",
                started_at=time.time(),
            )
            self._task = asyncio.create_task(self._run_loop())
            await self._emit_state()
            return {"ok": True, "session_id": self.state.session_id}
    
        async def pause(self) -> dict:
            if self.state.mode != LiveMode.RUNNING:
                return {"ok": False, "error": "not running"}
            self.state.mode = LiveMode.PAUSED
            self.state.paused_at = time.time()
            await self.player.stop()
            await self._emit_state()
            return {"ok": True}
    
        async def resume(self) -> dict:
            if self.state.mode != LiveMode.PAUSED:
                return {"ok": False, "error": "not paused"}
            if self.state.paused_at:
                self.state.paused_total_s += (time.time() - self.state.paused_at)
                self.state.paused_at = None
            self.state.mode = LiveMode.RUNNING
            await self._emit_state()
            return {"ok": True}
    
        async def stop(self, reason: str = "manual") -> dict:
            self.state.mode = LiveMode.STOPPED
            if self._task:
                self._task.cancel()
            await self.player.stop()
            await self._emit_state(extra={"stop_reason": reason})
            return {"ok": True, "reason": reason}
    
        async def _run_loop(self) -> None:
            try:
                for idx, phase in enumerate(self.runsheet):
                    if self.state.mode == LiveMode.STOPPED:
                        break
                    self.state.current_phase_idx = idx
                    self.state.current_phase = phase
                    self.state.current_product = phase.product
                    self.state.phase_started_at = time.time()
                    if self.obs and phase.obs_scene:
                        try:
                            await self.obs.switch_scene(phase.obs_scene)
                        except Exception as e:
                            log.warning("obs switch failed: %s", e)
                    await self._emit_state()
                    await self._play_phase(phase)
                await self.stop(reason="completed")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                log.error("director crashed: %s", e)
                await self.stop(reason=f"crash: {e}")
    
        async def _play_phase(self, phase: Phase) -> None:
            phase_end = time.time() + phase.duration_s
            while time.time() < phase_end:
                if self._total_elapsed() >= self.state.max_duration_s:
                    log.info("hard stop at 2h")
                    await self.stop(reason="max_duration")
                    return
                if self.state.mode == LiveMode.PAUSED:
                    await asyncio.sleep(1)
                    phase_end += 1  # pause tidak potong durasi fase
                    continue
                if self.state.mode == LiveMode.STOPPED:
                    return
                clip = self._pick_clip(phase)
                if clip:
                    await self.player.play(clip.id)
                    await self._emit_audio_now(clip)
                    # wait dengan jeda 3-8s di tengah
                    await asyncio.sleep(random.uniform(8, 18))
                    await asyncio.sleep(random.uniform(3, 8))
                else:
                    await asyncio.sleep(2)
    
        def _pick_clip(self, phase: Phase):
            now = time.time()
            pool = []
            for cat in phase.categories:
                pool.extend(self.library.by_category(cat))
            eligible = [c for c in pool if self.library.not_played_since(c.id, now, window_s=1200)]
            if not eligible:
                eligible = pool  # fallback kalau semua habis
            return random.choice(eligible) if eligible else None
    
        def _total_elapsed(self) -> int:
            if not self.state.started_at:
                return 0
            return int(time.time() - self.state.started_at - self.state.paused_total_s)
    
        async def _emit_state(self, extra: dict | None = None) -> None:
            payload = {
                "type": "live.state",
                "mode": self.state.mode.value,
                "session_id": self.state.session_id,
                "elapsed_s": self._total_elapsed(),
                "max_s": self.state.max_duration_s,
                "phase": self.state.current_phase.phase if self.state.current_phase else None,
                "product": self.state.current_product,
                "phase_idx": self.state.current_phase_idx,
                "phase_total": len(self.runsheet),
            }
            if extra:
                payload.update(extra)
            await self.broadcast(payload)
    
        async def _emit_audio_now(self, clip) -> None:
            await self.broadcast({
                "type": "audio.now",
                "clip_id": clip.id,
                "category": clip.category,
                "text": clip.text,
                "product": clip.product,
            })
    ```
    

## P3.3 · WS commands

```python
{ "type": "live.start" }
{ "type": "live.pause" }
{ "type": "live.resume" }
{ "type": "live.stop", "reason": "manual" }
{ "type": "live.emergency_stop" }  # = stop + audio.stop + obs to safe scene
{ "type": "live.get_state" }
```

## P3.4 · `apps/controller/src/lib/stores/live_state.ts`

```tsx
import { writable, derived } from 'svelte/store';

export interface LiveState {
  mode: 'idle' | 'running' | 'paused' | 'stopped';
  session_id: string | null;
  elapsed_s: number;
  max_s: number;
  phase: string | null;
  product: string | null;
  phase_idx: number;
  phase_total: number;
}

export const liveState = writable<LiveState>({
  mode: 'idle', session_id: null, elapsed_s: 0, max_s: 7200,
  phase: null, product: null, phase_idx: -1, phase_total: 0,
});

export const remainingS = derived(liveState, $s => Math.max(0, $s.max_s - $s.elapsed_s));
export const progressPct = derived(liveState, $s => Math.min(100, $s.elapsed_s / $s.max_s * 100));
```

## P3.5 · `apps/controller/src/lib/components/TwoHourTimer.svelte`

- Timer visual
    
    ```
    <script lang="ts">
      import { liveState, remainingS, progressPct } from '$lib/stores/live_state';
      function fmt(s: number) {
        const h = Math.floor(s/3600), m = Math.floor((s%3600)/60), ss = s%60;
        return `${h}:${String(m).padStart(2,'0')}:${String(ss).padStart(2,'0')}`;
      }
      const warnAt = 600;  // 10 menit terakhir warna merah
    </script>
    
    <div class="p-4 rounded border-2 {$remainingS < warnAt ? 'border-red-500 bg-red-50' : 'border-green-500 bg-green-50'}">
      <div class="flex justify-between items-baseline">
        <div class="text-xs uppercase">Sisa waktu</div>
        <div class="text-xs">{$liveState.phase || '—'} ({$liveState.phase_idx+1}/{$liveState.phase_total})</div>
      </div>
      <div class="text-4xl font-mono font-bold">{fmt($remainingS)}</div>
      <div class="h-2 bg-gray-200 rounded mt-2 overflow-hidden">
        <div class="h-full bg-blue-500" style:width="{$progressPct}%"></div>
      </div>
      <div class="text-xs mt-1 text-gray-600">Mode: <b>{$liveState.mode}</b> · Produk: <b>{$liveState.product || '—'}</b></div>
    </div>
    ```
    

## P3.6 · `apps/controller/src/lib/components/EmergencyStop.svelte`

- Big red button
    
    ```
    <script lang="ts">
      import { sendCommand } from '$lib/api/ws';
      let confirming = $state(false);
      let timeoutId: ReturnType<typeof setTimeout>;
      function armAndFire() {
        if (!confirming) {
          confirming = true;
          timeoutId = setTimeout(() => confirming = false, 3000);
          return;
        }
        clearTimeout(timeoutId);
        sendCommand({ type: 'live.emergency_stop' });
        confirming = false;
      }
    </script>
    
    <button
      on:click={armAndFire}
      class="w-full py-4 text-white font-bold rounded-lg text-lg transition {confirming ? 'bg-red-700 animate-pulse' : 'bg-red-500 hover:bg-red-600'}">
      {confirming ? '⚠️ KLIK LAGI DALAM 3 DETIK UNTUK STOP' : '🛑 EMERGENCY STOP'}
    </button>
    ```
    

## P3.7 · Test `test_director_state.py`

```python
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from banghack.core.orchestrator.director import LiveDirector, LiveMode

@pytest.fixture
def director(tmp_path):
    cfg = tmp_path / "products.yaml"
    cfg.write_text("""
products:
  X: {display_name: X, obs_scene: s_x, clip_category: CAT_X, segment_duration_s: 60, order: 1}
runsheet:
  - {phase: p1, duration_s: 5, product: X}
""")
    lib = MagicMock(); lib.by_category.return_value = []
    player = MagicMock(); player.stop = AsyncMock(); player.play = AsyncMock()
    broadcast = AsyncMock()
    return LiveDirector(lib, player, None, broadcast, config_path=cfg)

@pytest.mark.asyncio
async def test_start_sets_running(director):
    r = await director.start()
    assert r["ok"]
    assert director.state.mode == LiveMode.RUNNING
    await director.stop()

@pytest.mark.asyncio
async def test_pause_resume(director):
    await director.start()
    await asyncio.sleep(0.1)
    await director.pause()
    assert director.state.mode == LiveMode.PAUSED
    await director.resume()
    assert director.state.mode == LiveMode.RUNNING
    await director.stop()
```

## P3 · Acceptance

- [ ]  `live.start` → timer berjalan, clip dari fase `opening` auto-play
- [ ]  Fase berpindah otomatis sesuai `duration_s` di YAML
- [ ]  OBS scene switch saat ganti produk (kalau OBS terhubung)
- [ ]  Anti-repeat 20 menit: tidak ada clip yang play 2x dalam window tersebut
- [ ]  Emergency stop: audio berhenti <500ms, mode = stopped, timer stop
- [ ]  Hard stop di `max_duration_s` tanpa intervensi
- [ ]  Test unit hijau

---

# 🧪 Integration test final (sebelum live real)

Jalankan dry run 30 menit dengan `max_duration_s=1800`, `REPLY_ENABLED=false`, `DRY_RUN=true`:

- [ ]  Timer tampil benar
- [ ]  Semua fase teresekusi minimal 1x clip
- [ ]  Comment simulasi (script python inject fake comment) ter-klasifikasi + muncul suggestion
- [ ]  `budget.snapshot` tampil benar
- [ ]  Emergency stop di menit 15 → semua berhenti rapi
- [ ]  Log JSON lengkap di `apps/worker/logs/`
- [ ]  Tidak ada unhandled exception

---

# 📝 Urutan commit yang direkomendasikan

```
[v0.4][CC-LIVE-CLIP-001] add clips_script.yaml + deps
[v0.4][CC-LIVE-CLIP-002] audio library manager + adapter
[v0.4][CC-LIVE-CLIP-003] gen_audio_library script + bat
[v0.4][CC-LIVE-CLIP-004] WS audio.list/play/stop + AudioLibraryGrid
[v0.4][CC-LIVE-CLIP-005] test_audio_library + generate 10 sample
[v0.4][CC-LIVE-CLASSIFIER-001] rules.py + test
[v0.4][CC-LIVE-CLASSIFIER-002] llm_fallback + integration main.py
[v0.4][CC-LIVE-CLASSIFIER-003] DecisionStream svelte + store
[v0.4][CC-LIVE-ORCH-001] budget_guard
[v0.4][CC-LIVE-ORCH-002] reply_cache + test
[v0.4][CC-LIVE-ORCH-003] suggester + reply_templates.yaml
[v0.4][CC-LIVE-ORCH-004] WS reply.* + ReplySuggestions svelte
[v0.4][CC-LIVE-ORCH-005] output guardrail regex + test
[v0.4][CC-LIVE-DIRECTOR-001] products.yaml + director state machine
[v0.4][CC-LIVE-DIRECTOR-002] runsheet loop + anti-repeat
[v0.4][CC-LIVE-DIRECTOR-003] WS live.* + live_state store
[v0.4][CC-LIVE-DIRECTOR-004] TwoHourTimer + EmergencyStop svelte
[v0.4][CC-LIVE-DIRECTOR-005] test_director + integration dry-run
[v0.4] update CHANGELOG → v0.4.0 shipped
```

---

# ⚠️ Catatan untuk local agent

1. **JANGAN ubah file existing v0.3** (32 WS commands di `main.py`) kecuali hanya **menambahkan** handler baru di block dispatcher.
2. **JANGAN ganti stack** (Python/UV/Svelte 5/Tailwind v4). Kalau butuh library lain, tambah ke `pyproject.toml` dengan pin version.
3. **SEMUA LLM call** wajib lewat `BudgetGuard.can_call()` dulu. Tidak ada bypass.
4. **SEMUA output reply** wajib lewat `Suggester._safe()` regex. Tidak ada bypass.
5. **Anti-repeat 20 menit** wajib untuk clip library (ada di `manager.not_played_since()`).
6. **Hard-stop 2 jam** wajib — tidak boleh looping tanpa batas.
7. Kalau ada yang tidak jelas, tulis TODO comment `# TODO(dedy):` di file, jangan asal implement.

> ✅ **Bottom line**: dokumen ini punya ~650 baris skeleton kode yang 80% siap pakai. Agent lokal cukup baca top-down, paste skeleton, sesuaikan import/signature dengan v0.3 existing, run test, commit per tiket. Estimasi 40-50 jam kerja fokus.
>