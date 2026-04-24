<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import DecisionStream from '$lib/components/DecisionStream.svelte';
	import TwoHourTimer from '$lib/components/TwoHourTimer.svelte';
	import EmergencyStop from '$lib/components/EmergencyStop.svelte';

	const s = $derived(wsStore.liveState);
	function startLive() { wsStore.sendCommand('live.start', {}); }
	function pause() { wsStore.sendCommand('live.pause', {}); }
	function resume() { wsStore.sendCommand('live.resume', {}); }
</script>

<div class="p-6 space-y-4">
	<h1 class="text-2xl font-bold">🔴 Live Control</h1>

	<TwoHourTimer />

	<div class="flex gap-2">
		{#if s.mode === 'idle' || s.mode === 'stopped'}
			<button onclick={startLive} class="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded font-bold">▶️ START LIVE</button>
		{:else if s.mode === 'running'}
			<button onclick={pause} class="bg-yellow-600 hover:bg-yellow-500 text-white px-4 py-2 rounded font-bold">⏸ PAUSE</button>
		{:else if s.mode === 'paused'}
			<button onclick={resume} class="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded font-bold">▶️ RESUME</button>
		{/if}
		<div class="flex-1"></div>
		<div class="w-64"><EmergencyStop /></div>
	</div>

	<DecisionStream />
</div>
