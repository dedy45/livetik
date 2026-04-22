<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';

	type FilterType = 'all' | 'llm' | 'tts' | 'cartesia' | 'ninerouter' | 'guardrail' | 'tiktok';

	let filter = $state<FilterType>('all');

	const errors = $derived(wsStore.errorLog ?? []);
	const filtered = $derived(filter === 'all' ? errors : errors.filter((e) => e.category === filter));

	function copyToClipboard(text: string) {
		navigator.clipboard.writeText(text);
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Errors ({errors.length})</h2>
		<div class="text-xs text-text-secondary">Stream dari worker · keep 200 terakhir</div>
	</div>

	<div class="flex gap-2 flex-wrap">
		{#each ['all', 'llm', 'tts', 'cartesia', 'ninerouter', 'guardrail', 'tiktok'] as f}
			<button
				onclick={() => (filter = f as FilterType)}
				class="px-3 py-1 rounded-md text-sm border border-border {filter === f
					? 'bg-accent text-bg-primary'
					: 'bg-bg-panel text-text-secondary hover:bg-bg-elevated'}"
			>
				{f}
			</button>
		{/each}
	</div>

	<div class="bg-bg-panel border border-border rounded-lg">
		{#if filtered.length === 0}
			<p class="p-6 text-text-secondary text-sm">
				{errors.length === 0
					? 'Belum ada error — artinya sistem sehat ✅'
					: `Tidak ada error kategori ${filter}`}
			</p>
		{:else}
			<ul class="divide-y divide-border max-h-[75vh] overflow-auto">
				{#each filtered as err, i (err.ts + i)}
					<li class="px-4 py-3 text-sm flex items-start gap-3">
						<span class="text-accent font-mono text-xs shrink-0 w-20">
							{new Date(err.ts).toLocaleTimeString('id-ID')}
						</span>
						<span class="text-error text-xs shrink-0 w-20 uppercase">{err.category}</span>
						{#if err.user}<span class="text-text-secondary shrink-0">{err.user}</span>{/if}
						<span class="text-text-primary flex-1 font-mono text-xs">{err.detail}</span>
						<button
							onclick={() => copyToClipboard(`[${err.category}] ${err.detail}`)}
							class="text-xs text-text-secondary hover:text-accent shrink-0"
						>
							copy
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</div>
