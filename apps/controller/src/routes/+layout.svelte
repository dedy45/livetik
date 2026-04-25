<script lang="ts">
	import '../app.css';
	import { wsStore } from '$lib/stores/ws.svelte';

	let { children } = $props();
	const status = $derived(wsStore.status);
	const err = $derived(wsStore.lastConnectError);
	const toasts = $derived(wsStore.toasts);

	const statusColor = $derived({
		connecting: 'bg-yellow-500',
		connected: 'bg-green-500',
		disconnected: 'bg-red-600',
		reconnecting: 'bg-orange-500',
	}[status]);

	const statusLabel = $derived({
		connecting: '⏳ Connecting to worker ws://127.0.0.1:8765...',
		connected: '✅ Worker connected',
		disconnected: '❌ Worker DISCONNECTED — jalankan: cd apps/worker && uv run python -m banghack.main',
		reconnecting: `🔄 Reconnecting (attempt ${wsStore.reconnectAttempts})...`,
	}[status]);

	const menus = [
		{ href: '/', label: '📊 Dashboard' },
		{ href: '/live', label: '🎙 Live Cockpit' },
		{ href: '/library', label: '🎵 Audio Library' },
		{ href: '/errors', label: '⚠️ Errors' },
		{ href: '/persona', label: '🎭 Persona' },
		{ href: '/config', label: '⚙️ Config' },
		{ href: '/cost', label: '💰 Cost' },
	];
</script>

<!-- Status banner (always visible at top) -->
<div class="{statusColor} text-white text-sm px-4 py-2 flex items-center justify-between sticky top-0 z-50">
	<div class="flex items-center gap-2">
		<span class="w-2 h-2 rounded-full bg-white/80 {status === 'connected' ? '' : 'animate-pulse'}"></span>
		<span class="font-mono">{statusLabel}</span>
		{#if err}<span class="opacity-75">· {err}</span>{/if}
	</div>
	{#if status === 'connected'}
		<span class="text-xs opacity-75">uptime {wsStore.uptime}</span>
	{/if}
</div>

<!-- Nav -->
<nav class="bg-bg-panel border-b border-border px-4 py-2 flex gap-2 flex-wrap sticky top-10 z-40">
	{#each menus as m}
		<a href={m.href} class="px-3 py-1 rounded hover:bg-accent/20 text-sm">{m.label}</a>
	{/each}
</nav>

<!-- Page content -->
<main class="min-h-screen">
	{@render children()}
</main>

<!-- Toast container (top-right) -->
<div class="fixed top-20 right-4 z-50 flex flex-col gap-2 w-80 pointer-events-none">
	{#each toasts as t (t.id)}
		<div class="pointer-events-auto border rounded-lg p-3 shadow-lg animate-slide-in
			{t.kind === 'success' ? 'bg-green-900/80 border-green-500' : ''}
			{t.kind === 'error' ? 'bg-red-900/80 border-red-500' : ''}
			{t.kind === 'info' ? 'bg-blue-900/80 border-blue-500' : ''}
			{t.kind === 'warning' ? 'bg-yellow-900/80 border-yellow-500' : ''}">
			<div class="flex items-start justify-between gap-2">
				<div class="flex-1">
					<div class="font-semibold text-sm text-white">{t.title}</div>
					{#if t.detail}<div class="text-xs text-white/80 mt-1 font-mono break-all">{t.detail}</div>{/if}
				</div>
				<button onclick={() => wsStore.dismissToast(t.id)} class="text-white/60 hover:text-white text-xs">✕</button>
			</div>
		</div>
	{/each}
</div>

<style>
	:global(.animate-slide-in) {
		animation: slide-in 0.2s ease-out;
	}
	@keyframes slide-in {
		from { transform: translateX(100%); opacity: 0; }
		to { transform: translateX(0); opacity: 1; }
	}
</style>
