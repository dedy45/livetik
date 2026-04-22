<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';

	const m = $derived(wsStore.metrics);
	const comments = $derived(wsStore.comments);
	const allEvents = $derived(wsStore.tiktokEvents);

	let filter = $state<'all' | 'comment' | 'gift' | 'join' | 'like'>('comment');

	const filtered = $derived(
		filter === 'all' ? allEvents : allEvents.filter((e) => e.event_type === filter)
	);
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Live Monitor</h2>
		<div class="flex items-center gap-3 text-sm text-text-secondary">
			<span>Status: <span class="text-accent font-semibold">{m.status}</span></span>
			<span>Comments: {m.comments}</span>
			<span>Gifts: {m.gifts}</span>
			<span>Joins: {m.joins}</span>
		</div>
	</div>

	<div class="flex gap-2">
		{#each ['all', 'comment', 'gift', 'join', 'like'] as f}
			<button
				class="px-3 py-1 rounded-md text-sm border border-border {filter === f ? 'bg-accent text-bg-primary' : 'bg-bg-panel text-text-secondary hover:bg-bg-elevated'}"
				onclick={() => (filter = f as typeof filter)}
			>
				{f}
			</button>
		{/each}
	</div>

	<div class="bg-bg-panel border border-border rounded-lg">
		{#if filtered.length === 0}
			<p class="p-6 text-text-secondary text-sm">
				Menunggu event dari @interiorhack.id… pastikan worker jalan dan TikTok sedang live.
			</p>
		{:else}
			<ul class="divide-y divide-border max-h-[70vh] overflow-auto">
				{#each filtered as ev (ev.ts + ev.user + ev.text)}
					<li class="px-4 py-3 text-sm flex items-start gap-3">
						<span class="text-accent font-mono text-xs shrink-0">
							{new Date(ev.ts).toLocaleTimeString('id-ID')}
						</span>
						<span class="text-text-secondary shrink-0 w-16">{ev.event_type}</span>
						<span class="font-semibold shrink-0">{ev.user}</span>
						<span class="text-text-primary flex-1">
							{ev.text || (ev.count > 1 ? `×${ev.count}` : '')}
						</span>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</div>
