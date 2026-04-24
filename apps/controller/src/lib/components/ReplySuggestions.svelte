<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	const suggestions = $derived(wsStore.suggestions);

	function approve(id: string, variant: number) {
		wsStore.sendCommand('reply.approve', { suggestion_id: id, variant });
	}
	function reject(id: string) {
		wsStore.sendCommand('reply.reject', { suggestion_id: id });
	}
	function regen(id: string, hint: string) {
		wsStore.sendCommand('reply.regen', { suggestion_id: id, hint });
	}
</script>

<div class="bg-bg-panel border border-border rounded-lg p-6">
	<div class="flex items-center justify-between mb-3">
		<h3 class="text-lg font-semibold">💬 Reply Suggestions</h3>
		<span class="text-xs text-text-secondary">{suggestions.length} pending</span>
	</div>
	{#if suggestions.length === 0}
		<p class="text-sm text-text-secondary">Belum ada saran. LLM akan generate saat ada comment "bernilai" (buying_intent, compatibility, product_question).</p>
	{:else}
		<div class="space-y-3 max-h-[500px] overflow-auto">
			{#each suggestions as s (s.suggestion_id)}
				<div class="border border-border rounded p-3 bg-yellow-500/5">
					<div class="text-xs text-text-secondary mb-1">
						@{s.user} · <span class="text-accent">{s.intent}</span> · via <b>{s.source}</b>
					</div>
					<div class="text-sm font-medium mb-2">"{s.comment_text}"</div>
					<ul class="space-y-1">
						{#each s.replies as r, i}
							<li class="flex gap-2">
								<button
									onclick={() => approve(s.suggestion_id, i)}
									class="bg-green-600 hover:bg-green-500 text-white px-2 py-0.5 rounded text-xs font-bold"
								>✓ {i + 1}</button>
								<span class="text-sm flex-1">{r}</span>
							</li>
						{/each}
					</ul>
					<div class="flex gap-1 mt-2">
						<button onclick={() => regen(s.suggestion_id, 'lebih pendek')} class="text-xs bg-blue-500/20 hover:bg-blue-500/30 px-2 py-0.5 rounded">↻ pendek</button>
						<button onclick={() => regen(s.suggestion_id, 'lebih hangat')} class="text-xs bg-blue-500/20 hover:bg-blue-500/30 px-2 py-0.5 rounded">↻ hangat</button>
						<button onclick={() => reject(s.suggestion_id)} class="text-xs bg-red-500/20 hover:bg-red-500/30 px-2 py-0.5 rounded ml-auto">✕ skip</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
