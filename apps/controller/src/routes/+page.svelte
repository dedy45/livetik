<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';

	const m = $derived(wsStore.metrics);
	const statusColor = $derived(
		m.status === 'live'
			? 'bg-ok'
			: m.status === 'connecting'
				? 'bg-warn'
				: m.status === 'idle'
					? 'bg-warn'
					: 'bg-error'
	);
	const statusText = $derived(
		m.status === 'idle' ? 'Idle (worker ready, TikTok belum connect)' : m.status
	);
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Dashboard</h2>
		<div class="flex items-center gap-3">
			<span class="flex items-center gap-2">
				<span class="w-3 h-3 rounded-full {statusColor}"></span>
				<span class="text-sm text-text-secondary">{statusText}</span>
			</span>
			<span class="text-sm text-text-secondary">Uptime: {wsStore.uptime}</span>
			<span class="px-3 py-1 bg-bg-elevated rounded-md text-sm">Queue: {m.queue_size}</span>
		</div>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Status</h3>
			<p class="text-3xl font-bold {m.status === 'connected' ? 'text-ok' : 'text-error'}">
				{m.status}
			</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Viewers</h3>
			<p class="text-3xl font-bold">{m.viewers}</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Comments</h3>
			<p class="text-3xl font-bold">{m.comments}</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Replies</h3>
			<p class="text-3xl font-bold">{m.replies}</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Latency (p95)</h3>
			<p class="text-3xl font-bold text-ok">{m.latency_p95_ms}ms</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Cost Today</h3>
			<p class="text-3xl font-bold text-ok">Rp {m.cost_idr.toLocaleString('id-ID')}</p>
		</div>
	</div>

	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">Recent Events</h3>
		{#if wsStore.events.length === 0}
			<p class="text-text-secondary text-sm">Menunggu event dari worker...</p>
		{:else}
			<ul class="space-y-1 text-sm font-mono">
				{#each wsStore.events.slice(0, 10) as ev (ev.ts)}
					<li class="text-text-secondary">
						<span class="text-accent">{new Date(ev.ts).toLocaleTimeString('id-ID')}</span>
						<span class="ml-2">{ev.type}</span>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</div>
