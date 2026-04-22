<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import TestButton from '$lib/components/TestButton.svelte';

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

	<!-- System Health card (P2-C) -->
	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold">System Health</h3>
			<a href="/config" class="text-sm text-accent hover:underline">Full validation →</a>
		</div>
		<div class="grid grid-cols-2 md:grid-cols-5 gap-3">
			{#each [
				{ label: 'ffplay', cmd: 'test_ffplay' },
				{ label: '9router', cmd: 'test_ninerouter' },
				{ label: 'LLM', cmd: 'test_llm' },
				{ label: 'Cartesia', cmd: 'test_cartesia_all' },
				{ label: 'Edge-TTS', cmd: 'test_edge_tts' }
			] as probe}
				<div class="flex flex-col items-center gap-1 p-3 bg-bg-elevated rounded">
					<span class="text-xs text-text-secondary">{probe.label}</span>
					<TestButton command={probe.cmd} label="Probe" size="sm" variant="secondary" />
				</div>
			{/each}
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

	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold">Reply Feed</h3>
			<span class="text-xs px-2 py-1 rounded {m.reply_enabled ? 'bg-ok text-bg' : 'bg-warn text-bg'}">
				{m.reply_enabled ? (m.dry_run ? 'DRY RUN' : 'LIVE') : 'DISABLED'}
			</span>
		</div>
		{#if wsStore.replies.length === 0}
			<p class="text-text-secondary text-sm">
				{m.reply_enabled ? 'Menunggu reply…' : 'REPLY_ENABLED=false di .env'}
			</p>
		{:else}
			<ul class="space-y-3 text-sm max-h-64 overflow-auto">
				{#each wsStore.replies.slice(0, 10) as r (r.ts + r.user)}
					<li class="border-l-2 border-accent pl-3">
						<div class="flex items-baseline gap-2 mb-1">
							<span class="text-accent font-mono text-xs shrink-0">
								{new Date(r.ts).toLocaleTimeString('id-ID')}
							</span>
							<span class="font-semibold shrink-0">{r.user}:</span>
							<span class="text-text-secondary text-xs">{r.comment}</span>
						</div>
						<div class="flex items-baseline gap-2">
							<span class="text-ok">→</span>
							<span class="text-text-primary">{r.reply}</span>
						</div>
						<div class="flex gap-2 mt-1 text-xs text-text-secondary">
							<span>tier={r.tier}</span>
							<span>tts={r.tts}</span>
							<span>{r.latency_ms}ms</span>
						</div>
					</li>
				{/each}
			</ul>
		{/if}
	</div>

	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold">Cost & Budget</h3>
			<span class="text-xs px-2 py-1 rounded {m.over_budget ? 'bg-error text-bg' : 'bg-ok text-bg'}">
				{m.over_budget ? 'OVER BUDGET' : 'OK'}
			</span>
		</div>
		<div class="space-y-2">
			<div class="flex justify-between items-baseline">
				<span class="text-sm text-text-secondary">Cost Today</span>
				<span class="text-2xl font-bold">Rp {m.cost_idr.toLocaleString('id-ID')}</span>
			</div>
			<div class="flex justify-between items-baseline">
				<span class="text-sm text-text-secondary">Budget</span>
				<span class="text-lg">Rp {m.budget_idr.toLocaleString('id-ID')}</span>
			</div>
			<div class="w-full bg-bg-elevated rounded-full h-2 overflow-hidden">
				<div
					class="h-full transition-all {m.over_budget ? 'bg-error' : 'bg-ok'}"
					style="width: {Math.min(m.budget_pct, 100)}%"
				></div>
			</div>
			<p class="text-xs text-text-secondary text-right">{m.budget_pct.toFixed(1)}% used</p>
			
			{#if m.cartesia_pool && m.cartesia_pool.length > 0}
				<div class="mt-3 text-xs text-text-secondary border-t border-border pt-3">
					<div class="mb-1">Cartesia pool ({m.cartesia_pool.length} key):</div>
					{#each m.cartesia_pool as slot}
						<div class="flex justify-between font-mono">
							<span>{slot.key}</span>
							<span class={slot.exhausted ? 'text-error' : 'text-ok'}>
								{slot.exhausted ? `⏳ ${Math.floor(slot.cooldown_s/3600)}h` : `✓ ${slot.calls} calls`}
							</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>

	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold">LLM Models</h3>
			<span class="text-xs px-2 py-1 rounded bg-bg-elevated">
				{m.llm_models.length} tier{m.llm_models.length !== 1 ? 's' : ''}
			</span>
		</div>
		{#if m.llm_models.length === 0}
			<p class="text-text-secondary text-sm">No models configured</p>
		{:else}
			<div class="space-y-2 text-sm">
				{#each m.llm_models as model, i}
					<div class="border border-border rounded p-3">
						<div class="flex items-center justify-between mb-1">
							<span class="font-semibold text-accent">Tier {i + 1}: {model.id}</span>
							<span class="text-xs px-2 py-0.5 rounded bg-bg-elevated font-mono">
								{model.timeout}s
							</span>
						</div>
						<div class="text-xs text-text-secondary font-mono">
							{model.model}
						</div>
						{#if model.api_base}
							<div class="text-xs text-text-secondary mt-1">
								{model.api_base}
							</div>
						{/if}
					</div>
				{/each}
			</div>
			<div class="mt-3 text-xs text-text-secondary">
				<p>💡 Edit &amp; apply di <a href="/config" class="text-accent underline">Config page</a> — perubahan real-time tanpa restart</p>
			</div>
		{/if}
	</div>

	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold">Live Comments</h3>
			<a href="/live" class="text-sm text-accent hover:underline">Full monitor →</a>
		</div>
		{#if wsStore.comments.length === 0}
			<p class="text-text-secondary text-sm">
				{m.status === 'live' ? 'Menunggu comment masuk…' : `Status: ${m.status} — set TIKTOK_USERNAME di .env lalu restart worker.`}
			</p>
		{:else}
			<ul class="space-y-2 text-sm max-h-64 overflow-auto">
				{#each wsStore.comments.slice(0, 15) as c (c.ts + c.user)}
					<li class="flex items-baseline gap-2">
						<span class="text-accent font-mono text-xs shrink-0">
							{new Date(c.ts).toLocaleTimeString('id-ID')}
						</span>
						<span class="font-semibold shrink-0">{c.user}:</span>
						<span class="text-text-primary">{c.text}</span>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</div>
