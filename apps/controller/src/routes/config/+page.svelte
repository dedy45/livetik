<script lang="ts">
	import { wsStore } from '$lib/stores/ws.svelte';
	import TestButton from '$lib/components/TestButton.svelte';

	const m = $derived(wsStore.metrics);
	const pool = $derived(m.cartesia_pool ?? []);
	const models = $derived(m.llm_models ?? []);

	// LLM tier editable state — synced from metrics on first load
	type TierEdit = { model: string; api_base: string; api_key: string };
	let tierEdits = $state<Record<string, TierEdit>>({});

	// Populate edits when models arrive from worker
	$effect(() => {
		for (const model of models) {
			if (!tierEdits[model.id]) {
				tierEdits[model.id] = {
					model: model.model,
					api_base: model.api_base,
					api_key: ''
				};
			}
		}
	});

	// 9router model list (fetched on demand)
	let nineRouterModels = $state<Array<{ id: string; litellm_model: string }>>([]);
	let loadModelsReqId = $state<string | null>(null);
	const loadModelsResult = $derived(loadModelsReqId ? wsStore.testResults.get(loadModelsReqId) : undefined);

	$effect(() => {
		if (loadModelsResult?.ok && loadModelsResult.result?.models) {
			nineRouterModels = loadModelsResult.result.models;
		}
	});

	function loadNineRouterModels() {
		loadModelsReqId = wsStore.sendCommand('list_ninerouter_models');
	}

	// Ad-hoc test inputs
	let nineRouterTestModel = $state('KIRO');
	let nineRouterBase = $state('');
	let nineRouterKey = $state('');

	let ttsTestText = $state('Halo bos, Bang Hack di sini');
	let tiktokTestUsername = $state('');
	let guardrailTestText = $state('');
	let guardrailTestUser = $state('TestUser');

	function applyTierModel(tierId: string) {
		const edit = tierEdits[tierId];
		if (!edit) return;
		wsStore.sendCommand('update_llm_tier', { tier_id: tierId, model: edit.model });
	}

	function selectModel(model: string) {
		nineRouterTestModel = model;
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Config & Validation</h2>
		<TestButton command="reload_env" label="Reload .env" variant="secondary" size="sm" />
	</div>

	<!-- Runtime toggles -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">
			Runtime Toggles
			<span class="text-xs text-text-secondary font-normal">(tidak persist, hilang kalau worker restart)</span>
		</h3>
		<div class="grid grid-cols-2 gap-4">
			<div class="flex items-center justify-between p-3 bg-bg-elevated rounded">
				<div>
					<div class="font-medium">REPLY_ENABLED</div>
					<div class="text-xs text-text-secondary">Current: {m.reply_enabled ? 'ON' : 'OFF'}</div>
				</div>
				<div class="flex gap-1">
					<TestButton command="set_reply_enabled" params={{ value: true }} label="ON" size="sm" variant={m.reply_enabled ? 'primary' : 'secondary'} />
					<TestButton command="set_reply_enabled" params={{ value: false }} label="OFF" size="sm" variant={!m.reply_enabled ? 'primary' : 'secondary'} />
				</div>
			</div>
			<div class="flex items-center justify-between p-3 bg-bg-elevated rounded">
				<div>
					<div class="font-medium">DRY_RUN</div>
					<div class="text-xs text-text-secondary">Current: {m.dry_run ? 'ON' : 'OFF'}</div>
				</div>
				<div class="flex gap-1">
					<TestButton command="set_dry_run" params={{ value: true }} label="ON" size="sm" variant={m.dry_run ? 'primary' : 'secondary'} />
					<TestButton command="set_dry_run" params={{ value: false }} label="OFF" size="sm" variant={!m.dry_run ? 'primary' : 'secondary'} />
				</div>
			</div>
		</div>
	</section>

	<!-- System -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">System</h3>
		<div class="flex items-center justify-between p-3 bg-bg-elevated rounded">
			<div>
				<div class="font-medium">ffplay (ffmpeg)</div>
				<div class="text-xs text-text-secondary">Required untuk TTS audio playback</div>
			</div>
			<TestButton command="test_ffplay" label="Probe" />
		</div>
	</section>

	<!-- 9router -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">9router (LLM gateway)</h3>
		<div class="space-y-3">
			<!-- Connection test -->
			<div class="flex items-center justify-between p-3 bg-bg-elevated rounded">
				<div>
					<div class="font-medium">Connection</div>
					<div class="font-mono text-xs text-text-secondary">
						{models.find(m => m.id === 'ninerouter')?.api_base || 'localhost:20128/v1'}
					</div>
				</div>
				<div class="flex gap-2">
					<TestButton command="test_ninerouter" label="Ping /models" />
					<button
						onclick={loadNineRouterModels}
						disabled={!wsStore.connected}
						class="px-3 py-1.5 text-sm bg-bg-elevated border border-border rounded hover:bg-bg-primary disabled:opacity-40"
					>
						Load Models
					</button>
				</div>
			</div>

			<!-- Available models list -->
			{#if nineRouterModels.length > 0}
				<div class="p-3 bg-bg-elevated rounded">
					<div class="text-xs text-text-secondary mb-2">
						{nineRouterModels.length} model tersedia — klik untuk pilih:
					</div>
					<div class="flex flex-wrap gap-1 max-h-32 overflow-auto">
						{#each nineRouterModels as nm}
							<button
								onclick={() => selectModel(nm.id)}
								class="px-2 py-0.5 text-xs font-mono rounded border border-border hover:bg-accent hover:text-bg-primary transition
									{nineRouterTestModel === nm.id ? 'bg-accent text-bg-primary' : 'bg-bg-primary text-text-secondary'}"
							>
								{nm.id}
							</button>
						{/each}
					</div>
					<p class="text-xs text-text-secondary mt-2">
						💡 LiteLLM format: <code class="px-1 bg-bg-primary rounded">openai/&lt;model_id&gt;</code>
						— auto-applied saat test. Cukup ketik model ID saja.
					</p>
				</div>
			{/if}

			<!-- Ad-hoc model test -->
			<div class="p-3 bg-bg-elevated rounded space-y-2">
				<div class="font-medium text-sm">Test model (tanpa ubah config aktif)</div>
				<div class="space-y-2">
					<div class="flex gap-2">
						<input
							bind:value={nineRouterTestModel}
							class="flex-1 px-3 py-1.5 bg-bg-primary border border-border rounded text-sm font-mono"
							placeholder="Model ID, e.g. KIRO atau openai/KIRO"
						/>
						<TestButton
							command="test_llm_custom"
							params={{ model: nineRouterTestModel, api_base: nineRouterBase, api_key: nineRouterKey }}
							label="Test"
						/>
					</div>
					<div class="flex gap-2">
						<input
							bind:value={nineRouterBase}
							class="flex-1 px-3 py-1.5 bg-bg-primary border border-border rounded text-sm font-mono"
							placeholder="API Base (kosong = pakai NINEROUTER_BASE_URL dari .env)"
						/>
						<input
							bind:value={nineRouterKey}
							class="w-48 px-3 py-1.5 bg-bg-primary border border-border rounded text-sm font-mono"
							placeholder="API Key (kosong = dari .env)"
						/>
					</div>
				</div>
				<p class="text-xs text-text-secondary">
					Model ID tanpa prefix akan otomatis jadi <code class="px-1 bg-bg-primary rounded">openai/&lt;id&gt;</code>.
					Tidak mengubah router aktif.
				</p>
			</div>
		</div>
	</section>

	<!-- LLM models -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold">LLM Tiers ({models.length} tier)</h3>
			<TestButton command="test_llm" label="Test active router" />
		</div>
		<p class="text-xs text-text-secondary mb-3">
			Edit model string lalu klik <b>Apply</b> untuk update router runtime (tidak persist — edit .env untuk permanen).
		</p>
		{#if models.length === 0}
			<p class="text-text-secondary text-sm">No models configured. Set NINEROUTER/DEEPSEEK/ANTHROPIC keys di .env.</p>
		{:else}
			<div class="space-y-3">
				{#each models as model, i}
					{@const edit = tierEdits[model.id]}
					<div class="border border-border rounded p-4 space-y-3">
						<!-- Header -->
						<div class="flex items-center justify-between">
							<div class="font-semibold">
								Tier {i + 1}: <span class="text-accent">{model.id}</span>
							</div>
							<span class="text-xs text-text-secondary">{model.timeout}s timeout</span>
						</div>
						{#if edit}
							<!-- Model string -->
							<div class="space-y-1">
								<label class="text-xs text-text-secondary">Model (LiteLLM format)</label>
								<div class="flex gap-2">
									<input
										bind:value={edit.model}
										class="flex-1 px-3 py-1.5 bg-bg-elevated border border-border rounded text-sm font-mono"
										placeholder="e.g. openai/KIRO atau openai/kc/openai/gpt-4.1"
									/>
								</div>
								{#if nineRouterModels.length > 0 && model.id === 'ninerouter'}
									<div class="flex flex-wrap gap-1 mt-1">
										{#each nineRouterModels.slice(0, 8) as nm}
											<button
												onclick={() => { edit.model = `openai/${nm.id}`; }}
												class="px-1.5 py-0.5 text-xs font-mono rounded border border-border hover:bg-accent hover:text-bg-primary transition
													{edit.model === `openai/${nm.id}` ? 'bg-accent text-bg-primary' : 'bg-bg-primary text-text-secondary'}"
											>
												{nm.id}
											</button>
										{/each}
									</div>
								{/if}
							</div>
							<!-- api_base (only for ninerouter) -->
							{#if model.api_base}
								<div class="space-y-1">
									<label class="text-xs text-text-secondary">API Base</label>
									<input
										bind:value={edit.api_base}
										class="w-full px-3 py-1.5 bg-bg-elevated border border-border rounded text-sm font-mono"
										placeholder="http://localhost:20128/v1"
									/>
								</div>
							{/if}
							<!-- Actions -->
							<div class="flex items-center gap-2 pt-1">
								<button
									onclick={() => applyTierModel(model.id)}
									disabled={!wsStore.connected}
									class="px-3 py-1.5 text-sm bg-accent text-bg-primary rounded hover:bg-accent/80 disabled:opacity-40"
								>
									Apply
								</button>
								<TestButton
									command="test_llm_custom"
									params={{
										model: edit.model,
										api_base: edit.api_base,
										api_key: edit.api_key
									}}
									label="Test"
									variant="secondary"
								/>
								<span class="text-xs text-text-secondary">
									Apply → update router aktif. Test → coba model tanpa ubah router.
								</span>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</section>

	<!-- Cartesia pool -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold">Cartesia TTS Pool ({pool.length} key)</h3>
			<TestButton command="test_cartesia_all" label="Test semua key" />
		</div>
		{#if pool.length === 0}
			<p class="text-text-secondary text-sm">No keys configured. Set CARTESIA_API_KEYS=key1,key2,... di .env.</p>
		{:else}
			<div class="space-y-2">
				{#each pool as slot, i}
					<div class="flex items-center justify-between p-3 bg-bg-elevated rounded">
						<div>
							<div class="font-mono text-sm">{slot.key}</div>
							<div class="text-xs text-text-secondary">
								{slot.calls} calls · {slot.total_errors} errors
								{#if slot.exhausted} · <span class="text-error">⏳ {Math.floor(slot.cooldown_s / 3600)}h cooldown</span>{/if}
							</div>
						</div>
						<TestButton command="test_cartesia_key" params={{ key_index: i }} label="Test" size="sm" />
					</div>
				{/each}
			</div>
		{/if}
	</section>

	<!-- Edge-TTS + Voice out -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">TTS Output</h3>
		<div class="space-y-3">
			<div class="flex items-center justify-between p-3 bg-bg-elevated rounded">
				<div>
					<div class="font-medium">Edge-TTS fallback (id-ID-ArdiNeural)</div>
					<div class="text-xs text-text-secondary">Synth tanpa play — validasi Azure reachability</div>
				</div>
				<TestButton command="test_edge_tts" label="Test synth" />
			</div>
			<div class="p-3 bg-bg-elevated rounded">
				<div class="font-medium mb-2">Voice Output (end-to-end, keluar suara)</div>
				<div class="flex gap-2">
					<input
						bind:value={ttsTestText}
						class="flex-1 px-3 py-1.5 bg-bg-primary border border-border rounded text-sm"
						placeholder="Text untuk disintesis & diputar"
					/>
					<TestButton command="test_tts_voice_out" params={{ text: ttsTestText }} label="Speak" />
				</div>
				<div class="text-xs text-text-secondary mt-1">Suara keluar di default audio device (atau VB-CABLE kalau sudah di-route)</div>
			</div>
		</div>
	</section>

	<!-- TikTok -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">TikTok Connection</h3>
		<div class="p-3 bg-bg-elevated rounded">
			<div class="flex gap-2">
				<input
					bind:value={tiktokTestUsername}
					class="flex-1 px-3 py-1.5 bg-bg-primary border border-border rounded text-sm font-mono"
					placeholder="username (tanpa @) — kosong = pakai TIKTOK_USERNAME dari .env"
				/>
				<TestButton command="test_tiktok_conn" params={{ username: tiktokTestUsername }} label="Check live" />
			</div>
			<div class="text-xs text-text-secondary mt-1">Verify akun live atau offline (read-only, no ban risk)</div>
		</div>
	</section>

	<!-- Guardrail -->
	<section class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">Guardrail Test</h3>
		<div class="p-3 bg-bg-elevated rounded space-y-2">
			<div class="flex gap-2">
				<input
					bind:value={guardrailTestUser}
					class="w-32 px-3 py-1.5 bg-bg-primary border border-border rounded text-sm"
					placeholder="user"
				/>
				<input
					bind:value={guardrailTestText}
					class="flex-1 px-3 py-1.5 bg-bg-primary border border-border rounded text-sm"
					placeholder="Coba: 'halo bang', 'cek wa 081234', 'http://spam.com'"
				/>
				<TestButton command="test_guardrail" params={{ user: guardrailTestUser, text: guardrailTestText }} label="Check" />
			</div>
			<div class="text-xs text-text-secondary">Verify filter regex + rate limit + dedup sebelum go-live</div>
		</div>
	</section>
</div>
