# 🎨 03 · Design — UX Controller (Svelte 5 + Tailwind v4)

> **Canonical**: spesifikasi UX controller. Mirror dari Notion.  
> Prinsip: **profesional, cepat, minim klik, tidak ambigu saat error**.

---

## 1. Design Principles

1. **Operator-first** — Dedy sambil Live harus bisa baca status dalam ≤1 detik dari lirikan
2. **Status pills** — warna = truth: hijau healthy, kuning degraded, merah fail
3. **Event-stream UI** — live monitor = feed terbaru di atas, auto-scroll off-able
4. **Zero modal** — jangan interupsi saat Live; pakai toast + inline
5. **Keyboard-first** — shortcut untuk pause/resume/emergency stop
6. **Dark mode default** — live malam
7. **No build-time config surprise** — Tailwind v4 `@theme` di `app.css`, runtime-friendly

---

## 2. Information Architecture

```
Sidebar (64px collapsed / 200px expanded)
├── 🏠 Dashboard       → /
├── 📡 Live Monitor    → /live
├── 🚨 Errors          → /errors
├── 🎭 Persona         → /persona
├── ⚙️  Config         → /config
└── 💰 Cost            → /cost
Top bar (56px)
├── Status dot (🟢🟡🔴) + room ID
├── Uptime
├── Queue size badge
├── Pause/Resume toggle (space)
└── Emergency Stop (esc×2)
```

---

## 3. Page Specs

### 3.1 `/` Dashboard

6 KPI cards grid (3×2 desktop, 1×6 mobile):

| Card | Metric | Color rule |
|------|--------|------------|
| Status | Connected/Paused/Error | green/yellow/red |
| Viewers | Live count | neutral |
| Comments | Total session | neutral |
| Replies | Sent / Rejected | neutral |
| Latency | p95 ms | green <5s, yellow <8s, red ≥8s |
| Cost | Rp today | green <500, yellow <1000, red ≥1000 |

Bawahnya: 1 chart area (comments vs replies per menit, 30 min window) + recent 5 events mini-feed.

### 3.2 `/live` Live Monitor

Split view horizontal:

- **Kiri 50%**: Comment feed (latest first). Row: avatar-initial • nickname • comment • status pill (queued/sent/rejected/skipped)
- **Kanan 50%**: Reply feed. Row: target-nickname • reply text • latency ms • token count
- Sticky filter bar: search, filter by status, clear all
- Klik row kiri → highlight reply row kanan yang berpasangan
- Tombol "Ignore this comment" di setiap row kiri (kirim `POST /api/control/skip`)

### 3.3 `/errors`

- Tab horizontal: All • TikTok • LLM • TTS • Guardrail • OBS • IPC
- Table rows: ts • module • code • message • stack (toggle)
- Action: Copy cURL/command untuk reproduce
- Callout top: **"File pertama yang harus dibuka"** untuk error type terbanyak (berdasarkan Error Handling Matrix)

### 3.4 `/persona`

- Left: Monaco editor (80% lebar), syntax markdown
- Right: Preview rendered markdown
- Sticky footer: Save (ctrl+s) • Reload (ctrl+r) • "Last saved: 2 min ago"
- Test prompt box: "Try a comment" → kirim `POST /api/persona/test` → tampil sample reply (tidak broadcast)

### 3.5 `/config`

- Grouped sections: LLM • TTS • Rate Limit • OBS • Logging
- Form fields dari schema Pydantic (auto-generated dari `apps/worker/src/banghack/config/settings.py`)
- Field type: toggle, number slider, select, textarea
- Secret fields: masked, tombol "reveal" yang butuh confirm dialog
- Save → `POST /api/config` + hot-reload

### 3.6 `/cost`

- Top row: Today • This week • This month • Projected monthly
- Chart: stacked bar per jam (input token / output token)
- Table: per session (start, end, tokens, Rp, LLM provider used)
- Export CSV button

---

## 4. Component Library (lib/components)

| Component | Props | Usage |
|-----------|-------|-------|
| StatusPill | status: 'ok'\|'warn'\|'error'\|'info', label | Everywhere |
| KPICard | title, value, unit, trend, status | Dashboard |
| LogRow | event: WSEvent | Live monitor |
| SparkLine | data: number[], color | Dashboard chart |
| Toast | message, type, duration | Global notifications |
| MonacoEditor | value, language, onChange | Persona page |
| ConfirmDialog | message, onConfirm | Destructive actions |

---

## 5. Svelte 5 State Store Pattern

`lib/stores/ws.svelte.ts` — singleton WebSocket client dengan runes:

```typescript
class WSStore {
  events = $state<WSEvent[]>([]);
  connected = $state(false);
  private ws?: WebSocket;
  connect() {
    this.ws = new WebSocket('ws://localhost:8765');
    this.ws.onopen = () => this.connected = true;
    this.ws.onmessage = (e) => {
      const evt = JSON.parse(e.data) as WSEvent;
      this.events = [evt, ...this.events].slice(0, 500);
    };
    this.ws.onclose = () => {
      this.connected = false;
      setTimeout(() => this.connect(), 3000);
    };
  }
}
export const ws = new WSStore();
```

Derived state:

```typescript
import { ws } from './ws.svelte';
export const comments = $derived(ws.events.filter(e => e.type === 'comment_received'));
export const replies = $derived(ws.events.filter(e => e.type === 'reply_generated'));
export const errors = $derived(ws.events.filter(e => e.type === 'error'));
```

---

## 6. Tailwind v4 Theme (`src/app.css`)

```css
@import "tailwindcss";
@theme {
  --color-bg-primary: #0a0a0b;
  --color-bg-panel: #141417;
  --color-bg-elevated: #1c1c21;
  --color-border: #2a2a31;
  --color-text-primary: #ececf1;
  --color-text-secondary: #8e8ea0;
  --color-ok: #10b981;
  --color-warn: #f59e0b;
  --color-error: #ef4444;
  --color-accent: #a855f7;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
  --font-sans: "Inter", system-ui, sans-serif;
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
}
* { @apply border-border; }
html, body { @apply bg-bg-primary text-text-primary font-sans antialiased; }
```

---

## 7. Keyboard Shortcuts (global)

| Key | Action |
|-----|--------|
| Space | Pause / Resume |
| Esc × 2 | Emergency Stop |
| Ctrl+S | Save (di /persona dan /config) |
| Ctrl+R | Reload persona |
| G then D | Go to Dashboard |
| G then L | Go to Live |
| G then E | Go to Errors |

---

## 8. Responsive Breakpoints

- Mobile 360px: single column, sidebar drawer
- Tablet 768px: 2 column dashboard
- Desktop 1280px+: 3×2 dashboard, split view live monitor
- Target primary: **desktop Windows 1080p** (monitor Dedy saat Live)

---

## 9. Accessibility

- Color contrast WCAG AA (bg vs text ≥4.5:1)
- Semua icon ada aria-label
- Fokus ring visible (tailwind `focus-visible:ring-2`)
- Keyboard-only navigable

---

## 10. Wireframe ASCII (Live Monitor)

```
┌─ tiklivenotion controller ─────────────────────────────────────────┐
│🏠 📡 🚨 🎭 ⚙️ 💰   🟢 @interiorhack.id • up 12:34 • q:3  [⏸] [⏹]  │
├────────────────────────────────┬──────────────────────────────────┤
│ Comments (42)        [filter▾]│ Replies (38)          [filter▾] │
├────────────────────────────────┼──────────────────────────────────┤
│ 10:15 andi: lampu pir brp?  ✓ │ 10:15 → andi: Rp 35rb, keranjang │
│                                │        kuning bang   • 3.2s • 45t│
│ 10:14 budi: kirim shopee ✕    │ 10:14 → budi: REJECTED (link)    │
│ 10:13 siti: coco?          ⏳ │ 10:13 → siti: (queued...)        │
│ ...                            │ ...                              │
└────────────────────────────────┴──────────────────────────────────┘
```
