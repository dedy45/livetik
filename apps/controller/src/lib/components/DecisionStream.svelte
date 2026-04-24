<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';

	let filterIntent = $state('');

	const INTENT_COLORS: Record<string, string> = {
		greeting: 'bg-blue-500/20 text-blue-400',
		price_question: 'bg-yellow-500/20 text-yellow-400',
		stock_question: 'bg-green-500/20 text-green-400',
		buying_intent: 'bg-emerald-500/20 text-emerald-400',
		compatibility: 'bg-purple-500/20 text-purple-400',
		how_to_use: 'bg-indigo-500/20 text-indigo-400',
		objection: 'bg-orange-500/20 text-orange-400',
		forbidden_contact: 'bg-red-500/20 text-red-400',
		forbidden_link: 'bg-red-500/20 text-red-400',
		spam: 'bg-red-500/20 text-red-400',
		other: 'bg-gray-500/20 text-gray-400',
		empty: 'bg-gray-500/20 text-gray-400',
	};

	const ALL_INTENTS = Object.keys(INTENT_COLORS);

	const filtered = $derived(
		filterIntent
			? wsStore.classifiedComments.filter((c) => c.intent === filterIntent)
			: wsStore.classifiedComments
	);

	function intentColor(intent: string): string {
		return INTENT_COLORS[intent] ?? 'bg-gray-500/20 text-gray-400';
	}
</script>

<div class="bg-bg-panel border border-border rounded-lg p-6">
	<div class="flex items-center justify-between mb-4">
		<div class="flex items-center gap-3">
			<h3 class="text-lg font-semibold">Decision Stream</h3>
			<span class="text-xs px-2 py-0.5 rounded bg-bg-elevated text-text-secondary">
				{filtered.length} entries
			</span>
		</div>
		<select
			bind:value={filterIntent}
			class="px-3 py-1.5 rounded bg-bg-elevated border border-border text-sm text-text-primary focus:outline-none focus:border-accent"
		>
			<option value="">All intents</option>
			{#each ALL_INTENTS as intent}
				<option value={intent}>{intent}</option>
			{/each}
		</select>
	</div>

	{#if filtered.length === 0}
		<p class="text-text-secondary text-sm text-center py-8">Menunggu comment masuk...</p>
	{:else}
		<ul class="space-y-1.5 max-h-80 overflow-y-auto text-sm">
			{#each filtered as cc (cc.comment_id + cc.ts)}
				<li class="flex items-start gap-2 py-1 border-b border-border/50">
					<span class="text-xs text-text-secondary font-mono shrink-0 mt-0.5">
						{new Date(cc.ts).toLocaleTimeString('id-ID')}
					</span>
					<span class="font-semibold shrink-0 text-accent">{cc.user}:</span>
					<span class="text-text-primary flex-1 truncate"
						>{cc.text.slice(0, 60)}{cc.text.length > 60 ? '…' : ''}</span
					>
					<span class="shrink-0 flex items-center gap-1">
						<span class="text-xs px-1.5 py-0.5 rounded {intentColor(cc.intent)}">
							{cc.intent}
						</span>
						<span class="text-xs text-text-secondary">{Math.round(cc.confidence * 100)}%</span>
						<span class="text-xs text-text-secondary opacity-60">{cc.method}</span>
					</span>
				</li>
			{/each}
		</ul>
	{/if}
</div>
