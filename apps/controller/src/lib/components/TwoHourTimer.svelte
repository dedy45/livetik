<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	const s = $derived(wsStore.liveState);
	const remaining = $derived(Math.max(0, s.max_s - s.elapsed_s));
	const pct = $derived(Math.min(100, (s.elapsed_s / s.max_s) * 100));
	const warn = $derived(remaining < 600);
	function fmt(sec: number) {
		const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), ss = sec % 60;
		return `${h}:${String(m).padStart(2, '0')}:${String(ss).padStart(2, '0')}`;
	}
</script>

<div class="p-4 rounded-lg border-2 {warn ? 'border-red-500 bg-red-500/10' : 'border-green-500 bg-green-500/10'}">
	<div class="flex justify-between items-baseline">
		<span class="text-xs uppercase text-text-secondary">Sisa waktu</span>
		<span class="text-xs">{s.phase ?? '—'} ({s.phase_idx + 1}/{s.phase_total})</span>
	</div>
	<div class="text-4xl font-mono font-bold">{fmt(remaining)}</div>
	<div class="h-2 bg-bg-dark rounded mt-2 overflow-hidden">
		<div class="h-full bg-accent" style:width="{pct}%"></div>
	</div>
	<div class="text-xs mt-1 text-text-secondary">Mode: <b>{s.mode}</b> · Produk: <b>{s.product ?? '—'}</b></div>
</div>
