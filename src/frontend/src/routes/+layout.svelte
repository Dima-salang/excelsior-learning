<script lang="ts">
	import './layout.css';
    import { onMount } from 'svelte';
    import { auth } from '$lib/stores/auth';
	import { apiFetch } from '$lib/api';

	const { children } = $props();

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

<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="relative min-h-screen overflow-x-hidden text-slate-100">
	<!-- Starry Layer -->
	<div class="fixed inset-0 -z-50 bg-[#020617]">
		<!-- Gradient Mesh -->
		<div
			class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_#0f172a_0%,_#020617_100%)]"
		></div>
		<!-- Grain Texture -->
		<div
			class="absolute inset-0 opacity-[0.03]"
			style="background-image: url('https://www.transparenttextures.com/patterns/p6.png')"
		></div>
		<!-- Animated Nebula -->
		<div
			class="nebula nebula-1 animate-pulse-slow absolute top-[-20%] left-[-10%] h-[140%] w-[120%]"
		></div>
	</div>

	<main class="relative z-10 w-full">
		{@render children()}
	</main>
</div>

<style>
	:global(body) {
		font-family: 'Outfit', sans-serif;
		background-color: #020617;
	}
	:global(h1, h2, h3, h4, h5, h6) {
		font-family: 'Outfit', sans-serif;
		letter-spacing: -0.02em;
	}
	:global(.font-serif) {
		font-family: 'IBM Plex Serif', serif;
	}

	.nebula {
		filter: blur(100px);
		background: radial-gradient(circle at center, rgba(34, 211, 238, 0.08) 0%, transparent 60%);
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
