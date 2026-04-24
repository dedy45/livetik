<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	const decisions = $derived(wsStore.decisions);

	const colorByKind: Record<string, string> = {
		classify: 'text-blue-400',
		suggest: 'text-purple-400',
		'clip.play': 'text-green-400',
		phase: 'text-orange-400',
	};
</script>

<div class="bg-bg-panel border border-border rounded-lg p-6">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-lg font-semibold">🧠 Orchestrator Decision Stream</h3>
		<span class="text-xs text-text-secondary">{decisions.length} decision · live</span>
	</div>
	{#if decisions.length === 0}
		<p class="text-text-secondary text-sm">
			Belum ada keputusan. Trigger dengan <code>live.start</code> atau inject fake comment:<br />
			<code class="text-xs">python debug-dan-tes/02_inject_fake_comments.py</code>
		</p>
	{:else}
		<ul class="space-y-1 text-xs font-mono max-h-96 overflow-auto">
			{#each decisions as d (d.ts + d.kind + d.output)}
				<li class="grid grid-cols-[80px_80px_1fr_1fr_1fr] gap-2 py-1 border-b border-border/50">
					<span class="text-accent">{new Date(d.ts).toLocaleTimeString('id-ID')}</span>
					<span class={colorByKind[d.kind] ?? 'text-text-secondary'}>{d.kind}</span>
					<span class="text-text-secondary truncate" title={d.input}>{d.input}</span>
					<span class="text-text-primary truncate" title={d.output}>→ {d.output}</span>
					<span class="text-text-secondary italic truncate" title={d.reasoning}>{d.reasoning}</span>
				</li>
			{/each}
		</ul>
	{/if}
</div>
