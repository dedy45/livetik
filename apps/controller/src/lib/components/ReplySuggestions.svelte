<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import { onMount } from 'svelte';

	type Suggestion = {
		comment_id: string;
		comment_text: string;
		user: string;
		intent: string;
		replies: string[];
		source: string;
		cached: boolean;
	};

	let current = $state<Suggestion | null>(null);
	let loading = $state(false);
	let lastCommentId = $state('');

	const replyEnabled = $derived(wsStore.metrics.reply_enabled);
	const classified = $derived(wsStore.classifiedComments);

	// Watch for new classified comments and auto-request suggestions
	$effect(() => {
		const latest = classified[0];
		if (!latest) return;
		const cid = latest.comment_id;
		if (cid === lastCommentId) return;
		if (latest.intent === 'spam' || latest.intent.startsWith('forbidden')) return;
		lastCommentId = cid;
		loading = true;
		wsStore.sendCommand('reply.suggest', {
			comment_id: cid,
			text: latest.text,
			intent: latest.intent,
			user: latest.user,
		});
	});

	// Watch cmd_result for reply.suggest responses
	$effect(() => {
		const results = wsStore.testResults;
		for (const [, r] of results) {
			if (r.name === 'reply.suggest' && r.ok && r.result) {
				const res = r.result as {
					comment_id: string;
					replies: string[];
					source: string;
					cached: boolean;
				};
				const cc = classified.find((c) => c.comment_id === res.comment_id) ?? classified[0];
				if (cc) {
					current = {
						comment_id: res.comment_id,
						comment_text: cc.text,
						user: cc.user,
						intent: cc.intent,
						replies: res.replies ?? [],
						source: res.source ?? 'template',
						cached: res.cached ?? false,
					};
				}
				loading = false;
				wsStore.clearResult(r.req_id);
				break;
			}
		}
	});

	// Watch reply.suggestion WS push events
	$effect(() => {
		const latest = wsStore.replySuggestions[0];
		if (!latest) return;
		current = {
			comment_id: latest.comment_id,
			comment_text: latest.comment_text,
			user: latest.user,
			intent: latest.intent,
			replies: latest.replies,
			source: latest.source,
			cached: latest.cached,
		};
		loading = false;
	});

	function handleKey(e: KeyboardEvent) {
		if (!current || !replyEnabled) return;
		const idx = parseInt(e.key) - 1;
		if (idx >= 0 && idx <= 2 && current.replies[idx]) {
			approve(current.replies[idx]);
		}
	}

	onMount(() => {
		window.addEventListener('keydown', handleKey);
		return () => window.removeEventListener('keydown', handleKey);
	});

	function approve(reply: string) {
		wsStore.sendCommand('reply.approve', { reply });
	}

	function reject() {
		if (!current) return;
		wsStore.sendCommand('reply.reject', { comment_id: current.comment_id });
		current = null;
	}

	function regen() {
		if (!current) return;
		loading = true;
		wsStore.sendCommand('reply.regen', {
			text: current.comment_text,
			intent: current.intent,
			user: current.user,
		});
	}

	function sourceBadgeClass(source: string): string {
		if (source === 'llm') return 'bg-warn text-bg';
		if (source === 'cache') return 'bg-ok text-bg';
		return 'bg-bg-elevated text-text-secondary';
	}
</script>

<div class="bg-bg-panel border border-border rounded-lg p-6">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-lg font-semibold">Reply Suggestions</h3>
		<div class="flex items-center gap-2">
			{#if current}
				<span class="text-xs px-2 py-0.5 rounded {sourceBadgeClass(current.source)}">
					{current.source}{current.cached ? ' (cached)' : ''}
				</span>
			{/if}
			<span class="text-xs px-2 py-1 rounded {replyEnabled ? 'bg-ok text-bg' : 'bg-warn text-bg'}">
				{replyEnabled ? 'REPLY ON' : 'REPLY OFF'}
			</span>
		</div>
	</div>

	{#if !current && !loading}
		<p class="text-text-secondary text-sm">Menunggu komentar baru...</p>
	{:else if loading}
		<div class="flex items-center gap-2 text-text-secondary text-sm">
			<span class="animate-pulse">⏳</span>
			<span>Generating suggestions...</span>
		</div>
	{:else if current}
		<div class="mb-4 p-3 bg-bg-elevated rounded border-l-2 border-accent">
			<div class="flex items-baseline gap-2 text-sm">
				<span class="font-semibold text-accent shrink-0">{current.user}:</span>
				<span class="text-text-primary">{current.comment_text}</span>
			</div>
			<div class="mt-1">
				<span class="text-xs px-1.5 py-0.5 rounded bg-bg-panel text-text-secondary">
					{current.intent}
				</span>
			</div>
		</div>

		<div class="space-y-2 mb-4">
			{#each current.replies as reply, i (i)}
				<div
					class="flex items-start gap-3 p-3 bg-bg-elevated rounded border border-border hover:border-accent transition-colors"
				>
					<span
						class="shrink-0 w-6 h-6 flex items-center justify-center rounded bg-bg-panel text-xs font-bold text-accent border border-border"
					>
						{i + 1}
					</span>
					<p class="flex-1 text-sm text-text-primary leading-relaxed">{reply}</p>
					<button
						onclick={() => approve(reply)}
						disabled={!replyEnabled}
						class="shrink-0 px-3 py-1 text-xs rounded bg-ok text-bg font-semibold hover:opacity-80 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
					>
						Approve
					</button>
				</div>
			{/each}
		</div>

		<div class="flex items-center gap-2">
			<button
				onclick={regen}
				disabled={loading}
				class="px-3 py-1.5 text-xs rounded border border-border text-text-secondary hover:text-text-primary hover:border-accent transition-colors disabled:opacity-40"
			>
				↻ Regen
			</button>
			<button
				onclick={reject}
				class="px-3 py-1.5 text-xs rounded border border-border text-text-secondary hover:text-error hover:border-error transition-colors"
			>
				✕ Reject
			</button>
			{#if replyEnabled}
				<span class="ml-auto text-xs text-text-secondary">Press 1/2/3 to approve</span>
			{:else}
				<span class="ml-auto text-xs text-warn">Approve disabled — REPLY_ENABLED=false</span>
			{/if}
		</div>
	{/if}
</div>
