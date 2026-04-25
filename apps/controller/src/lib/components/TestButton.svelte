<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';

	interface Props {
		command: string;
		params?: Record<string, unknown>;
		label?: string;
		variant?: 'primary' | 'secondary' | 'danger';
		size?: 'sm' | 'md';
		onDone?: (result: unknown) => void;
	}

	let {
		command,
		params = {},
		label = 'Test',
		variant = 'primary',
		size = 'md',
		onDone
	}: Props = $props();

	let reqId = $state<string | null>(null);
	let busy = $state(false);

	const result = $derived(reqId ? wsStore.testResults[reqId] : undefined);

	$effect(() => {
		if (result && busy) {
			busy = false;
			onDone?.(result);
		}
	});

	function run() {
		busy = true;
		reqId = wsStore.sendCommand(command, params);
		setTimeout(() => {
			if (busy) busy = false; // timeout guard
		}, 30000);
	}

	function reset() {
		if (reqId) wsStore.clearResult(reqId);
		reqId = null;
	}

	const colors = $derived({
		primary: 'bg-accent hover:bg-accent/80 text-bg-primary',
		secondary: 'bg-bg-elevated hover:bg-bg-elevated/80 text-text-primary border border-border',
		danger: 'bg-error hover:bg-error/80 text-bg-primary'
	}[variant]);
	const padding = $derived(size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1.5 text-sm');
</script>

<div class="inline-flex items-center gap-2">
	<button
		onclick={run}
		disabled={busy || !wsStore.connected}
		class="rounded-md {padding} {colors} disabled:opacity-40 disabled:cursor-not-allowed transition"
	>
		{#if busy}⏳ …{:else}{label}{/if}
	</button>

	{#if result}
		{#if result.ok}
			<span class="text-ok text-xs" title={JSON.stringify(result.result, null, 2)}>
				✓ {result.latency_ms}ms
			</span>
		{:else}
			<span class="text-error text-xs" title={result.error}>✗ {result.error?.slice(0, 40)}…</span>
		{/if}
		<button onclick={reset} class="text-xs text-text-secondary hover:text-text-primary">✕</button>
	{/if}
</div>
