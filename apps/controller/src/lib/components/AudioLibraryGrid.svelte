<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import { CATEGORIES } from '$lib/stores/audio_library.svelte';

	let search = $state('');
	let cat = $state<string>('ALL');

	const clips = $derived(wsStore.audioClips);
	const nowId = $derived(wsStore.nowPlaying?.clip_id);
	const visible = $derived(
		clips
			.filter((c: any) => cat === 'ALL' || c.category === cat)
			.filter((c: any) => !search || (c.text || '').toLowerCase().includes(search.toLowerCase()) || c.id.toLowerCase().includes(search.toLowerCase()))
	);

	function play(id: string) { wsStore.sendCommand('audio.play', { clip_id: id }); }
	function stop() { wsStore.sendCommand('audio.stop', {}); }
</script>

<div class="bg-bg-panel border border-border rounded-lg p-4">
	<div class="flex gap-2 mb-3 items-center">
		<input bind:value={search} placeholder="cari clip..." class="bg-bg-dark border border-border rounded px-2 py-1 text-sm flex-1" />
		<select bind:value={cat} class="bg-bg-dark border border-border rounded px-2 py-1 text-sm">
			{#each CATEGORIES as c}<option value={c}>{c}</option>{/each}
		</select>
		<button onclick={stop} class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm">⏹ Stop</button>
		<span class="text-xs text-text-secondary">{visible.length}/{clips.length}</span>
	</div>
	<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-[500px] overflow-auto">
		{#each visible as c (c.id)}
			<button
				onclick={() => play(c.id)}
				class="text-left border border-border rounded p-2 hover:bg-accent/10 text-xs {nowId === c.id ? 'ring-2 ring-accent bg-accent/20' : ''}"
			>
				<div class="font-mono text-[10px] text-text-secondary">{c.id}</div>
				<div class="line-clamp-3">{c.text}</div>
				{#if c.product}<div class="text-accent mt-1">🏷 {c.product}</div>{/if}
			</button>
		{/each}
	</div>
</div>
