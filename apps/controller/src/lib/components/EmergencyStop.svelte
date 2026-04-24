<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	let confirming = $state(false);
	let tid: ReturnType<typeof setTimeout>;
	function click() {
		if (!confirming) {
			confirming = true;
			tid = setTimeout(() => (confirming = false), 3000);
			return;
		}
		clearTimeout(tid);
		wsStore.sendCommand('live.emergency_stop', {});
		confirming = false;
	}
</script>

<button
	onclick={click}
	class="w-full py-4 text-white font-bold rounded-lg text-lg transition {confirming ? 'bg-red-700 animate-pulse' : 'bg-red-500 hover:bg-red-600'}"
>
	{confirming ? '⚠️ KLIK LAGI (3 detik) UNTUK STOP' : '🛑 EMERGENCY STOP'}
</button>
