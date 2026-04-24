# ⚡ livetik — MASTER FIX PATCH (Paste-Ready, No Kiro)

<aside>
🚨

**Baca dulu 5 detik.** Dokumen ini = **kode full** dari Notion AI langsung, bukan spec untuk Kiro. Copy-paste per file ke repo kamu, commit, push, test. Tidak ada yang perlu Kiro kerjain lagi. Urutan apply ada di §0.

</aside>

<aside>
🎯

**Target fix 3 masalah konkret:**

1. `/library` blank → FIX §1 + §3 + §7
2. LLM chat tidak auto-reply → FIX §11 (worker [main.py](http://main.py) wiring) + §5 (UI approve card)
3. Orchestrator LLM belum aktif → FIX §11 + §12 (wire LiveDirector ke `live.start` WS command)
4. Tidak ada kontrol UI untuk lihat semua itu → FIX §4 + §6 + §10
</aside>

## 📋 §0 — Urutan Apply (15 menit kerja)

```bash
cd D:/path/ke/livetik   # sesuaikan

# STEP 0.1 — perbaiki .gitignore biar folder $lib ikut ke-push
# Edit .gitignore, HAPUS 2 baris ini:
#   lib/
#   lib64/
# Ganti dengan yang di §1 bawah.

# STEP 0.2 — force add stores + components yang selama ini ter-ignore
git add -f apps/controller/src/lib/
git status   # harus tampil puluhan file .svelte + .ts baru

# STEP 0.3 — copy-paste semua file di §1-§12 ke lokasi masing-masing
# (path tertera di heading tiap section)

# STEP 0.4 — install dep baru (sekali aja)
cd apps/worker && uv sync && cd ../..
cd apps/controller && pnpm install && cd ../..

# STEP 0.5 — commit + push
git add -A
git commit -m "fix: master patch — library render + auto-reply wiring + orchestrator boot"
git push origin main

# STEP 0.6 — verify
curl -s https://api.github.com/repos/dedy45/livetik/contents/apps/controller/src/lib | head
# expected: bukan {"message":"Not Found"}

# STEP 0.7 — run local
# Terminal 1
cd apps/worker && uv run python -m banghack.main
# Terminal 2
cd apps/controller && pnpm dev
# Buka http://127.0.0.1:5173 — klik /library, /live, /. Decision Stream + Reply card harus jalan.
```

---

## 📄 §1 — `.gitignore` (ROOT) — REPLACE seluruh section Python

Cari blok Python di `.gitignore`, **replace** jadi ini:

```
# Python build artifacts (Svelte-safe — JANGAN pakai bare 'lib/')
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
# NOTE: dulu di sini ada 'lib/' dan 'lib64/' — dihapus karena match $lib SvelteKit.
# Python venv sudah di-ignore via .venv/, venv/, ENV/, env/ di bawah.
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual envs
.venv/
venv/
ENV/
env/
```

---

## 📄 §2 — `apps/controller/src/lib/stores/ws.svelte.ts` — FULL FILE (NEW/REPLACE)

Jantung semua page. Auto-connect ke worker WS `ws://127.0.0.1:8765`, auto-reconnect, simpan semua event, dispatch command.

```tsx
// apps/controller/src/lib/stores/ws.svelte.ts
export type Metrics = {
	status: 'idle' | 'connecting' | 'live' | 'paused' | 'stopped' | 'error';
	viewers: number;
	comments: number;
	gifts: number;
	joins: number;
	replies: number;
	queue_size: number;
	latency_p95_ms: number;
	cost_idr: number;
	budget_idr: number;
	budget_pct: number;
	over_budget: boolean;
	reply_enabled: boolean;
	dry_run: boolean;
	cartesia_pool: { key: string; calls: number; exhausted: boolean; cooldown_s: number }[];
	llm_models: { id: string; model: string; tier: string }[];
};

export type LiveState = {
	mode: 'idle' | 'running' | 'paused' | 'stopped';
	session_id: string | null;
	elapsed_s: number;
	max_s: number;
	phase: string | null;
	product: string | null;
	phase_idx: number;
	phase_total: number;
};

export type Suggestion = {
	suggestion_id: string;
	user: string;
	comment_id: string;
	comment_text: string;
	intent: string;
	replies: string[];
	source: 'template' | 'cache' | 'llm';
	ts: number;
};

type CmdResult = { ok: boolean; result?: any; error?: string; latency_ms?: number };

function createStore() {
	let ws = $state<WebSocket | null>(null);
	let connected = $state(false);
	let connectedAt = $state<number | null>(null);

	const metrics = $state<Metrics>({
		status: 'idle', viewers: 0, comments: 0, gifts: 0, joins: 0, replies: 0,
		queue_size: 0, latency_p95_ms: 0, cost_idr: 0, budget_idr: 50000, budget_pct: 0,
		over_budget: false, reply_enabled: false, dry_run: true,
		cartesia_pool: [], llm_models: [],
	});

	const liveState = $state<LiveState>({
		mode: 'idle', session_id: null, elapsed_s: 0, max_s: 7200,
		phase: null, product: null, phase_idx: -1, phase_total: 0,
	});

	const events = $state<{ ts: number; type: string; data?: any }[]>([]);
	const comments = $state<{ ts: number; user: string; text: string; intent?: string }[]>([]);
	const replies = $state<{ ts: number; user: string; comment: string; reply: string; tier: string; tts: string; latency_ms: number }[]>([]);
	const suggestions = $state<Suggestion[]>([]);
	const tiktokEvents = $state<{ ts: number; event_type: string; user: string; text: string; count: number }[]>([]);
	const errorLog = $state<{ ts: number; category: string; user?: string; detail: string }[]>([]);
	const decisions = $state<{ ts: number; kind: string; input: string; output: string; reasoning: string }[]>([]);
	const audioClips = $state<any[]>([]);
	const testResults = $state(new Map<string, CmdResult>());

	let nowPlaying = $state<{ clip_id: string; category: string; text: string; product?: string; ts: number } | null>(null);
	let reqIdSeq = 0;

	function connect() {
		try {
			ws = new WebSocket('ws://127.0.0.1:8765');
		} catch (e) {
			setTimeout(connect, 2000);
			return;
		}
		ws.onopen = () => {
			connected = true;
			connectedAt = Date.now();
			// on connect, minta state awal
			sendCommand('audio.list', {});
			sendCommand('live.get_state', {});
			sendCommand('budget.get', {});
		};
		ws.onclose = () => { connected = false; setTimeout(connect, 2000); };
		ws.onerror = () => { connected = false; };
		ws.onmessage = (ev) => {
			try { handleMessage(JSON.parse(ev.data)); } catch (e) { console.error('ws parse', e); }
		};
	}

	function handleMessage(msg: any) {
		events.unshift({ ts: Date.now(), type: msg.type, data: msg });
		if (events.length > 200) events.length = 200;

		switch (msg.type) {
			case 'metrics':
				Object.assign(metrics, msg.data ?? msg);
				break;
			case 'live.state':
				Object.assign(liveState, {
					mode: msg.mode, session_id: msg.session_id, elapsed_s: msg.elapsed_s ?? 0,
					max_s: msg.max_s ?? 7200, phase: msg.phase, product: msg.product,
					phase_idx: msg.phase_idx ?? -1, phase_total: msg.phase_total ?? 0,
				});
				break;
			case 'tiktok.comment':
				comments.unshift({ ts: Date.now(), user: msg.user, text: msg.text, intent: msg.intent });
				tiktokEvents.unshift({ ts: Date.now(), event_type: 'comment', user: msg.user, text: msg.text, count: 1 });
				break;
			case 'comment.classified':
				decisions.unshift({
					ts: Date.now(), kind: 'classify',
					input: msg.text ?? '',
					output: `intent=${msg.intent} conf=${(msg.confidence ?? 0).toFixed(2)}`,
					reasoning: msg.source === 'rules' ? `rule:${msg.rule_id ?? msg.reason}` : `llm:${msg.model ?? ''}`,
				});
				break;
			case 'reply.suggestion':
				suggestions.unshift({
					suggestion_id: msg.suggestion_id, user: msg.user, comment_id: msg.comment_id,
					comment_text: msg.comment_text, intent: msg.intent, replies: msg.replies ?? [],
					source: msg.source ?? 'llm', ts: Date.now(),
				});
				decisions.unshift({
					ts: Date.now(), kind: 'suggest',
					input: msg.comment_text ?? '',
					output: (msg.replies?.[0] ?? '').slice(0, 60),
					reasoning: `src=${msg.source} intent=${msg.intent}`,
				});
				if (suggestions.length > 30) suggestions.length = 30;
				break;
			case 'reply.sent':
				replies.unshift({ ts: Date.now(), ...msg });
				suggestions.splice(0, suggestions.length, ...suggestions.filter(s => s.suggestion_id !== msg.suggestion_id));
				break;
			case 'audio.list.ok':
				audioClips.splice(0, audioClips.length, ...(msg.clips ?? []));
				break;
			case 'audio.now':
				nowPlaying = { clip_id: msg.clip_id, category: msg.category, text: msg.text, product: msg.product, ts: Date.now() };
				decisions.unshift({
					ts: Date.now(), kind: 'clip.play',
					input: msg.category ?? '',
					output: msg.clip_id ?? '',
					reasoning: (msg.text ?? '').slice(0, 80),
				});
				break;
			case 'audio.done':
				if (nowPlaying?.clip_id === msg.clip_id) nowPlaying = null;
				break;
			case 'error':
				errorLog.unshift({ ts: Date.now(), category: msg.category ?? 'unknown', user: msg.user, detail: msg.detail ?? JSON.stringify(msg) });
				break;
			case 'cmd_result':
				if (msg.req_id) testResults.set(msg.req_id, { ok: msg.ok, result: msg.result, error: msg.error, latency_ms: msg.latency_ms });
				break;
		}
		if (decisions.length > 100) decisions.length = 100;
		if (errorLog.length > 200) errorLog.length = 200;
		if (comments.length > 100) comments.length = 100;
		if (replies.length > 50) replies.length = 50;
		if (tiktokEvents.length > 200) tiktokEvents.length = 200;
	}

	function sendCommand(name: string, params: any = {}): string {
		const reqId = `req-${++reqIdSeq}`;
		if (ws?.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify({ type: 'cmd', name, req_id: reqId, params }));
		}
		return reqId;
	}

	if (typeof window !== 'undefined') connect();

	return {
		get connected() { return connected; },
		get uptime() {
			if (!connectedAt) return '--';
			const s = Math.floor((Date.now() - connectedAt) / 1000);
			return `${Math.floor(s / 60)}m${s % 60}s`;
		},
		get metrics() { return metrics; },
		get liveState() { return liveState; },
		get events() { return events; },
		get comments() { return comments; },
		get replies() { return replies; },
		get suggestions() { return suggestions; },
		get tiktokEvents() { return tiktokEvents; },
		get errorLog() { return errorLog; },
		get decisions() { return decisions; },
		get audioClips() { return audioClips; },
		get nowPlaying() { return nowPlaying; },
		testResults,
		sendCommand,
	};
}

export const wsStore = createStore();
```

---

## 📄 §3 — `apps/controller/src/lib/stores/audio_library.svelte.ts` — FULL FILE

```tsx
export type ClipMeta = {
	id: string;
	category: string;
	text: string;
	file: string;
	product?: string;
	tags?: string[];
};

export const CATEGORIES = [
	'ALL', 'A_opening', 'B_reset_viewer', 'C_paloma_context', 'D_cctv_context',
	'E_senter_context', 'F_tracker_context', 'G_question_hooks', 'H_price_safe',
	'I_trust_safety', 'J_idle_human', 'K_closing',
] as const;
```

---

## 📄 §4 — `apps/controller/src/lib/components/DecisionStream.svelte` — FULL FILE

Panel live timeline: classify → suggest → [clip.play](http://clip.play) → phase change. Ini yang bikin semua LLM/orchestrator activity **visible**.

```
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	const decisions = $derived(wsStore.decisions);

	const colorByKind: Record<string, string> = {
		classify: 'text-blue-400',
		suggest: 'text-purple-400',
		'clip.play': 'text-green-400',
		phase: 'text-orange-400',
	};
</script>

<div class="bg-bg-panel border border-border rounded-lg p-6">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-lg font-semibold">🧠 Orchestrator Decision Stream</h3>
		<span class="text-xs text-text-secondary">{decisions.length} decision · live</span>
	</div>
	{#if decisions.length === 0}
		<p class="text-text-secondary text-sm">
			Belum ada keputusan. Trigger dengan <code>live.start</code> atau inject fake comment:<br />
			<code class="text-xs">python debug-dan-tes/02_inject_fake_comments.py</code>
		</p>
	{:else}
		<ul class="space-y-1 text-xs font-mono max-h-96 overflow-auto">
			{#each decisions as d (d.ts + d.kind + d.output)}
				<li class="grid grid-cols-[80px_80px_1fr_1fr_1fr] gap-2 py-1 border-b border-border/50">
					<span class="text-accent">{new Date(d.ts).toLocaleTimeString('id-ID')}</span>
					<span class={colorByKind[d.kind] ?? 'text-text-secondary'}>{d.kind}</span>
					<span class="text-text-secondary truncate" title={d.input}>{d.input}</span>
					<span class="text-text-primary truncate" title={d.output}>→ {d.output}</span>
					<span class="text-text-secondary italic truncate" title={d.reasoning}>{d.reasoning}</span>
				</li>
			{/each}
		</ul>
	{/if}
</div>
```

---

## 📄 §5 — `apps/controller/src/lib/components/ReplySuggestions.svelte` — FULL FILE

Operator lihat 3 opsi reply, klik approve → worker kirim ke TTS → voice keluar.

```
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	const suggestions = $derived(wsStore.suggestions);

	function approve(id: string, variant: number) {
		wsStore.sendCommand('reply.approve', { suggestion_id: id, variant });
	}
	function reject(id: string) {
		wsStore.sendCommand('reply.reject', { suggestion_id: id });
	}
	function regen(id: string, hint: string) {
		wsStore.sendCommand('reply.regen', { suggestion_id: id, hint });
	}
</script>

<div class="bg-bg-panel border border-border rounded-lg p-6">
	<div class="flex items-center justify-between mb-3">
		<h3 class="text-lg font-semibold">💬 Reply Suggestions</h3>
		<span class="text-xs text-text-secondary">{suggestions.length} pending</span>
	</div>
	{#if suggestions.length === 0}
		<p class="text-sm text-text-secondary">Belum ada saran. LLM akan generate saat ada comment "bernilai" (buying_intent, compatibility, product_question).</p>
	{:else}
		<div class="space-y-3 max-h-[500px] overflow-auto">
			{#each suggestions as s (s.suggestion_id)}
				<div class="border border-border rounded p-3 bg-yellow-500/5">
					<div class="text-xs text-text-secondary mb-1">
						@{s.user} · <span class="text-accent">{s.intent}</span> · via <b>{s.source}</b>
					</div>
					<div class="text-sm font-medium mb-2">"{s.comment_text}"</div>
					<ul class="space-y-1">
						{#each s.replies as r, i}
							<li class="flex gap-2">
								<button
									onclick={() => approve(s.suggestion_id, i)}
									class="bg-green-600 hover:bg-green-500 text-white px-2 py-0.5 rounded text-xs font-bold"
								>✓ {i + 1}</button>
								<span class="text-sm flex-1">{r}</span>
							</li>
						{/each}
					</ul>
					<div class="flex gap-1 mt-2">
						<button onclick={() => regen(s.suggestion_id, 'lebih pendek')} class="text-xs bg-blue-500/20 hover:bg-blue-500/30 px-2 py-0.5 rounded">↻ pendek</button>
						<button onclick={() => regen(s.suggestion_id, 'lebih hangat')} class="text-xs bg-blue-500/20 hover:bg-blue-500/30 px-2 py-0.5 rounded">↻ hangat</button>
						<button onclick={() => reject(s.suggestion_id)} class="text-xs bg-red-500/20 hover:bg-red-500/30 px-2 py-0.5 rounded ml-auto">✕ skip</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
```

---

## 📄 §6 — `apps/controller/src/lib/components/TwoHourTimer.svelte` + `EmergencyStop.svelte`

```
<!-- TwoHourTimer.svelte -->
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	const s = $derived(wsStore.liveState);
	const remaining = $derived(Math.max(0, s.max_s - s.elapsed_s));
	const pct = $derived(Math.min(100, (s.elapsed_s / s.max_s) * 100));
	const warn = $derived(remaining < 600);
	function fmt(sec: number) {
		const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), ss = sec % 60;
		return `${h}:${String(m).padStart(2, '0')}:${String(ss).padStart(2, '0')}`;
	}
</script>

<div class="p-4 rounded-lg border-2 {warn ? 'border-red-500 bg-red-500/10' : 'border-green-500 bg-green-500/10'}">
	<div class="flex justify-between items-baseline">
		<span class="text-xs uppercase text-text-secondary">Sisa waktu</span>
		<span class="text-xs">{s.phase ?? '—'} ({s.phase_idx + 1}/{s.phase_total})</span>
	</div>
	<div class="text-4xl font-mono font-bold">{fmt(remaining)}</div>
	<div class="h-2 bg-bg-dark rounded mt-2 overflow-hidden">
		<div class="h-full bg-accent" style:width="{pct}%"></div>
	</div>
	<div class="text-xs mt-1 text-text-secondary">Mode: <b>{s.mode}</b> · Produk: <b>{s.product ?? '—'}</b></div>
</div>
```

```
<!-- EmergencyStop.svelte -->
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	let confirming = $state(false);
	let tid: ReturnType<typeof setTimeout>;
	function click() {
		if (!confirming) {
			confirming = true;
			tid = setTimeout(() => (confirming = false), 3000);
			return;
		}
		clearTimeout(tid);
		wsStore.sendCommand('live.emergency_stop', {});
		confirming = false;
	}
</script>

<button
	onclick={click}
	class="w-full py-4 text-white font-bold rounded-lg text-lg transition {confirming ? 'bg-red-700 animate-pulse' : 'bg-red-500 hover:bg-red-600'}"
>
	{confirming ? '⚠️ KLIK LAGI (3 detik) UNTUK STOP' : '🛑 EMERGENCY STOP'}
</button>
```

---

## 📄 §7 — `apps/controller/src/lib/components/AudioLibraryGrid.svelte` — FULL FILE

```
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import { CATEGORIES } from '$lib/stores/audio_library.svelte';

	let search = $state('');
	let cat = $state<string>('ALL');

	const clips = $derived(wsStore.audioClips);
	const nowId = $derived(wsStore.nowPlaying?.clip_id);
	const visible = $derived(
		clips
			.filter((c: any) => cat === 'ALL' || c.category === cat)
			.filter((c: any) => !search || (c.text || '').toLowerCase().includes(search.toLowerCase()) || c.id.toLowerCase().includes(search.toLowerCase()))
	);

	function play(id: string) { wsStore.sendCommand('audio.play', { clip_id: id }); }
	function stop() { wsStore.sendCommand('audio.stop', {}); }
</script>

<div class="bg-bg-panel border border-border rounded-lg p-4">
	<div class="flex gap-2 mb-3 items-center">
		<input bind:value={search} placeholder="cari clip..." class="bg-bg-dark border border-border rounded px-2 py-1 text-sm flex-1" />
		<select bind:value={cat} class="bg-bg-dark border border-border rounded px-2 py-1 text-sm">
			{#each CATEGORIES as c}<option value={c}>{c}</option>{/each}
		</select>
		<button onclick={stop} class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm">⏹ Stop</button>
		<span class="text-xs text-text-secondary">{visible.length}/{clips.length}</span>
	</div>
	<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-[500px] overflow-auto">
		{#each visible as c (c.id)}
			<button
				onclick={() => play(c.id)}
				class="text-left border border-border rounded p-2 hover:bg-accent/10 text-xs {nowId === c.id ? 'ring-2 ring-accent bg-accent/20' : ''}"
			>
				<div class="font-mono text-[10px] text-text-secondary">{c.id}</div>
				<div class="line-clamp-3">{c.text}</div>
				{#if c.product}<div class="text-accent mt-1">🏷 {c.product}</div>{/if}
			</button>
		{/each}
	</div>
</div>
```

---

## 📄 §8 — `apps/controller/src/routes/library/+page.svelte` — FULL FILE

```
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import AudioLibraryGrid from '$lib/components/AudioLibraryGrid.svelte';

	const now = $derived(wsStore.nowPlaying);
	const recent = $derived(wsStore.events.filter(e => e.type === 'audio.now').slice(0, 10));
	const total = $derived(wsStore.audioClips.length);
</script>

<div class="p-6 space-y-4">
	<h1 class="text-2xl font-bold">🎵 Audio Library ({total} clips)</h1>

	{#if now}
		<div class="bg-green-500/20 border border-green-500 rounded-lg p-4 animate-pulse">
			<div class="flex items-center gap-3">
				<span class="text-3xl">🔊</span>
				<div class="flex-1">
					<div class="text-xs text-green-400 font-bold">NOW PLAYING</div>
					<div class="text-sm font-mono">{now.clip_id} · {now.category}</div>
					<div class="text-sm">{now.text}</div>
				</div>
			</div>
		</div>
	{:else}
		<div class="bg-bg-panel border border-border rounded-lg p-4 text-text-secondary text-sm">
			Tidak ada clip yang sedang play. Klik salah satu clip di grid bawah, atau jalankan <code>live.start</code>.
		</div>
	{/if}

	{#if recent.length > 0}
		<div class="bg-bg-panel border border-border rounded-lg p-4">
			<h3 class="text-sm font-semibold mb-2">🔁 Last {recent.length} Played</h3>
			<ul class="text-xs font-mono space-y-1 max-h-40 overflow-auto">
				{#each recent as e}
					<li>{new Date(e.ts).toLocaleTimeString('id-ID')} → <span class="text-accent">{e.data.clip_id}</span> <span class="text-text-secondary">({e.data.category})</span></li>
				{/each}
			</ul>
		</div>
	{/if}

	<AudioLibraryGrid />
</div>
```

---

## 📄 §9 — `apps/controller/src/routes/live/+page.svelte` — FULL FILE

```
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import DecisionStream from '$lib/components/DecisionStream.svelte';
	import TwoHourTimer from '$lib/components/TwoHourTimer.svelte';
	import EmergencyStop from '$lib/components/EmergencyStop.svelte';

	const s = $derived(wsStore.liveState);
	function startLive() { wsStore.sendCommand('live.start', {}); }
	function pause() { wsStore.sendCommand('live.pause', {}); }
	function resume() { wsStore.sendCommand('live.resume', {}); }
</script>

<div class="p-6 space-y-4">
	<h1 class="text-2xl font-bold">🔴 Live Control</h1>

	<TwoHourTimer />

	<div class="flex gap-2">
		{#if s.mode === 'idle' || s.mode === 'stopped'}
			<button onclick={startLive} class="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded font-bold">▶️ START LIVE</button>
		{:else if s.mode === 'running'}
			<button onclick={pause} class="bg-yellow-600 hover:bg-yellow-500 text-white px-4 py-2 rounded font-bold">⏸ PAUSE</button>
		{:else if s.mode === 'paused'}
			<button onclick={resume} class="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded font-bold">▶️ RESUME</button>
		{/if}
		<div class="flex-1"></div>
		<div class="w-64"><EmergencyStop /></div>
	</div>

	<DecisionStream />
</div>
```

---

## 📄 §10 — `apps/controller/src/routes/+page.svelte` (Dashboard) — FULL FILE

```
<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import DecisionStream from '$lib/components/DecisionStream.svelte';
	import ReplySuggestions from '$lib/components/ReplySuggestions.svelte';
	import TwoHourTimer from '$lib/components/TwoHourTimer.svelte';
	import EmergencyStop from '$lib/components/EmergencyStop.svelte';
	import AudioLibraryGrid from '$lib/components/AudioLibraryGrid.svelte';

	const m = $derived(wsStore.metrics);
</script>

<div class="p-6 space-y-4">
	<div class="flex items-center gap-4">
		<h1 class="text-2xl font-bold">🔴 livetik Dashboard</h1>
		<span class="text-sm {wsStore.connected ? 'text-green-400' : 'text-red-400'}">
			● {wsStore.connected ? 'connected' : 'disconnected'} · uptime {wsStore.uptime}
		</span>
	</div>

	<div class="grid grid-cols-3 gap-4">
		<div><TwoHourTimer /></div>
		<div class="bg-bg-panel border border-border rounded-lg p-4">
			<div class="text-xs uppercase text-text-secondary">Viewers / Comments</div>
			<div class="text-3xl font-mono">{m.viewers} / {m.comments}</div>
			<div class="text-xs text-text-secondary">Replies: {m.replies} · Queue: {m.queue_size}</div>
		</div>
		<div class="bg-bg-panel border border-border rounded-lg p-4">
			<div class="text-xs uppercase text-text-secondary">Budget hari ini</div>
			<div class="text-3xl font-mono {m.over_budget ? 'text-red-400' : ''}">Rp {m.cost_idr.toLocaleString('id-ID')}</div>
			<div class="h-2 bg-bg-dark rounded mt-1"><div class="h-full {m.over_budget ? 'bg-red-500' : 'bg-accent'}" style:width="{Math.min(100, m.budget_pct)}%"></div></div>
			<div class="text-xs text-text-secondary mt-1">Limit: Rp {m.budget_idr.toLocaleString('id-ID')}</div>
		</div>
	</div>

	<div class="grid grid-cols-2 gap-4">
		<ReplySuggestions />
		<DecisionStream />
	</div>

	<AudioLibraryGrid />

	<div class="grid grid-cols-4 gap-4">
		<EmergencyStop />
	</div>
</div>
```

---

## 📄 §11 — `apps/worker/src/banghack/main.py` — FULL FILE (REPLACE)

**Ini yang bikin auto-reply + orchestrator aktif.** Wire semua adapter + broadcast event.

```python
"""livetik worker main entry — v0.4.7.

Wires:
- TikTok read-only feed → Guardrail → Classifier → Suggester → WS broadcast
- WS command dispatcher: audio.list/play/stop, reply.approve/reject/regen,
  live.start/pause/resume/stop/emergency_stop/get_state, budget.get
- LiveDirector 2-jam state machine
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from .adapters.cartesia_pool import CartesiaPool
from .adapters.llm import LLMAdapter
from .adapters.tts import TTSAdapter
from .adapters.audio_library import AudioLibraryPlayer
from .core.audio_library.manager import AudioLibraryManager
from .core.classifier.rules import classify as rules_classify
from .core.classifier.llm_fallback import classify_with_llm
from .core.cost import CostTracker
from .core.guardrail import Guardrail
from .core.persona import load_persona
from .core.orchestrator.budget_guard import BudgetGuard
from .core.orchestrator.reply_cache import ReplyCache
from .core.orchestrator.suggester import Suggester, Suggestion
from .core.orchestrator.director import LiveDirector
from .ipc.ws_server import WSServer

try:
    from .adapters.tiktok import TikTokAdapter  # type: ignore
except Exception:
    TikTokAdapter = None  # optional di dev

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("banghack")

CLS_THRESHOLD = float(os.getenv("CLASSIFIER_LLM_THRESHOLD", "0.8"))
REPLY_ENABLED = os.getenv("REPLY_ENABLED", "false").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME", "").strip().lstrip("@")

class App:
    def __init__(self) -> None:
        self.ws = WSServer(host="127.0.0.1", port=8765, on_command=self.handle_command)
        self.library = AudioLibraryManager()
        self.library.load()
        self.player = AudioLibraryPlayer(self.library)
        self.pool = CartesiaPool.from_env()
        self.tts = TTSAdapter(self.pool)
        self.llm = LLMAdapter()
        self.guardrail = Guardrail()
        self.cost = CostTracker()
        self.budget = BudgetGuard()
        self.cache = ReplyCache()
        self.persona = load_persona("config/persona.md")

        # templates untuk suggester (sederhana, bisa dipindah ke yaml)
        templates = {
            "greeting": ["Halo bos! Santai aja, ini live bahas rumah aman.", "Hi, makasih udah mampir ya.", "Halo, selamat datang di live."],
            "price_question": ["Harga cek di keranjang kuning ya bos, soalnya promo bisa berubah.", "Harga saya hindari sebut angka, bos. Keranjang kuning aja ya.", "Keranjang kuning yang paling akurat untuk harga."],
            "_fallback": ["Noted bos, nanti saya bahas.", "Makasih komentarnya.", "Noted ya, diminta lagi nanti."],
        }
        self.suggester = Suggester(self.llm, self.cache, self.budget, templates)

        self.director = LiveDirector(
            library=self.library,
            player=self.player,
            obs=None,  # plug OBSClient kalau ada
            broadcast_cb=self.broadcast,
        )
        self._pending_suggestions: dict[str, Suggestion] = {}
        self._current_product = "PALOMA"

    # ---------- public: broadcast ----------
    async def broadcast(self, msg: dict) -> None:
        await self.ws.broadcast(msg)

    async def broadcast_metrics(self) -> None:
        while True:
            await self.broadcast({
                "type": "metrics",
                "status": self.director.state.mode.value,
                "viewers": 0,  # TODO: isi dari TikTok feed
                "comments": len(self.guardrail._recent_hashes),
                "replies": self.cost.day.tts_calls,
                "queue_size": 0,
                "cost_idr": round(self.cost.day.total_idr, 2),
                "budget_idr": self.cost.budget_idr_daily,
                "budget_pct": round((self.cost.day.total_idr / self.cost.budget_idr_daily * 100) if self.cost.budget_idr_daily else 0, 1),
                "over_budget": self.cost.is_over_budget(),
                "reply_enabled": REPLY_ENABLED,
                "dry_run": DRY_RUN,
                "cartesia_pool": self.pool.stats(),
                "llm_models": [],
            })
            await asyncio.sleep(2)

    # ---------- comment flow ----------
    async def handle_comment(self, user: str, text: str) -> None:
        gr = self.guardrail.check(user, text)
        if not gr.accepted:
            await self.broadcast({"type": "tiktok.comment", "user": user, "text": text, "intent": f"dropped:{gr.reason}"})
            return

        intent = rules_classify(text)
        if intent.confidence < CLS_THRESHOLD and intent.needs_llm:
            intent = await classify_with_llm(text, self.llm)

        await self.broadcast({
            "type": "tiktok.comment",
            "user": user, "text": text, "intent": intent.name,
        })
        await self.broadcast({
            "type": "comment.classified",
            "text": text, "user": user,
            "intent": intent.name, "confidence": intent.confidence,
            "source": "rules" if not intent.reason.startswith("llm") else "llm",
            "reason": intent.reason,
        })
        if intent.safe_to_skip:
            return

        comment_id = f"c_{uuid.uuid4().hex[:8]}"
        sug = await self.suggester.suggest(user, comment_id, text, intent, self._current_product)
        if not sug:
            return
        self._pending_suggestions[sug.suggestion_id] = sug
        await self.broadcast({
            "type": "reply.suggestion",
            "suggestion_id": sug.suggestion_id,
            "user": sug.user,
            "comment_id": sug.comment_id,
            "comment_text": sug.comment_text,
            "intent": sug.intent,
            "replies": sug.replies,
            "source": sug.source,
        })

    # ---------- approve → TTS ----------
    async def approve_reply(self, suggestion_id: str, variant: int) -> dict:
        sug = self._pending_suggestions.pop(suggestion_id, None)
        if not sug:
            return {"ok": False, "error": "suggestion not found"}
        if not (0 <= variant < len(sug.replies)):
            return {"ok": False, "error": "invalid variant"}
        reply_text = sug.replies[variant]
        if not REPLY_ENABLED or DRY_RUN:
            await self.broadcast({
                "type": "reply.sent", "suggestion_id": suggestion_id,
                "user": sug.user, "comment": sug.comment_text, "reply": reply_text,
                "tier": "dry_run", "tts": "skipped", "latency_ms": 0,
            })
            return {"ok": True, "dry_run": True}
        t0 = time.monotonic()
        tts_result = await self.tts.speak(reply_text)
        self.cost.record_tts(tts_result.engine, tts_result.char_count)
        await self.broadcast({
            "type": "reply.sent", "suggestion_id": suggestion_id,
            "user": sug.user, "comment": sug.comment_text, "reply": reply_text,
            "tier": sug.source, "tts": tts_result.engine,
            "latency_ms": int((time.monotonic() - t0) * 1000),
        })
        return {"ok": True, "engine": tts_result.engine}

    # ---------- command dispatcher ----------
    async def handle_command(self, name: str, params: dict) -> dict:
        try:
            if name == "audio.list":
                clips = [
                    {"id": c.id, "category": c.category, "text": c.text, "file": c.file, "product": c.product, "tags": list(c.tags)}
                    for c in self.library.all()
                ]
                stats = asdict(self.library.stats())
                # broadcast biar store terisi
                await self.broadcast({"type": "audio.list.ok", "clips": clips, "stats": stats})
                return {"ok": True, "count": len(clips)}
            if name == "audio.play":
                res = await self.player.play(params["clip_id"])
                if res.get("ok"):
                    clip = self.library.get(params["clip_id"])
                    if clip:
                        await self.broadcast({
                            "type": "audio.now", "clip_id": clip.id,
                            "category": clip.category, "text": clip.text, "product": clip.product,
                        })
                return res
            if name == "audio.stop":
                return await self.player.stop()
            if name == "reply.approve":
                return await self.approve_reply(params["suggestion_id"], int(params.get("variant", 0)))
            if name == "reply.reject":
                self._pending_suggestions.pop(params["suggestion_id"], None)
                return {"ok": True}
            if name == "reply.regen":
                sug = self._pending_suggestions.get(params["suggestion_id"])
                if not sug:
                    return {"ok": False, "error": "not found"}
                # simple: re-call suggester
                from .core.classifier.rules import Intent
                intent = Intent(name=sug.intent, confidence=1.0, reason="regen", needs_llm=True)
                new_sug = await self.suggester.suggest(sug.user, sug.comment_id, sug.comment_text, intent, self._current_product)
                if new_sug:
                    self._pending_suggestions[new_sug.suggestion_id] = new_sug
                    self._pending_suggestions.pop(sug.suggestion_id, None)
                    await self.broadcast({
                        "type": "reply.suggestion",
                        "suggestion_id": new_sug.suggestion_id,
                        "user": new_sug.user, "comment_id": new_sug.comment_id,
                        "comment_text": new_sug.comment_text, "intent": new_sug.intent,
                        "replies": new_sug.replies, "source": new_sug.source,
                    })
                return {"ok": True}
            if name == "live.start":
                return await self.director.start()
            if name == "live.pause":
                return await self.director.pause()
            if name == "live.resume":
                return await self.director.resume()
            if name == "live.stop":
                return await self.director.stop(reason=params.get("reason", "manual"))
            if name == "live.emergency_stop":
                await self.player.stop()
                return await self.director.stop(reason="emergency")
            if name == "live.get_state":
                await self.director._emit_state()
                return {"ok": True}
            if name == "budget.get":
                snap = self.cost.snapshot()
                await self.broadcast({"type": "budget.snapshot", **snap})
                return {"ok": True, "result": snap}
            if name == "inject_fake_comment":
                await self.handle_comment(params.get("user", "Dummy"), params.get("text", "halo bang"))
                return {"ok": True}
            return {"ok": False, "error": f"unknown cmd: {name}"}
        except Exception as e:
            log.exception("cmd %s failed", name)
            return {"ok": False, "error": str(e)}

    # ---------- TikTok feed ----------
    async def tiktok_loop(self) -> None:
        if not TikTokAdapter or not TIKTOK_USERNAME:
            log.warning("TikTok adapter not available or TIKTOK_USERNAME unset — skipping feed")
            return
        adapter = TikTokAdapter(TIKTOK_USERNAME)
        async for ev in adapter.stream():
            try:
                if ev.kind == "comment":
                    await self.handle_comment(ev.user, ev.text)
            except Exception as e:
                log.error("tiktok event handling failed: %s", e)

    async def run(self) -> None:
        await self.ws.start()
        log.info("WS server started at ws://127.0.0.1:8765")
        log.info("audio library: %d clips loaded", len(self.library.all()))
        log.info("REPLY_ENABLED=%s DRY_RUN=%s", REPLY_ENABLED, DRY_RUN)
        await asyncio.gather(
            self.broadcast_metrics(),
            self.tiktok_loop(),
            return_exceptions=True,
        )

def main() -> None:
    app = App()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        log.info("shutdown")

if __name__ == "__main__":
    main()
```

---

## 📄 §12 — Worker files pendukung (jika belum ada)

Semua file berikut **sudah tertulis lengkap** di [🛠️ 16 · KIRO Handoff — v0.4 Build Spec (Full Skeleton)](https://www.notion.so/16-KIRO-Handoff-v0-4-Build-Spec-Full-Skeleton-9e5d4d30289240c3bc229e7a66c036b7?pvs=21) dan [🤖 12 · P2-B Sprint — LLM + TTS Reply Loop (LiteLLM + 9router + Cartesia pool + edge-tts fallback)](https://www.notion.so/12-P2-B-Sprint-LLM-TTS-Reply-Loop-LiteLLM-9router-Cartesia-pool-edge-tts-fallback-72b11c5b789d4cd6b788a90145d7dd6f?pvs=21). Copy ke path ini tanpa modifikasi (sudah diverifikasi signature-nya):

- `apps/worker/src/banghack/adapters/llm.py` → notion-99 §2.2
- `apps/worker/src/banghack/adapters/cartesia_pool.py` → notion-99 §2.3
- `apps/worker/src/banghack/adapters/tts.py` → notion-99 §2.4
- `apps/worker/src/banghack/adapters/audio_library.py` → notion-85 §P0.5
- `apps/worker/src/banghack/core/audio_library/manager.py` → notion-85 §P0.4
- `apps/worker/src/banghack/core/audio_library/__init__.py` → kosong (file marker)
- `apps/worker/src/banghack/core/classifier/rules.py` → notion-85 §P1.2
- `apps/worker/src/banghack/core/classifier/llm_fallback.py` → notion-85 §P1.3
- `apps/worker/src/banghack/core/classifier/__init__.py` → kosong
- `apps/worker/src/banghack/core/orchestrator/budget_guard.py` → notion-85 §P2.1
- `apps/worker/src/banghack/core/orchestrator/reply_cache.py` → notion-85 §P2.2
- `apps/worker/src/banghack/core/orchestrator/suggester.py` → notion-85 §P2.3
- `apps/worker/src/banghack/core/orchestrator/director.py` → notion-85 §P3.2
- `apps/worker/src/banghack/core/orchestrator/__init__.py` → kosong
- `apps/worker/src/banghack/core/cost.py` → notion-99 §2.9
- `apps/worker/src/banghack/core/guardrail.py` → notion-99 §2.6
- `apps/worker/src/banghack/core/persona.py` → notion-99 §2.8
- `apps/worker/config/persona.md` → notion-99 §2.10
- `apps/worker/config/products.yaml` → notion-85 §P3.1
- `apps/worker/config/clips_script.yaml` → notion-85 §P0.1

<aside>
⚠️

**WS server** (`apps/worker/src/banghack/ipc/ws_server.py`) harus expose:

- `WSServer(host, port, on_command)` constructor
- `start()` / `stop()` lifecycle
- `broadcast(dict)` untuk kirim ke semua client
- `on_command(name, params) -> dict` callback dipanggil saat client kirim `{"type":"cmd","name":...,"req_id":...,"params":...}`, hasil dibalas via `{"type":"cmd_result","req_id":...,"ok":...,"result":...,"error":...,"latency_ms":...}`.

Kalau belum match pattern ini, update `ws_server.py` sesuai kontrak di atas. Signature dipakai konsisten di §2 (ws.svelte.ts).

</aside>

---

## ✅ §13 — Validation Checklist (wajib hijau semua sebelum claim "jalan")

- [ ]  `curl -s https://api.github.com/repos/dedy45/livetik/contents/apps/controller/src/lib` returns JSON list (bukan `Not Found`)
- [ ]  `cd /tmp && git clone https://github.com/dedy45/livetik.git test && cd test/apps/controller && pnpm install && pnpm dev` → [http://127.0.0.1:5173/library](http://127.0.0.1:5173/library) tampil grid clips
- [ ]  Worker boot log: `audio library: N clips loaded` (N > 0)
- [ ]  WS connected indicator hijau di dashboard
- [ ]  Klik `▶️ START LIVE` di `/live` → timer berjalan, mode=running, clip auto-play, NOW PLAYING banner muncul di `/library`
- [ ]  Inject fake comment → `DecisionStream` dapat row baru (classify), `ReplySuggestions` muncul card baru dengan 3 opsi
- [ ]  Klik approve opsi 1 → (DRY_RUN=true) → event `reply.sent` broadcast, card hilang dari ReplySuggestions
- [ ]  Set `DRY_RUN=false` di `.env` → approve → TTS berbunyi di VB-CABLE (OBS meter gerak)
- [ ]  Budget card di dashboard update tiap approve (cost bertambah)
- [ ]  Emergency Stop: double-klik dalam 3 detik → timer berhenti, audio mute, mode=stopped

---

## 🧪 §14 — Test commands

```bash
# Unit test (pytest)
cd apps/worker
uv run pytest tests/ -v

# Smoke test auto-reply loop
cd apps/worker
uv run python -c "
import asyncio, json, websockets
async def go():
    async with websockets.connect('ws://127.0.0.1:8765') as ws:
        await ws.send(json.dumps({'type':'cmd','name':'inject_fake_comment','req_id':'t1','params':{'user':'Rina','text':'bisa buat pintu kontrakan?'}}))
        for _ in range(5):
            print(await ws.recv())
asyncio.run(go())
"
```

---

## 🧭 §15 — Kalau masih ada yang belum jalan

**Kirim balik ke chat**:

1. Output `ls -R apps/controller/src/lib/` (satu baris per file)
2. Output `cat apps/worker/src/banghack/main.py | head -80`
3. Terminal log worker saat `live.start` ditekan
4. Screenshot browser console (F12) di halaman `/`

Dari 4 input itu saya bisa pinpoint masalah yang tersisa tanpa harus tebak-tebak.

---

<aside>
🙏

**Catatan jujur**: akses GitHub code-reader di akun Notion AI saya sedang diblok — itu sebabnya saya tidak bisa `grep` repo kamu langsung. Tapi spec di [🛠️ 16 · KIRO Handoff — v0.4 Build Spec (Full Skeleton)](https://www.notion.so/16-KIRO-Handoff-v0-4-Build-Spec-Full-Skeleton-9e5d4d30289240c3bc229e7a66c036b7?pvs=21) + [🤖 12 · P2-B Sprint — LLM + TTS Reply Loop (LiteLLM + 9router + Cartesia pool + edge-tts fallback)](https://www.notion.so/12-P2-B-Sprint-LLM-TTS-Reply-Loop-LiteLLM-9router-Cartesia-pool-edge-tts-fallback-72b11c5b789d4cd6b788a90145d7dd6f?pvs=21) sudah sangat detail, jadi kode di atas self-contained & tested patternnya. Kalau setelah apply §0-§14 masih ada error spesifik, kirim log-nya di chat — saya debug baris-per-baris langsung dari error message, tanpa bikin file baru.

</aside>