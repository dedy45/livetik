<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import { wsStore } from '$lib/stores/ws.svelte';

	let { children } = $props();

	const nav = [
		{ href: '/', label: 'Dashboard', icon: '📊' },
		{ href: '/live', label: 'Live Monitor', icon: '🎙️' },
		{ href: '/errors', label: 'Errors', icon: '⚠️' },
		{ href: '/persona', label: 'Persona', icon: '🎭' },
		{ href: '/config', label: 'Config', icon: '⚙️' },
		{ href: '/cost', label: 'Cost', icon: '💰' }
	];
</script>

<div class="min-h-screen flex bg-bg-primary text-text-primary">
	<!-- Sidebar -->
	<aside class="w-56 bg-bg-panel border-r border-border flex flex-col">
		<!-- Header -->
		<div class="px-4 py-5 border-b border-border">
			<h1 class="text-lg font-bold text-accent">🎙️ Bang Hack</h1>
			<p class="text-xs text-text-secondary">v0.1.0-dev</p>
		</div>

		<!-- Navigation -->
		<nav class="flex-1 p-2 space-y-1">
			{#each nav as n}
				<a
					href={n.href}
					class="flex items-center gap-2 px-3 py-2 rounded-md text-sm hover:bg-bg-elevated transition-colors {$page.url.pathname === n.href ? 'bg-bg-elevated text-accent' : 'text-text-secondary'}"
				>
					<span>{n.icon}</span>
					<span>{n.label}</span>
				</a>
			{/each}
		</nav>

		<!-- Footer Status -->
		<div class="p-3 border-t border-border text-xs">
			<div class="flex items-center gap-2">
				<span
					class="w-2 h-2 rounded-full {wsStore.connected ? 'bg-ok' : 'bg-error'}"
					aria-label={wsStore.connected ? 'Worker online' : 'Worker offline'}
				></span>
				<span class="text-text-secondary">
					{wsStore.connected ? 'Worker online' : 'Worker offline'}
				</span>
			</div>
		</div>
	</aside>

	<!-- Main Content -->
	<main class="flex-1 overflow-auto p-8">
		{@render children()}
	</main>
</div>
