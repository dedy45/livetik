<script lang="ts">
	import { liveStateStore } from '$lib/stores/live_state.svelte';

	let showModal = $state(false);

	function handleEmergencyStop() {
		liveStateStore.emergencyStop();
		showModal = false;
	}
</script>

<!-- Emergency Stop button -->
<div class="bg-bg-panel border border-error/50 rounded-lg p-6 flex flex-col items-center justify-center gap-4">
	<h3 class="text-lg font-semibold text-text-primary">Emergency Control</h3>
	<button
		onclick={() => (showModal = true)}
		class="w-full px-6 py-4 rounded-lg bg-error text-bg font-bold text-lg hover:opacity-90 active:scale-95 transition-all shadow-lg"
	>
		🚨 EMERGENCY STOP
	</button>
	<p class="text-xs text-text-secondary text-center">
		Hentikan semua proses live, audio, dan otomasi seketika
	</p>
</div>

<!-- Confirmation modal -->
{#if showModal}
	<div class="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
		<div class="bg-bg-panel border border-error rounded-xl p-8 max-w-sm w-full mx-4 shadow-2xl">
			<h2 class="text-xl font-bold text-error mb-2">Emergency Stop</h2>
			<p class="text-text-secondary mb-6">
				Yakin stop semua? Ini akan menghentikan live session, audio, dan semua proses otomatis.
			</p>
			<div class="flex gap-3">
				<button
					onclick={handleEmergencyStop}
					class="flex-1 px-4 py-3 rounded bg-error text-bg font-bold hover:opacity-90 transition-opacity"
				>
					Ya, Stop Sekarang
				</button>
				<button
					onclick={() => (showModal = false)}
					class="flex-1 px-4 py-3 rounded border border-border text-text-secondary hover:text-text-primary transition-colors"
				>
					Batal
				</button>
			</div>
		</div>
	</div>
{/if}
