<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import AudioLibraryGrid from '$lib/components/AudioLibraryGrid.svelte';

	const now = $derived(wsStore.nowPlaying);
	const recent = $derived(wsStore.events.filter(e => e.type === 'audio.now').slice(0, 10));
	const total = $derived(wsStore.audioClips.length);
</script>

<div class="p-6 space-y-4">
	<h1 class="text-2xl font-bold">🎵 Audio Library ({total} clips)</h1>

	{#if now}
		<div class="bg-green-500/20 border border-green-500 rounded-lg p-4 animate-pulse">
			<div class="flex items-center gap-3">
				<span class="text-3xl">🔊</span>
				<div class="flex-1">
					<div class="text-xs text-green-400 font-bold">NOW PLAYING</div>
					<div class="text-sm font-mono">{now.clip_id} · {now.category}</div>
					<div class="text-sm">{now.text}</div>
				</div>
			</div>
		</div>
	{:else}
		<div class="bg-bg-panel border border-border rounded-lg p-4 text-text-secondary text-sm">
			Tidak ada clip yang sedang play. Klik salah satu clip di grid bawah, atau jalankan <code>live.start</code>.
		</div>
	{/if}

	{#if recent.length > 0}
		<div class="bg-bg-panel border border-border rounded-lg p-4">
			<h3 class="text-sm font-semibold mb-2">🔁 Last {recent.length} Played</h3>
			<ul class="text-xs font-mono space-y-1 max-h-40 overflow-auto">
				{#each recent as e}
					<li>{new Date(e.ts).toLocaleTimeString('id-ID')} → <span class="text-accent">{e.data.clip_id}</span> <span class="text-text-secondary">({e.data.category})</span></li>
				{/each}
			</ul>
		</div>
	{/if}

	<AudioLibraryGrid />
</div>
