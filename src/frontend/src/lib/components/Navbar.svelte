<script lang="ts">
	import { BrainCircuit } from '@lucide/svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { page } from '$app/state';
	import { fade } from 'svelte/transition';

	const isActive = (path: string) => {
		if (path === '/') return page.url.pathname === '/';
		return page.url.pathname.startsWith(path);
	};
</script>

<nav
	class="sticky top-0 z-50 flex w-full items-center justify-between border-b border-white/5 bg-background/80 px-6 py-4 backdrop-blur-3xl backdrop-saturate-150 md:px-12"
	in:fade={{ duration: 300 }}
>
	<div class="flex items-center gap-12">
		<a href="/" class="group flex items-center gap-3 px-2">
			<div
				class="rounded-xl bg-primary p-2 shadow-lg shadow-primary/20 transition-transform group-hover:scale-110"
			>
				<BrainCircuit class="h-6 w-6 text-white" />
			</div>
			<div class="flex flex-col">
				<span class="font-display text-xl font-black tracking-tighter text-white uppercase"
					>EXCELSIOR</span
				>
				<span
					class="-mt-1 font-display text-[8px] font-black tracking-[0.4em] text-primary uppercase"
					>Academy</span
				>
			</div>
		</a>
		<div
			class="hidden items-center gap-8 text-xs font-black tracking-widest text-muted-foreground uppercase md:flex"
		>
			<a
				href="/"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/')
					? 'text-foreground'
					: ''}"
			>
				Dashboard
				{#if isActive('/')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/providers"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/providers')
					? 'text-foreground'
					: ''}"
			>
				AI Models
				{#if isActive('/providers')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/generate"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/generate')
					? 'text-foreground'
					: ''}"
			>
				Generate
				{#if isActive('/generate')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/chat"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/chat')
					? 'text-foreground'
					: ''}"
			>
				Chat
				{#if isActive('/chat')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/decks"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/decks')
					? 'text-foreground'
					: ''}"
			>
				Decks
				{#if isActive('/decks')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/library"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/library')
					? 'text-foreground'
					: ''}"
			>
				Library
				{#if isActive('/library')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
		</div>
	</div>

	<div class="group flex cursor-pointer items-center gap-4 pr-2">
		<div class="mr-1 flex flex-col items-end">
			<span class="text-xs font-black text-foreground transition-colors group-hover:text-primary"
				>{auth.user?.username || 'Guest'}</span
			>
			<span class="text-[9px] leading-none text-muted-foreground/60 lowercase italic"
				>Connected</span
			>
		</div>
		<div
			class="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-secondary transition-all group-hover:border-primary/40 group-hover:shadow-[0_0_15px_rgba(99,102,241,0.2)]"
		>
			<span class="text-xs font-black text-primary uppercase"
				>{auth.user?.username?.[0] || 'G'}</span
			>
		</div>
	</div>
</nav>

<style>
	.font-display {
		font-family: var(--font-display);
	}
</style>
