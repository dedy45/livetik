<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import TestButton from '$lib/components/TestButton.svelte';

	// ── Load current persona ──────────────────────────────────────────────
	let loadReqId = $state<string | null>(null);
	const loadResult = $derived(loadReqId ? wsStore.testResults.get(loadReqId) : undefined);

	// Editor state — populated when load result arrives
	let editorContent = $state('');
	let isDirty = $state(false);
	let lastSavedLen = $state(0);

	$effect(() => {
		if (loadResult?.ok && loadResult.result?.content !== undefined) {
			// Use full content instead of preview
			editorContent = loadResult.result.content ?? '';
			lastSavedLen = loadResult.result.char_count ?? 0;
			isDirty = false; // Mark as clean after loading
		}
	});

	// Auto-load persona on connect
	$effect(() => {
		if (wsStore.connected && !editorContent && !loadReqId) {
			loadPersona();
		}
	});

	// ── Save persona ──────────────────────────────────────────────────────
	let saveReqId = $state<string | null>(null);
	const saveResult = $derived(saveReqId ? wsStore.testResults.get(saveReqId) : undefined);

	$effect(() => {
		if (saveResult?.ok) {
			isDirty = false;
			lastSavedLen = saveResult.result?.char_count ?? editorContent.length;
			// Update editor with saved content to ensure sync
			if (saveResult.result?.content) {
				editorContent = saveResult.result.content;
			}
		}
	});

	function loadPersona() {
		loadReqId = wsStore.sendCommand('reload_persona');
	}

	function savePersona() {
		if (!editorContent.trim()) return;
		saveReqId = wsStore.sendCommand('save_persona', { content: editorContent });
	}

	function onEditorInput(e: Event) {
		editorContent = (e.target as HTMLTextAreaElement).value;
		isDirty = true;
	}

	// ── Test reply ────────────────────────────────────────────────────────
	let testUser = $state('Bang Rizky');
	let testText = $state('bang rangkanya kuat nggak?');
	let replyReqId = $state<string | null>(null);
	const replyResult = $derived(replyReqId ? wsStore.testResults.get(replyReqId) : undefined);

	function testReply() {
		replyReqId = wsStore.sendCommand('test_reply', { user: testUser, text: testText });
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Persona</h2>
		<div class="flex gap-2">
			<button
				onclick={loadPersona}
				disabled={!wsStore.connected}
				class="px-3 py-1.5 text-sm border border-border rounded hover:bg-bg-elevated disabled:opacity-50"
			>
				Load dari file
			</button>
			<button
				onclick={savePersona}
				disabled={!wsStore.connected || !editorContent.trim()}
				class="px-3 py-1.5 text-sm rounded disabled:opacity-50
					{isDirty ? 'bg-accent text-bg-primary hover:bg-accent/80' : 'bg-bg-elevated border border-border'}"
			>
				{isDirty ? '💾 Save & Apply' : '✓ Saved'}
			</button>
		</div>
	</div>

	<!-- Editor -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-3">
			<h3 class="text-lg font-semibold">Editor persona.md</h3>
			<div class="flex items-center gap-3 text-xs text-text-secondary">
				{#if lastSavedLen > 0}
					<span>file: {lastSavedLen} chars</span>
				{/if}
				<span class={isDirty ? 'text-warn' : 'text-text-secondary'}>
					{isDirty ? '● unsaved' : '● synced'}
				</span>
				<span>{editorContent.length} chars</span>
			</div>
		</div>

		<textarea
			value={editorContent}
			oninput={onEditorInput}
			rows={12}
			spellcheck={false}
			class="w-full px-4 py-3 bg-bg-elevated border border-border rounded text-sm font-mono
				resize-y focus:outline-none focus:border-accent transition-colors"
			placeholder="Klik 'Load dari file' untuk load persona aktif, atau ketik langsung di sini.&#10;&#10;Contoh:&#10;Kamu adalah Bang Hack, asisten virtual TikTok Live @interiorhack.id.&#10;Jawab dalam bahasa Indonesia santai maksimal 2 kalimat pendek.&#10;Fokus interior, furniture, rangka baja. Jangan sebut harga pasti atau kontak."
		></textarea>

		<div class="flex items-center justify-between mt-2">
			<p class="text-xs text-text-secondary">
				Edit langsung → klik <b>Save & Apply</b> → persona aktif berubah real-time tanpa restart.
				File <code class="px-1 py-0.5 bg-bg-elevated rounded">config/persona.md</code> ikut tersimpan.
			</p>
			{#if saveResult}
				{#if saveResult.ok}
					<span class="text-xs text-success">✓ Saved {saveResult.result?.char_count} chars</span>
				{:else}
					<span class="text-xs text-error">✗ {saveResult.error}</span>
				{/if}
			{/if}
		</div>
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
				Pipeline: guardrail.check → llm.reply (tanpa TTS). Pakai untuk iterate persona tanpa spend TTS quota.
			</p>
		</div>
	</section>
</div>
