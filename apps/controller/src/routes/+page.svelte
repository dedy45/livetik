<script lang="ts">
	let status = $state('disconnected');
	let uptime = $state('00:00:00');
	let queueSize = $state(0);
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-2xl font-bold">Dashboard</h2>
		<div class="flex items-center gap-3">
			<span class="flex items-center gap-2">
				<span class="w-3 h-3 rounded-full bg-error"></span>
				<span class="text-sm text-text-secondary">{status}</span>
			</span>
			<span class="text-sm text-text-secondary">Uptime: {uptime}</span>
			<span class="px-3 py-1 bg-bg-elevated rounded-md text-sm">Queue: {queueSize}</span>
		</div>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Status</h3>
			<p class="text-3xl font-bold text-error">Disconnected</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Viewers</h3>
			<p class="text-3xl font-bold">0</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Comments</h3>
			<p class="text-3xl font-bold">0</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Replies</h3>
			<p class="text-3xl font-bold">0 / 0</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Latency (p95)</h3>
			<p class="text-3xl font-bold text-ok">0ms</p>
		</div>

		<div class="bg-bg-panel border border-border rounded-lg p-6">
			<h3 class="text-sm text-text-secondary mb-2">Cost Today</h3>
			<p class="text-3xl font-bold text-ok">Rp 0</p>
		</div>
	</div>

	<div class="bg-bg-panel border border-border rounded-lg p-6">
		<h3 class="text-lg font-semibold mb-4">Recent Events</h3>
		<div class="text-text-secondary text-sm">
			<p>No events yet. Start the worker to see activity.</p>
		</div>
	</div>
</div>
