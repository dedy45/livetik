<script lang="ts">
	import { onMount } from 'svelte';
	import { wsStore } from '$lib/stores/ws.svelte';
	import type { ClipMeta } from '$lib/stores/audio_library.svelte';

	// Local self-contained state
	let clips = $state<ClipMeta[]>([]);
	let currentClipId = $state<string | null>(null);
	let searchQuery = $state('');
	let filterCategory = $state('');
	let searchTimer: ReturnType<typeof setTimeout> | null = null;

	const categories = $derived([...new Set(clips.map((c) => c.category))].sort());

	const filteredClips = $derived(
		clips.filter((c) => {
			const matchCat = !filterCategory || c.category === filterCategory;
			return matchCat;
		})
	);

	function formatDuration(ms: number): string {
		const totalSec = Math.floor(ms / 1000);
		const m = Math.floor(totalSec / 60).toString().padStart(2, '0');
		const s = (totalSec % 60).toString().padStart(2, '0');
		return `${m}:${s}`;
	}

	function onSearchInput(e: Event) {
		const val = (e.target as HTMLInputElement).value;
		searchQuery = val;
		if (searchTimer) clearTimeout(searchTimer);
		searchTimer = setTimeout(() => {
			wsStore.sendCommand('audio.list', val.trim() ? { tag: val.trim() } : {});
		}, 300);
	}

	function playClip(clipId: string) {
		wsStore.sendCommand('audio.play', { clip_id: clipId });
	}

	function stopAudio() {
		wsStore.sendCommand('audio.stop', {});
	}

	// Watch cmd_result for audio.list to populate clips
	$effect(() => {
		for (const [, result] of wsStore.testResults) {
			if (result.name === 'audio.list' && result.ok && result.result?.clips) {
				clips = result.result.clips as ClipMeta[];
				wsStore.clearResult(result.req_id);
				break;
			}
		}
	});

	// Track currently playing clip from ws audioNow
	$effect(() => {
		currentClipId = wsStore.audioNow;
	});

	onMount(() => {
		wsStore.sendCommand('audio.list', {});
	});
</script>

<div class="bg-bg-panel border border-border rounded-lg p-6">
	<div class="flex items-center justify-between mb-4">
		<div class="flex items-center gap-3">
			<h3 class="text-lg font-semibold">Audio Library</h3>
			<span class="text-xs px-2 py-0.5 rounded bg-bg-elevated text-text-secondary">
				{filteredClips.length} / {clips.length} clips
			</span>
		</div>
		<button
			onclick={stopAudio}
			class="px-3 py-1.5 rounded bg-error text-bg text-sm font-semibold hover:opacity-80 transition-opacity"
		>
			⏹ Stop
		</button>
	</div>

	<div class="flex gap-3 mb-4">
		<input
			type="text"
			placeholder="Search by tag, script, category…"
			value={searchQuery}
			oninput={onSearchInput}
			class="flex-1 px-3 py-2 rounded bg-bg-elevated border border-border text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:border-accent"
		/>
		<select
			bind:value={filterCategory}
			class="px-3 py-2 rounded bg-bg-elevated border border-border text-sm text-text-primary focus:outline-none focus:border-accent"
		>
			<option value="">All categories</option>
			{#each categories as cat}
				<option value={cat}>{cat}</option>
			{/each}
		</select>
	</div>

	{#if filteredClips.length === 0}
		<p class="text-text-secondary text-sm text-center py-8">
			{clips.length === 0 ? 'Loading clips…' : 'No clips match the current filter.'}
		</p>
	{:else}
		<div class="grid grid-cols-2 md:grid-cols-4 gap-3 max-h-[480px] overflow-y-auto pr-1">
			{#each filteredClips as clip (clip.id)}
				<button
					onclick={() => playClip(clip.id)}
					class="text-left p-3 rounded border transition-all hover:border-accent focus:outline-none focus:border-accent
						{currentClipId === clip.id
							? 'border-ok bg-ok/10'
							: 'border-border bg-bg-elevated hover:bg-bg-panel'}"
				>
					<div class="flex items-start justify-between gap-1 mb-1">
						<span class="text-xs font-mono text-text-secondary truncate flex-1">{clip.id}</span>
						{#if currentClipId === clip.id}
							<span class="text-ok text-xs shrink-0">▶</span>
						{/if}
					</div>
					<span class="inline-block text-xs px-1.5 py-0.5 rounded bg-accent/20 text-accent mb-1.5">
						{clip.category}
					</span>
					<p class="text-xs text-text-primary leading-snug mb-1.5 line-clamp-2">
						{clip.script.slice(0, 60)}{clip.script.length > 60 ? '…' : ''}
					</p>
					<div class="flex flex-wrap gap-1 mb-1.5">
						{#each clip.tags.slice(0, 3) as tag}
							<span class="text-xs px-1 py-0.5 rounded bg-bg-panel text-text-secondary border border-border">
								{tag}
							</span>
						{/each}
					</div>
					<span class="text-xs text-text-secondary font-mono">{formatDuration(clip.duration_ms)}</span>
				</button>
			{/each}
		</div>
	{/if}
</div>
