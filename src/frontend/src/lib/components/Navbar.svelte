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

<nav class="flex items-center justify-between py-4 border-b border-white/5 w-full bg-transparent/10 backdrop-blur-3xl sticky top-0 z-50 backdrop-saturate-150" in:fade>
	<div class="flex items-center gap-12">
		<a href="/" class="flex items-center gap-3 group px-2">
			<div class="rounded-xl bg-primary p-2 group-hover:scale-110 transition-transform shadow-lg shadow-primary/20">
				<BrainCircuit class="h-6 w-6 text-white" />
			</div>
			<div class="flex flex-col">
				<span class="font-display text-xl font-black tracking-tighter text-white uppercase">EXCELSIOR</span>
				<span class="text-[8px] font-display font-black tracking-[0.4em] text-primary -mt-1 uppercase">Academy</span>
			</div>
		</a>
		<div class="hidden items-center gap-8 text-xs font-black tracking-widest text-muted-foreground uppercase md:flex">
			<a href="/" class="transition-all hover:text-foreground relative pb-1 {isActive('/') ? 'text-foreground' : ''}">
				Dashboard
                {#if isActive('/')}
                    <div class="absolute -bottom-1 left-0 w-full h-0.5 bg-primary rounded-full shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
                {/if}
			</a>
			<a href="/providers" class="transition-all hover:text-foreground relative pb-1 {isActive('/providers') ? 'text-foreground' : ''}">
				AI Models
                {#if isActive('/providers')}
                    <div class="absolute -bottom-1 left-0 w-full h-0.5 bg-primary rounded-full shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
                {/if}
			</a>
			<a href="/decks" class="transition-all hover:text-foreground relative pb-1 {isActive('/decks') ? 'text-foreground' : ''}">
				NeuroDecks
                {#if isActive('/decks')}
                    <div class="absolute -bottom-1 left-0 w-full h-0.5 bg-primary rounded-full shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
                {/if}
			</a>
			<a href="/library" class="transition-all hover:text-foreground relative pb-1 {isActive('/library') ? 'text-foreground' : ''}">
				Library
                {#if isActive('/library')}
                    <div class="absolute -bottom-1 left-0 w-full h-0.5 bg-primary rounded-full shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
                {/if}
			</a>
		</div>
	</div>
	
	<div class="flex items-center gap-4 group cursor-pointer pr-2">
		<div class="flex flex-col items-end mr-1">
			<span class="text-xs font-black text-foreground group-hover:text-primary transition-colors">{auth.user?.username || 'Guest'}</span>
			<span class="text-[9px] text-muted-foreground/60 leading-none lowercase italic">Connected</span>
		</div>
		<div class="h-10 w-10 rounded-full bg-slate-900 border border-white/10 flex items-center justify-center group-hover:border-primary/40 group-hover:shadow-[0_0_15px_rgba(99,102,241,0.2)] transition-all">
			<span class="text-xs font-black text-primary uppercase">{auth.user?.username?.[0] || 'G'}</span>
		</div>
	</div>
</nav>

<style>
    .font-display { font-family: var(--font-display); }
</style>
