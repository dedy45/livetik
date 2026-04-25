// apps/controller/src/lib/stores/ws.svelte.ts
export type Metrics = {
	status: string;
	viewers: number; comments: number; gifts: number; joins: number;
	replies: number; queue_size: number; latency_p95_ms: number;
	cost_idr: number; budget_idr: number; budget_pct: number;
	over_budget: boolean; reply_enabled: boolean; dry_run: boolean;
	by_tier?: Record<string, number>;
	llm_calls?: number; tts_calls?: number;
	cartesia_pool: { key: string; calls: number; exhausted: boolean; cooldown_s: number }[];
	cartesia_voice_id?: string;
	cartesia_model?: string;
	cartesia_default_emotion?: string;
	llm_models: { id: string; model: string; tier: string }[];
	tiktok_username?: string;
	tiktok_running?: boolean;
	guardrail?: any;
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
	suggestion_id: string; user: string; comment_id: string;
	comment_text: string; intent: string; replies: string[];
	source: string; ts: number;
};

export type CmdResult = {
	ok: boolean; result?: any; error?: string; latency_ms?: number;
	pending?: boolean; timedOut?: boolean;
};

export type Toast = {
	id: number; kind: 'success' | 'error' | 'info' | 'warning';
	title: string; detail?: string; ts: number;
};

type ConnStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting';

const WS_URL = 'ws://127.0.0.1:8765';
const CMD_TIMEOUT_MS = 10_000;
const RECONNECT_DELAY_MS = 2_000;

function createStore() {
	let ws: WebSocket | null = $state(null);
	let connStatus = $state<ConnStatus>('connecting');
	let lastConnectError = $state<string | null>(null);
	let connectedAt = $state<number | null>(null);
	let reconnectAttempts = $state(0);

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
	const replies = $state<any[]>([]);
	const suggestions = $state<Suggestion[]>([]);
	const tiktokEvents = $state<any[]>([]);
	const errorLog = $state<{ ts: number; category: string; user?: string; detail: string }[]>([]);
	const decisions = $state<{ ts: number; kind: string; input: string; output: string; reasoning: string }[]>([]);
	const audioClips = $state<any[]>([]);
	let testResults = $state<Record<string, CmdResult>>({});
	const toasts = $state<Toast[]>([]);

	let nowPlaying = $state<any | null>(null);
	let reqIdSeq = 0;
	let toastSeq = 0;

	// Command queue for when WS is not yet open
	const pendingQueue: { name: string; reqId: string; params: any }[] = [];
	// Pending timeouts per reqId
	const pendingTimeouts = new Map<string, ReturnType<typeof setTimeout>>();
	// Awaiters for sendCommandAwait
	const awaiters = new Map<string, (r: CmdResult) => void>();

	function pushToast(t: Omit<Toast, 'id' | 'ts'>) {
		const toast: Toast = { id: ++toastSeq, ts: Date.now(), ...t };
		toasts.unshift(toast);
		if (toasts.length > 6) toasts.length = 6;
		// Auto-dismiss after 4s
		setTimeout(() => {
			const idx = toasts.findIndex(x => x.id === toast.id);
			if (idx >= 0) toasts.splice(idx, 1);
		}, 4000);
	}

	function dismissToast(id: number) {
		const idx = toasts.findIndex(x => x.id === id);
		if (idx >= 0) toasts.splice(idx, 1);
	}

	function connect() {
		if (typeof window === 'undefined') return;
		connStatus = reconnectAttempts > 0 ? 'reconnecting' : 'connecting';
		try {
			ws = new WebSocket(WS_URL);
		} catch (e: any) {
			lastConnectError = String(e?.message ?? e);
			connStatus = 'disconnected';
			setTimeout(connect, RECONNECT_DELAY_MS);
			return;
		}
		ws.onopen = () => {
			connStatus = 'connected';
			connectedAt = Date.now();
			reconnectAttempts = 0;
			lastConnectError = null;
			pushToast({ kind: 'success', title: '✅ WS connected', detail: WS_URL });
			// Flush queued commands
			while (pendingQueue.length > 0) {
				const c = pendingQueue.shift()!;
				_rawSend(c.name, c.reqId, c.params);
			}
			// Bootstrap state
			sendCommand('audio.list', {});
			sendCommand('live.get_state', {});
			sendCommand('budget.get', {});
			sendCommand('read_env', {});
		};
		ws.onclose = () => {
			if (connStatus === 'connected') {
				pushToast({ kind: 'warning', title: '⚠ WS disconnected', detail: 'Reconnecting in 2s...' });
			}
			connStatus = 'disconnected';
			reconnectAttempts++;
			setTimeout(connect, RECONNECT_DELAY_MS);
		};
		ws.onerror = (ev: any) => {
			lastConnectError = 'WS error — is worker running on port 8765?';
		};
		ws.onmessage = (ev) => {
			try { handleMessage(JSON.parse(ev.data)); }
			catch (e) { console.error('ws parse error:', e); }
		};
	}

	function _rawSend(name: string, reqId: string, params: any) {
		if (ws?.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify({ type: 'cmd', name, req_id: reqId, params }));
			// Start timeout
			const t = setTimeout(() => {
				const existing = testResults[reqId];
				if (!existing || existing.pending) {
					const timed: CmdResult = { ok: false, error: `timeout ${CMD_TIMEOUT_MS}ms`, timedOut: true };
					testResults[reqId] = timed;
					pushToast({ kind: 'error', title: `⏱ ${name} timeout`, detail: 'Worker tidak balas dalam 10 detik' });
					const aw = awaiters.get(reqId);
					if (aw) { aw(timed); awaiters.delete(reqId); }
				}
				pendingTimeouts.delete(reqId);
			}, CMD_TIMEOUT_MS);
			pendingTimeouts.set(reqId, t);
		}
	}

	function handleMessage(msg: any) {
		events.unshift({ ts: Date.now(), type: msg.type, data: msg });
		if (events.length > 200) events.length = 200;

		switch (msg.type) {
			case 'hello':
				pushToast({ kind: 'info', title: '🤖 Worker hello', detail: `${msg.server} v${msg.version} · ${msg.commands?.length ?? 0} commands` });
				break;
			case 'metrics':
				Object.assign(metrics, msg);
				break;
			case 'live.state':
				Object.assign(liveState, {
					mode: String(msg.mode || 'idle').toLowerCase(),
					session_id: msg.session_id ?? null,
					elapsed_s: msg.elapsed_s ?? 0,
					max_s: msg.max_s ?? 7200,
					phase: msg.phase, product: msg.product,
					phase_idx: msg.phase_idx ?? -1,
					phase_total: msg.phase_total ?? 0,
				});
				break;
			case 'live.tick':
				liveState.elapsed_s = msg.elapsed_s ?? liveState.elapsed_s;
				liveState.mode = String(msg.mode || liveState.mode).toLowerCase() as any;
				break;
			case 'tiktok.comment':
				comments.unshift({ ts: Date.now(), user: msg.user, text: msg.text, intent: msg.intent });
				if (comments.length > 100) comments.length = 100;
				break;
			case 'tiktok_event':
				tiktokEvents.unshift({ ts: Date.now(), ...msg });
				if (tiktokEvents.length > 200) tiktokEvents.length = 200;
				break;
			case 'comment.classified':
				decisions.unshift({
					ts: Date.now(), kind: 'classify',
					input: msg.text ?? '',
					output: `intent=${msg.intent} conf=${(msg.confidence ?? 0).toFixed(2)}`,
					reasoning: (msg.source ?? msg.method) === 'rules' || (msg.source ?? msg.method) === 'rule'
						? `rule:${msg.reason ?? ''}`
						: `llm:${msg.reason ?? ''}`,
				});
				if (decisions.length > 100) decisions.length = 100;
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
			case 'reply_event':
				replies.unshift({ ts: Date.now(), ...msg });
				if (msg.suggestion_id) {
					const idx = suggestions.findIndex(s => s.suggestion_id === msg.suggestion_id);
					if (idx >= 0) suggestions.splice(idx, 1);
				}
				if (replies.length > 50) replies.length = 50;
				break;
			case 'audio.list.ok':
				audioClips.splice(0, audioClips.length, ...(msg.clips ?? []));
				pushToast({ kind: 'success', title: '📚 Audio library loaded', detail: `${msg.clips?.length ?? 0} clips` });
				break;
			case 'audio.now':
				nowPlaying = {
					clip_id: msg.clip_id,
					category: msg.category ?? '',
					text: msg.text ?? msg.script_preview ?? '',
					product: msg.product,
					ts: Date.now(),
				};
				decisions.unshift({
					ts: Date.now(), kind: 'clip.play',
					input: msg.category ?? '', output: msg.clip_id ?? '',
					reasoning: (msg.text ?? msg.script_preview ?? '').slice(0, 80),
				});
				break;
			case 'audio.done':
				if (nowPlaying?.clip_id === msg.clip_id) nowPlaying = null;
				break;
			case 'error':
			case 'error_event':
			case 'error.audio_playback':
				errorLog.unshift({
					ts: Date.now(),
					category: msg.category ?? msg.type ?? 'unknown',
					user: msg.user,
					detail: msg.detail ?? JSON.stringify(msg),
				});
				pushToast({ kind: 'error', title: `❌ ${msg.category ?? 'error'}`, detail: msg.detail ?? '' });
				if (errorLog.length > 200) errorLog.length = 200;
				break;
			case 'cmd_result': {
				const rid = msg.req_id;
				const t = pendingTimeouts.get(rid);
				if (t) { clearTimeout(t); pendingTimeouts.delete(rid); }
				const cr: CmdResult = {
					ok: msg.ok, result: msg.result, error: msg.error, latency_ms: msg.latency_ms,
				};
				if (rid) testResults[rid] = cr;
				const aw = awaiters.get(rid);
				if (aw) { aw(cr); awaiters.delete(rid); }
				if (msg.ok) {
					pushToast({ kind: 'success', title: `✅ ${msg.name ?? 'cmd'} ok`, detail: `${msg.latency_ms ?? 0}ms` });
				} else {
					pushToast({ kind: 'error', title: `❌ ${msg.name ?? 'cmd'} failed`, detail: msg.error ?? '' });
				}
				break;
			}
		}
	}

	function sendCommand(name: string, params: any = {}): string {
		const reqId = `req-${++reqIdSeq}`;
		testResults[reqId] = { ok: false, pending: true };
		if (ws?.readyState === WebSocket.OPEN) {
			_rawSend(name, reqId, params);
		} else {
			pendingQueue.push({ name, reqId, params });
			pushToast({ kind: 'info', title: `📨 ${name} queued`, detail: 'menunggu WS connect...' });
		}
		return reqId;
	}

	function sendCommandAwait(name: string, params: any = {}): Promise<CmdResult> {
		const reqId = sendCommand(name, params);
		return new Promise<CmdResult>((resolve) => {
			awaiters.set(reqId, resolve);
		});
	}

	if (typeof window !== 'undefined') connect();

	return {
		get connected() { return connStatus === 'connected'; },
		get status() { return connStatus; },
		get lastConnectError() { return lastConnectError; },
		get reconnectAttempts() { return reconnectAttempts; },
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
		get toasts() { return toasts; },
		testResults,
		sendCommand,
		sendCommandAwait,
		dismissToast,
	};
}

export const wsStore = createStore();
