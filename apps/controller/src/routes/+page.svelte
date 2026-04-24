<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import DecisionStream from '$lib/components/DecisionStream.svelte';
	import ReplySuggestions from '$lib/components/ReplySuggestions.svelte';
	import TwoHourTimer from '$lib/components/TwoHourTimer.svelte';
	import EmergencyStop from '$lib/components/EmergencyStop.svelte';
	import AudioLibraryGrid from '$lib/components/AudioLibraryGrid.svelte';

	const m = $derived(wsStore.metrics);
</script>

<div class="p-6 space-y-4">
	<div class="flex items-center gap-4">
		<h1 class="text-2xl font-bold">🔴 livetik Dashboard</h1>
		<span class="text-sm {wsStore.connected ? 'text-green-400' : 'text-red-400'}">
			● {wsStore.connected ? 'connected' : 'disconnected'} · uptime {wsStore.uptime}
		</span>
	</div>

	<div class="grid grid-cols-3 gap-4">
		<div><TwoHourTimer /></div>
		<div class="bg-bg-panel border border-border rounded-lg p-4">
			<div class="text-xs uppercase text-text-secondary">Viewers / Comments</div>
			<div class="text-3xl font-mono">{m.viewers} / {m.comments}</div>
			<div class="text-xs text-text-secondary">Replies: {m.replies} · Queue: {m.queue_size}</div>
		</div>
		<div class="bg-bg-panel border border-border rounded-lg p-4">
			<div class="text-xs uppercase text-text-secondary">Budget hari ini</div>
			<div class="text-3xl font-mono {m.over_budget ? 'text-red-400' : ''}">Rp {m.cost_idr.toLocaleString('id-ID')}</div>
			<div class="h-2 bg-bg-dark rounded mt-1"><div class="h-full {m.over_budget ? 'bg-red-500' : 'bg-accent'}" style:width="{Math.min(100, m.budget_pct)}%"></div></div>
			<div class="text-xs text-text-secondary mt-1">Limit: Rp {m.budget_idr.toLocaleString('id-ID')}</div>
		</div>
	</div>

	<div class="grid grid-cols-2 gap-4">
		<ReplySuggestions />
		<DecisionStream />
	</div>

	<AudioLibraryGrid />

	<div class="grid grid-cols-4 gap-4">
		<EmergencyStop />
	</div>
</div>
