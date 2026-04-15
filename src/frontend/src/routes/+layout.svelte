<script lang="ts">
	import './layout.css';
	import 'katex/dist/katex.min.css';
	import { onMount, type Snippet } from 'svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { apiFetch } from '$lib/api';
	import Navbar from '$lib/components/Navbar.svelte';
	import { page } from '$app/state';

	const { children }: { children: Snippet } = $props();

	// Hide global navbar on the reader page as it has its own sidebar navigation
	const showNavbar = $derived(!page.url.pathname.includes('/step/'));

	onMount(async () => {
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

<div
	class="relative min-h-screen overflow-x-hidden text-foreground selection:bg-primary/20 selection:text-primary"
>
	<!-- Adaptive Background Atmosphere -->
	<div class="pointer-events-none fixed inset-0 -z-50 overflow-hidden bg-background">
		<!-- Starry Gradient Mesh -->
		<div
			class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--color-primary)_0%,_var(--color-background)_100%)] opacity-20"
		></div>
		<!-- Grain Texture Overlay -->
		<div
			class="absolute inset-0 opacity-[0.03] mix-blend-overlay"
			style="background-image: url('https://www.transparenttextures.com/patterns/p6.png')"
		></div>
		<!-- Animated Floating Glows -->
		<div
			class="nebula nebula-1 animate-pulse-slow pointer-events-none absolute top-[-20%] left-[-10%] h-[140%] w-[120%]"
		></div>
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
		background: radial-gradient(circle at center, var(--color-primary / 0.08) 0%, transparent 60%);
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
