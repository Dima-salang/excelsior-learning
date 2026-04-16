<script lang="ts">
	import './layout.css';
	import 'katex/dist/katex.min.css';
	import { onMount, type Snippet } from 'svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { settings } from '$lib/stores/settings.svelte';
	import { apiFetch } from '$lib/api';
	import Navbar from '$lib/components/Navbar.svelte';
	import { page } from '$app/state';

	const { children }: { children: Snippet } = $props();

	const showNavbar = $derived(!page.url.pathname.includes('/step/'));

	onMount(async () => {
		settings.initTheme();

		const token = localStorage.getItem('access_token');
		if (token) {
			try {
				const user = await apiFetch('/auth/me');
				auth.login(token, user);
			} catch (err) {
				auth.logout();
			}
		}
	});
</script>

<div class="relative min-h-screen text-foreground">
	<div class="pointer-events-none fixed inset-0 -z-50 bg-background">
		<div class="nebula animate-pulse-slow absolute -top-20 -left-10 h-[140%] w-[120%]"></div>
	</div>

	<main class="relative z-10 flex min-h-screen w-full flex-col">
		{#if showNavbar}
			<Navbar />
		{/if}

		<div class="flex flex-grow flex-col">
			{@render children()}
		</div>
	</main>
</div>

<style>
	:global(body) {
		background-color: var(--background);
	}

	.nebula {
		filter: blur(100px);
		background: radial-gradient(circle at center, oklch(0.55 0.22 260 / 0.08) 0%, transparent 60%);
	}

	@media (prefers-color-scheme: light) {
		.nebula {
			display: none;
		}
	}

	:global(.light) .nebula {
		display: none;
	}

	@keyframes pulse-slow {
		0%,
		100% {
			transform: scale(1) translate(0, 0);
			opacity: 0.8;
		}
		50% {
			transform: scale(1.1) translate(2%, 1%);
			opacity: 1;
		}
	}
	.animate-pulse-slow {
		animation: pulse-slow 20s ease-in-out infinite;
	}
</style>
