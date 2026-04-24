<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import type { ClipMeta } from '$lib/stores/audio_library.svelte';

	let clips = $state<ClipMeta[]>([]);
	let loading = $state(true);
	let filterCategory = $state('');
	let filterProduct = $state('');
	let searchTag = $state('');
	let notPlayedRecently = $state(false);

	// Load clips from audio.list command
	$effect(() => {
		if (wsStore.connected) {
			const reqId = wsStore.sendCommand('audio.list', {});
			// Wait for result
			setTimeout(() => {
				const result = wsStore.getResult(reqId);
				if (result?.ok && result.result?.clips) {
					clips = result.result.clips;
					loading = false;
					wsStore.clearResult(reqId);
				}
			}, 500);
		}
	});

	const categories = $derived([...new Set(clips.map((c) => c.category))].sort());
	const products = $derived([...new Set(clips.map((c) => c.tags[0] || ''))].filter(Boolean).sort());

	const filtered = $derived(
		clips.filter((c) => {
			if (filterCategory && c.category !== filterCategory) return false;
			if (filterProduct && !c.tags.includes(filterProduct)) return false;
			if (searchTag && !c.tags.some((t) => t.toLowerCase().includes(searchTag.toLowerCase())))
				return false;
			return true;
		})
	);

	function playClip(clipId: string) {
		wsStore.sendCommand('audio.play', { clip_id: clipId });
	}

	function refreshList() {
		loading = true;
		const reqId = wsStore.sendCommand('audio.list', {});
		setTimeout(() => {
			const result = wsStore.getResult(reqId);
			if (result?.ok && result.result?.clips) {
				clips = result.result.clips;
				loading = false;
				wsStore.clearResult(reqId);
			}
		}, 500);
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Audio Library</h2>
		<button
			onclick={refreshList}
			class="px-4 py-2 bg-accent text-bg rounded hover:opacity-80 transition-opacity"
		>
			↻ Refresh
		</button>
	</div>

	<!-- Stats Panel -->
	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">Library Stats</h3>
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
			<div>
				<p class="text-sm text-text-secondary">Total Clips</p>
				<p class="text-2xl font-bold">{clips.length}</p>
			</div>
			<div>
				<p class="text-sm text-text-secondary">Categories</p>
				<p class="text-2xl font-bold">{categories.length}</p>
			</div>
			<div>
				<p class="text-sm text-text-secondary">Filtered</p>
				<p class="text-2xl font-bold">{filtered.length}</p>
			</div>
			<div>
				<p class="text-sm text-text-secondary">Avg Duration</p>
				<p class="text-2xl font-bold">
					{clips.length > 0 ? Math.round(clips.reduce((sum, c) => sum + c.duration_ms, 0) / clips.length / 1000) : 0}s
				</p>
			</div>
		</div>
	</div>

	<!-- Filter Bar -->
	<div class="bg-bg-panel border border-border rounded-lg p-4">
		<div class="grid grid-cols-1 md:grid-cols-4 gap-3">
			<div>
				<label class="block text-sm text-text-secondary mb-1">Category</label>
				<select
					bind:value={filterCategory}
					class="w-full px-3 py-2 rounded bg-bg-elevated border border-border text-text-primary focus:outline-none focus:border-accent"
				>
					<option value="">All categories</option>
					{#each categories as cat}
						<option value={cat}>{cat}</option>
					{/each}
				</select>
			</div>
			<div>
				<label class="block text-sm text-text-secondary mb-1">Product</label>
				<select
					bind:value={filterProduct}
					class="w-full px-3 py-2 rounded bg-bg-elevated border border-border text-text-primary focus:outline-none focus:border-accent"
				>
					<option value="">All products</option>
					{#each products as prod}
						<option value={prod}>{prod}</option>
					{/each}
				</select>
			</div>
			<div>
				<label class="block text-sm text-text-secondary mb-1">Search Tags</label>
				<input
					type="text"
					bind:value={searchTag}
					placeholder="Type to search..."
					class="w-full px-3 py-2 rounded bg-bg-elevated border border-border text-text-primary focus:outline-none focus:border-accent"
				/>
			</div>
			<div class="flex items-end">
				<button
					onclick={() => {
						filterCategory = '';
						filterProduct = '';
						searchTag = '';
						notPlayedRecently = false;
					}}
					class="px-4 py-2 rounded border border-border text-text-secondary hover:text-text-primary hover:border-accent transition-colors"
				>
					Clear Filters
				</button>
			</div>
		</div>
	</div>

	<!-- Clips Grid -->
	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">Clips ({filtered.length})</h3>
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<span class="text-text-secondary">Loading clips...</span>
			</div>
		{:else if filtered.length === 0}
			<div class="flex items-center justify-center py-12">
				<span class="text-text-secondary">No clips found</span>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[600px] overflow-y-auto">
				{#each filtered as clip (clip.id)}
					<button
						onclick={() => playClip(clip.id)}
						class="border border-border rounded p-3 text-left hover:bg-bg-elevated hover:border-accent transition-colors"
					>
						<div class="flex items-start justify-between mb-2">
							<span class="text-xs font-mono text-accent">{clip.id}</span>
							<span class="text-xs text-text-secondary">{Math.round(clip.duration_ms / 1000)}s</span>
						</div>
						<div class="text-xs px-2 py-0.5 rounded bg-bg-elevated text-text-secondary inline-block mb-2">
							{clip.category}
						</div>
						<p class="text-sm text-text-primary line-clamp-2 mb-2">{clip.script}</p>
						{#if clip.tags.length > 0}
							<div class="flex flex-wrap gap-1">
								{#each clip.tags.slice(0, 3) as tag}
									<span class="text-xs px-1.5 py-0.5 rounded bg-bg-primary text-text-secondary">
										{tag}
									</span>
								{/each}
							</div>
						{/if}
						{#if clip.scene_hint}
							<div class="mt-2 text-xs text-text-secondary italic">
								Scene: {clip.scene_hint}
							</div>
						{/if}
					</button>
				{/each}
			</div>
		{/if}
	</div>
</div>
