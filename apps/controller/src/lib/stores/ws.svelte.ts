// Svelte 5 runes store — import via `import { wsStore } from '$lib/stores/ws.svelte';`
type Metrics = {
	status: string;
	uptime_s: number;
	viewers: number;
	comments: number;
	replies: number;
	gifts: number;
	joins: number;
	queue_size: number;
	latency_p95_ms: number;
	cost_idr: number;
	budget_idr: number;
	budget_pct: number;
	over_budget: boolean;
	mode: string;
	reply_enabled: boolean;
	dry_run: boolean;
	cartesia_pool: Array<{
		key: string;
		calls: number;
		total_errors: number;
		exhausted: boolean;
		cooldown_s: number;
	}>;
	llm_models: Array<{
		id: string;
		model: string;
		api_base: string;
		timeout: number;
	}>;
	by_tier: Record<string, number>;
	llm_calls: number;
	tts_calls: number;
};

type ReplyEntry = {
	ts: number;
	user: string;
	comment: string;
	reply: string;
	tier: string;
	tts: string;
	latency_ms: number;
};

type TikTokEntry = {
	ts: number;
	event_type: string;
	user: string;
	text: string;
	count: number;
};

type TestResult = {
	req_id: string;
	name: string;
	ok: boolean;
	latency_ms?: number;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	result?: any;
	error?: string;
	ts: number;
};

type ErrorEntry = {
	ts: number;
	category: string;
	user?: string;
	detail: string;
};

type ClassifiedComment = {
	ts: number;
	comment_id: string;
	user: string;
	text: string;
	intent: string;
	confidence: number;
	reason: string;
	method: string;
};

type ReplySuggestion = {
	ts: number;
	comment_id: string;
	comment_text: string;
	user: string;
	intent: string;
	replies: string[];
	source: string;
	cached: boolean;
};

const DEFAULTS: Metrics = {
	status: 'disconnected',
	uptime_s: 0,
	viewers: 0,
	comments: 0,
	replies: 0,
	gifts: 0,
	joins: 0,
	queue_size: 0,
	latency_p95_ms: 0,
	cost_idr: 0,
	budget_idr: 0,
	budget_pct: 0,
	over_budget: false,
	mode: 'unknown',
	reply_enabled: false,
	dry_run: false,
	cartesia_pool: [],
	llm_models: [],
	by_tier: {},
	llm_calls: 0,
	tts_calls: 0
};

function fmtUptime(s: number): string {
	const h = Math.floor(s / 3600).toString().padStart(2, '0');
	const m = Math.floor((s % 3600) / 60).toString().padStart(2, '0');
	const sec = Math.floor(s % 60).toString().padStart(2, '0');
	return `${h}:${m}:${sec}`;
}

export function createWsStore(url = 'ws://127.0.0.1:8765') {
	let connected = $state(false);
	let metrics = $state<Metrics>({ ...DEFAULTS });
	let lastEventTs = $state(0);
	let comments = $state<TikTokEntry[]>([]);
	let tiktokEvents = $state<TikTokEntry[]>([]);
	let replies = $state<ReplyEntry[]>([]);
	let events = $state<Array<{ ts: number; type: string; payload: unknown }>>([]);
	let testResults = $state<Map<string, TestResult>>(new Map());
	let errorLog = $state<ErrorEntry[]>([]);
	let classifiedComments = $state<ClassifiedComment[]>([]);
	let replySuggestions = $state<ReplySuggestion[]>([]);
	let availableCommands = $state<string[]>([]);
	let audioNow = $state<string | null>(null);
	let liveStateRaw = $state<Record<string, unknown>>({});
	let ws: WebSocket | null = null;
	let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

	function connect() {
		if (typeof window === 'undefined') return;
		ws = new WebSocket(url);
		ws.onopen = () => {
			connected = true;
		};
		ws.onclose = () => {
			connected = false;
			metrics = { ...DEFAULTS };
			reconnectTimer = setTimeout(connect, 2000);
		};
		ws.onerror = () => ws?.close();
		ws.onmessage = (ev) => {
			try {
				const msg = JSON.parse(ev.data);
				lastEventTs = Date.now();
				if (msg.type === 'metrics') {
					metrics = { ...metrics, ...msg };
				} else if (msg.type === 'tiktok_event') {
					const entry: TikTokEntry = {
						ts: lastEventTs,
						event_type: msg.event_type,
						user: msg.user,
						text: msg.text,
						count: msg.count
					};
					tiktokEvents = [entry, ...tiktokEvents].slice(0, 200);
					if (entry.event_type === 'comment') {
						comments = [entry, ...comments].slice(0, 100);
					}
				} else if (msg.type === 'reply_event') {
					const r: ReplyEntry = {
						ts: lastEventTs,
						user: msg.user,
						comment: msg.comment,
						reply: msg.reply,
						tier: msg.tier,
						tts: msg.tts,
						latency_ms: msg.latency_ms
					};
					replies = [r, ...replies].slice(0, 50);
				} else if (msg.type === 'hello') {
					availableCommands = msg.commands ?? [];
				} else if (msg.type === 'cmd_result') {
					const r: TestResult = {
						req_id: msg.req_id,
						name: msg.name ?? 'unknown',
						ok: msg.ok,
						latency_ms: msg.latency_ms,
						result: msg.result,
						error: msg.error,
						ts: Date.now()
					};
					testResults.set(msg.req_id, r);
					testResults = new Map(testResults); // trigger reactivity
				} else if (msg.type === 'error_event') {
					errorLog = [
						{ ts: lastEventTs, category: msg.category, user: msg.user, detail: msg.detail },
						...errorLog
					].slice(0, 200);
				} else if (msg.type === 'audio.now') {
					audioNow = (msg.clip_id as string) ?? null;
				} else if (msg.type === 'audio.done' || msg.type === 'error.audio_playback') {
					audioNow = null;
				} else if (msg.type === 'comment.classified') {
					const cc: ClassifiedComment = {
						ts: lastEventTs,
						comment_id: (msg.comment_id as string) ?? '',
						user: (msg.user as string) ?? '',
						text: (msg.text as string) ?? '',
						intent: (msg.intent as string) ?? 'other',
						confidence: (msg.confidence as number) ?? 0,
						reason: (msg.reason as string) ?? '',
						method: (msg.method as string) ?? 'rule',
					};
					classifiedComments = [cc, ...classifiedComments].slice(0, 200);
				} else if (msg.type === 'reply.suggestion') {
					const rs: ReplySuggestion = {
						ts: lastEventTs,
						comment_id: (msg.comment_id as string) ?? '',
						comment_text: (msg.comment_text as string) ?? '',
						user: (msg.user as string) ?? '',
						intent: (msg.intent as string) ?? 'other',
						replies: (msg.replies as string[]) ?? [],
						source: (msg.source as string) ?? 'template',
						cached: (msg.cached as boolean) ?? false,
					};
					replySuggestions = [rs, ...replySuggestions].slice(0, 50);
				} else if (msg.type === 'live.state' || msg.type === 'live.tick') {
					liveStateRaw = {
						mode: (msg.mode as string) ?? 'IDLE',
						phase: (msg.phase as string) ?? '',
						phase_idx: (msg.phase_idx as number) ?? 0,
						phase_total: (msg.phase_total as number) ?? 0,
						product: (msg.product as string) ?? '',
						elapsed_s: (msg.elapsed_s as number) ?? 0,
						remaining_s: (msg.remaining_s as number) ?? 7200,
						total_decisions: (msg.total_decisions as number) ?? 0,
					};
				}
				events = [{ ts: lastEventTs, type: msg.type, payload: msg }, ...events].slice(0, 50);
			} catch (e) {
				console.error('ws parse error', e);
			}
		};
	}

	connect();

	function sendCommand(name: string, params: Record<string, unknown> = {}): string {
		const req_id = `${name}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
		if (ws?.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify({ type: 'cmd', name, req_id, params }));
		} else {
			testResults.set(req_id, {
				req_id, name, ok: false, error: 'WebSocket not connected', ts: Date.now()
			});
			testResults = new Map(testResults);
		}
		return req_id;
	}

	function getResult(req_id: string): TestResult | undefined {
		return testResults.get(req_id);
	}

	function clearResult(req_id: string): void {
		testResults.delete(req_id);
		testResults = new Map(testResults);
	}

	return {
		get connected() { return connected; },
		get metrics() { return metrics; },
		get uptime() { return fmtUptime(metrics.uptime_s); },
		get events() { return events; },
		get comments() { return comments; },
		get tiktokEvents() { return tiktokEvents; },
		get replies() { return replies; },
		get lastEventTs() { return lastEventTs; },
		get testResults() { return testResults; },
		get errorLog() { return errorLog; },
		get classifiedComments() { return classifiedComments; },
		get replySuggestions() { return replySuggestions; },
		get availableCommands() { return availableCommands; },
		get audioNow() { return audioNow; },
		get liveStateRaw() { return liveStateRaw; },
		sendCommand,
		getResult,
		clearResult,
		dispose() {
			if (reconnectTimer) clearTimeout(reconnectTimer);
			ws?.close();
		}
	};
}

export const wsStore = createWsStore();
