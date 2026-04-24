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
