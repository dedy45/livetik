<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import TestButton from '$lib/components/TestButton.svelte';

	let reloadReqId = $state<string | null>(null);
	const reloadResult = $derived(reloadReqId ? wsStore.testResults.get(reloadReqId) : undefined);
	const personaPreview = $derived(reloadResult?.ok ? (reloadResult.result?.preview ?? '') : '');
	const personaLen = $derived(reloadResult?.ok ? (reloadResult.result?.char_count ?? 0) : 0);

	let testUser = $state('Bang Rizky');
	let testText = $state('bang rangkanya kuat nggak?');
	let replyReqId = $state<string | null>(null);
	const replyResult = $derived(replyReqId ? wsStore.testResults.get(replyReqId) : undefined);

	function reload() {
		reloadReqId = wsStore.sendCommand('reload_persona');
	}
	function testReply() {
		replyReqId = wsStore.sendCommand('test_reply', { user: testUser, text: testText });
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Persona</h2>
		<button
			onclick={reload}
			disabled={!wsStore.connected}
			class="px-3 py-1.5 text-sm bg-accent text-bg-primary rounded hover:bg-accent/80 disabled:opacity-50"
		>
			Reload persona.md
		</button>
	</div>

	<!-- Preview -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold">Current persona.md</h3>
			<span class="text-xs text-text-secondary">{personaLen} chars</span>
		</div>
		{#if !personaPreview}
			<p class="text-text-secondary text-sm">Klik "Reload persona.md" untuk load content dari file.</p>
		{:else}
			<pre
				class="bg-bg-elevated border border-border rounded p-4 text-xs font-mono whitespace-pre-wrap overflow-auto max-h-64"
			>{personaPreview}</pre>
			<p class="text-xs text-text-secondary mt-2">
				Preview 200 char pertama. Edit file <code class="px-1 py-0.5 bg-bg-elevated rounded">apps/worker/config/persona.md</code> lalu klik Reload.
			</p>
		{/if}
	</section>

	<!-- Test reply -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">Test Reply (guardrail + LLM pipeline)</h3>
		<div class="space-y-3">
			<div class="flex gap-2">
				<input
					bind:value={testUser}
					class="w-40 px-3 py-2 bg-bg-elevated border border-border rounded text-sm"
					placeholder="user"
				/>
				<input
					bind:value={testText}
					class="flex-1 px-3 py-2 bg-bg-elevated border border-border rounded text-sm"
					placeholder="comment hipotetis"
				/>
				<button
					onclick={testReply}
					disabled={!wsStore.connected}
					class="px-4 py-2 bg-accent text-bg-primary rounded text-sm hover:bg-accent/80 disabled:opacity-50"
				>
					Test
				</button>
			</div>
			{#if replyResult}
				<div class="p-4 bg-bg-elevated rounded space-y-2 text-sm">
					{#if replyResult.ok && replyResult.result?.stage === 'ok'}
						<div class="flex gap-2 text-xs text-text-secondary">
							<span class="px-2 py-0.5 bg-bg-panel rounded">tier: {replyResult.result.tier}</span>
							<span class="px-2 py-0.5 bg-bg-panel rounded">{replyResult.result.latency_ms}ms</span>
							<span class="px-2 py-0.5 bg-bg-panel rounded">guardrail: ✓</span>
						</div>
						<div><span class="text-text-secondary">Q:</span> {testUser}: {testText}</div>
						<div class="text-accent"><span class="text-text-secondary">A:</span> {replyResult.result.reply}</div>
					{:else if replyResult.ok && replyResult.result?.stage === 'guardrail'}
						<div class="text-warn">🛡 Guardrail blocked: <b>{replyResult.result.reason}</b></div>
					{:else}
						<div class="text-error">Error: {replyResult.error || replyResult.result?.error}</div>
					{/if}
				</div>
			{/if}
			<p class="text-xs text-text-secondary">
				Pipeline: guardrail.check → llm.reply (tanpa TTS). Pakai untuk iterate persona.md tanpa spend TTS quota.
			</p>
		</div>
	</section>
</div>
