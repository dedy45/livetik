<script lang="ts">
	import { onMount } from 'svelte';
	import { liveStateStore } from '$lib/stores/live_state.svelte';

	let localElapsed = $state(0);
	let ticker: ReturnType<typeof setInterval> | null = null;

	const ls = $derived(liveStateStore.liveState);
	const remaining = $derived(
		Math.max(0, ls.remaining_s - (ls.mode === 'RUNNING' ? localElapsed : 0))
	);
	const progressPct = $derived(
		Math.min(
			100,
			Math.round(((ls.elapsed_s + (ls.mode === 'RUNNING' ? localElapsed : 0)) / 7200) * 100)
		)
	);

	// Reset local elapsed when we get a new tick from server
	$effect(() => {
		const _ = ls.elapsed_s; // track dependency
		localElapsed = 0;
	});

	onMount(() => {
		ticker = setInterval(() => {
			if (ls.mode === 'RUNNING') localElapsed += 1;
		}, 1000);
		return () => {
			if (ticker) clearInterval(ticker);
		};
	});

	function fmtTime(s: number): string {
		const m = Math.floor(s / 60)
			.toString()
			.padStart(2, '0');
		const sec = Math.floor(s % 60)
			.toString()
			.padStart(2, '0');
		return `${m}:${sec}`;
	}

	const timerColor = $derived(
		remaining < 120 ? 'text-error animate-pulse' : remaining < 600 ? 'text-warn' : 'text-ok'
	);

	const progressColor = $derived(
		remaining < 120 ? 'bg-error' : remaining < 600 ? 'bg-warn' : 'bg-ok'
	);

	const modeBadgeClass = $derived(
		ls.mode === 'RUNNING'
			? 'bg-ok text-bg'
			: ls.mode === 'PAUSED'
				? 'bg-warn text-bg'
				: ls.mode === 'STOPPED'
					? 'bg-error text-bg'
					: 'bg-bg-elevated text-text-secondary'
	);
</script>

<div class="bg-bg-panel border border-border rounded-lg p-6">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-lg font-semibold">Live Session</h3>
		<span class="text-xs px-2 py-1 rounded {modeBadgeClass}">{ls.mode}</span>
	</div>

	<!-- Big timer display -->
	<div class="text-center mb-4">
		<div class="text-6xl font-mono font-bold {timerColor}">
			{fmtTime(remaining)}
		</div>
		<div class="text-sm text-text-secondary mt-1">remaining</div>
	</div>

	<!-- Progress bar -->
	<div class="w-full bg-bg-elevated rounded-full h-3 overflow-hidden mb-4">
		<div class="h-full transition-all {progressColor}" style="width: {progressPct}%"></div>
	</div>

	<!-- Phase info -->
	{#if ls.phase}
		<div class="flex items-center gap-2 text-sm text-text-secondary mb-4">
			<span>Phase:</span>
			<span class="text-text-primary font-medium">{ls.phase}</span>
			{#if ls.product}
				<span>·</span>
				<span class="text-accent">{ls.product}</span>
			{/if}
		</div>
	{/if}

	<!-- Controls -->
	<div class="flex gap-2">
		{#if ls.mode === 'IDLE' || ls.mode === 'STOPPED'}
			<button
				onclick={() => liveStateStore.startLive()}
				class="flex-1 px-4 py-2 rounded bg-ok text-bg font-semibold hover:opacity-80 transition-opacity"
			>
				▶ Start Live
			</button>
		{:else if ls.mode === 'RUNNING'}
			<button
				onclick={() => liveStateStore.pauseLive()}
				class="flex-1 px-4 py-2 rounded bg-warn text-bg font-semibold hover:opacity-80 transition-opacity"
			>
				⏸ Pause
			</button>
			<button
				onclick={() => liveStateStore.stopLive()}
				class="px-4 py-2 rounded border border-border text-text-secondary hover:text-error hover:border-error transition-colors"
			>
				⏹ Stop
			</button>
		{:else if ls.mode === 'PAUSED'}
			<button
				onclick={() => liveStateStore.resumeLive()}
				class="flex-1 px-4 py-2 rounded bg-ok text-bg font-semibold hover:opacity-80 transition-opacity"
			>
				▶ Resume
			</button>
			<button
				onclick={() => liveStateStore.stopLive()}
				class="px-4 py-2 rounded border border-border text-text-secondary hover:text-error hover:border-error transition-colors"
			>
				⏹ Stop
			</button>
		{/if}
	</div>
</div>
