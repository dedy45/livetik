<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import TestButton from '$lib/components/TestButton.svelte';

	const m = $derived(wsStore.metrics);
	const byTier = $derived(m.by_tier ?? {});

	const entries = $derived(
		Object.entries(byTier)
			.map(([k, v]) => ({
				label: k,
				idr: v as number,
				pct: m.cost_idr > 0 ? ((v as number) / m.cost_idr) * 100 : 0
			}))
			.sort((a, b) => b.idr - a.idr)
	);
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Cost Tracker</h2>
		<TestButton command="reset_cost_today" params={{ confirm: true }} label="Reset today (DEV)" variant="danger" size="sm" />
	</div>

	<div class="grid grid-cols-3 gap-4">
		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<div class="text-sm text-text-secondary mb-1">Today</div>
			<div class="text-3xl font-bold {m.over_budget ? 'text-error' : 'text-accent'}">
				Rp {m.cost_idr.toLocaleString('id-ID')}
			</div>
			<div class="text-xs text-text-secondary mt-1">/ Rp {m.budget_idr.toLocaleString('id-ID')} budget</div>
		</div>
		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<div class="text-sm text-text-secondary mb-1">LLM calls</div>
			<div class="text-3xl font-bold">{m.llm_calls ?? 0}</div>
		</div>
		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<div class="text-sm text-text-secondary mb-1">TTS calls</div>
			<div class="text-3xl font-bold">{m.tts_calls ?? 0}</div>
		</div>
	</div>

	<!-- Progress -->
	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-3">
			<h3 class="text-lg font-semibold">Daily Budget</h3>
			<span class="text-sm font-mono {m.over_budget ? 'text-error' : 'text-text-secondary'}">
				{m.budget_pct.toFixed(1)}% used
			</span>
		</div>
		<div class="w-full h-4 bg-bg-elevated rounded-full overflow-hidden">
			<div
				class="h-full transition-all {m.over_budget
					? 'bg-error'
					: m.budget_pct > 75
						? 'bg-warn'
						: 'bg-ok'}"
				style="width: {Math.min(100, m.budget_pct)}%"
			></div>
		</div>
		{#if m.over_budget}
			<p class="mt-3 text-sm text-error">⚠ Budget harian tercapai. Reply di-skip sampai reset jam 00:00.</p>
		{/if}
	</div>

	<!-- Breakdown -->
	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">Breakdown per Tier</h3>
		{#if entries.length === 0}
			<p class="text-text-secondary text-sm">Belum ada biaya hari ini (cost_idr = 0).</p>
		{:else}
			<ul class="space-y-2">
				{#each entries as e}
					<li>
						<div class="flex justify-between text-sm mb-1">
							<span class="font-mono">{e.label}</span>
							<span>
								Rp {e.idr.toFixed(2)}
								<span class="text-text-secondary text-xs">({e.pct.toFixed(1)}%)</span>
							</span>
						</div>
						<div class="w-full h-2 bg-bg-elevated rounded overflow-hidden">
							<div class="h-full bg-accent" style="width: {e.pct}%"></div>
						</div>
					</li>
				{/each}
			</ul>
		{/if}
	</div>

	<!-- Estimasi tarif -->
	<div class="bg-bg-panel border border-border rounded-lg p-6 text-sm text-text-secondary">
		<h3 class="text-text-primary font-semibold mb-2">Estimasi tarif (Apr 2026)</h3>
		<ul class="list-disc list-inside space-y-1">
			<li><b>9router</b> (Claude via subscription): Rp 0 / reply</li>
			<li><b>DeepSeek</b>: ~Rp 1.5 / reply (80 token avg)</li>
			<li><b>Claude Haiku</b>: ~Rp 12 / reply</li>
			<li><b>Cartesia Sonic-3</b>: ~Rp 7 / reply (50 char avg)</li>
			<li><b>Edge-TTS</b>: Rp 0</li>
		</ul>
		<p class="mt-2 text-xs">Update tarif di <code class="px-1 py-0.5 bg-bg-elevated rounded">core/cost.py</code> kalau Cartesia/DeepSeek ubah harga.</p>
	</div>
</div>
