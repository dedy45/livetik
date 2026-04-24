// Live Director state store — Svelte 5 runes
// NOTE: $effect is NOT used here — only $state and $derived (safe for SSR)
import { wsStore } from './ws.svelte';

export type LiveState = {
	mode: string;
	phase: string;
	phase_idx: number;
	phase_total: number;
	product: string;
	elapsed_s: number;
	remaining_s: number;
	total_decisions: number;
};

function createLiveStateStore() {
	// Derive liveState directly from wsStore.liveStateRaw — no $effect needed
	const liveState = $derived<LiveState>({
		mode: (wsStore.liveStateRaw.mode as string) ?? 'IDLE',
		phase: (wsStore.liveStateRaw.phase as string) ?? '',
		phase_idx: (wsStore.liveStateRaw.phase_idx as number) ?? 0,
		phase_total: (wsStore.liveStateRaw.phase_total as number) ?? 0,
		product: (wsStore.liveStateRaw.product as string) ?? '',
		elapsed_s: (wsStore.liveStateRaw.elapsed_s as number) ?? 0,
		remaining_s: (wsStore.liveStateRaw.remaining_s as number) ?? 7200,
		total_decisions: (wsStore.liveStateRaw.total_decisions as number) ?? 0,
	});

	const remainingS = $derived(liveState.remaining_s);
	const progressPct = $derived(Math.round((liveState.elapsed_s / 7200) * 100));
	const isRunning = $derived(liveState.mode === 'RUNNING');

	function startLive() {
		wsStore.sendCommand('live.start', {});
	}

	function stopLive() {
		wsStore.sendCommand('live.stop', {});
	}

	function pauseLive() {
		wsStore.sendCommand('live.pause', {});
	}

	function resumeLive() {
		wsStore.sendCommand('live.resume', {});
	}

	function emergencyStop() {
		wsStore.sendCommand('live.emergency_stop', { operator_id: 'operator' });
	}

	return {
		get liveState() {
			return liveState;
		},
		get remainingS() {
			return remainingS;
		},
		get progressPct() {
			return progressPct;
		},
		get isRunning() {
			return isRunning;
		},
		startLive,
		stopLive,
		pauseLive,
		resumeLive,
		emergencyStop,
	};
}

export const liveStateStore = createLiveStateStore();
