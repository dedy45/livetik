<script lang="ts">
	import '../app.css';
</script>

<div class="min-h-screen bg-bg-primary text-text-primary">
	<nav class="bg-bg-panel border-b border-border px-6 py-4">
		<div class="flex items-center justify-between">
			<h1 class="text-xl font-bold text-accent">🎙️ Bang Hack Controller</h1>
			<div class="flex items-center gap-4">
				<span class="text-sm text-text-secondary">v0.1.0-dev</span>
			</div>
		</div>
	</nav>
	
	<main class="container mx-auto px-6 py-8">
		<slot />
	</main>
</div>
