<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import { 
		Layers, 
		Plus, 
		BrainCircuit, 
		Calendar, 
		ChevronRight, 
		Loader2,
		Sparkles
	} from '@lucide/svelte';
	import { goto } from '$app/navigation';

	interface Deck {
		id: number;
		title: string;
		description: string | null;
		created_at: string;
	}

	let decks = $state<Deck[]>([]);
	let isLoading = $state(true);
	let error = $state('');

	async function fetchDecks() {
		if (!auth.user) return;
		try {
			decks = await apiFetch(`/decks?user_id=${auth.user.id}`);
		} catch (err: any) {
			error = err.message || 'Identity failure while retrieving neural nodes.';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		fetchDecks();
	});

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>Neural Decks — Excelsior</title>
</svelte:head>

<div class="min-h-screen bg-transparent pt-32 pb-20 px-6">
	<div class="max-w-7xl mx-auto space-y-16">
		<header class="flex flex-col md:flex-row md:items-end justify-between gap-8" in:fade>
			<div class="space-y-4">
				<div class="flex items-center gap-3 text-[10px] font-black tracking-[0.4em] text-indigo-400 uppercase">
					<Layers class="w-4 h-4" />
					<span>Knowledge Architecture</span>
				</div>
				<h1 class="text-5xl md:text-7xl font-unbounded font-black tracking-tighter text-white uppercase leading-none">
					Neuro<span class="text-indigo-500">Decks</span>
				</h1>
				<p class="text-slate-500 font-serif italic text-lg max-w-xl">
					Manage your collection of AI-synthesized knowledge modules and flashcard networks.
				</p>
			</div>
			
			<Button 
				onclick={() => goto('/dashboard')}
				class="h-14 px-8 rounded-2xl bg-indigo-600 font-black tracking-widest uppercase shadow-[0_0_30px_rgba(79,70,229,0.4)] transition-all hover:-translate-y-1"
			>
				<Plus class="mr-2 w-5 h-5" />
				Generate New Lecture
			</Button>
		</header>

		{#if isLoading}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				{#each Array(6) as _}
					<div class="h-64 rounded-3xl bg-white/5 animate-pulse border border-white/5"></div>
				{/each}
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center py-20 text-center space-y-6">
				<div class="p-6 rounded-full bg-red-500/10 border border-red-500/20">
					<BrainCircuit class="w-12 h-12 text-red-500" />
				</div>
				<h2 class="text-2xl font-unbounded font-black text-white uppercase italic">{error}</h2>
				<Button onclick={fetchDecks} variant="outline" class="rounded-xl border-white/10">Retry Connection</Button>
			</div>
		{:else if decks.length === 0}
			<div class="flex flex-col items-center justify-center py-32 text-center space-y-10 rounded-[4rem] border border-dashed border-white/5 bg-white/2" in:scale>
				<div class="relative">
					<div class="absolute inset-0 animate-ping rounded-full bg-indigo-500/20"></div>
					<div class="relative p-8 rounded-full bg-indigo-500/10 border border-indigo-500/20">
						<Layers class="w-16 h-16 text-indigo-400" />
					</div>
				</div>
				<div class="space-y-4">
					<h2 class="text-3xl font-unbounded font-black text-white uppercase tracking-tighter">No Neural Decks Found</h2>
					<p class="text-slate-500 font-serif italic text-xl max-w-md mx-auto">
						Start by generating a lecture to synthesize your first knowledge deck.
					</p>
				</div>
				<Button 
					onclick={() => goto('/dashboard')}
					class="h-16 px-10 rounded-2xl bg-indigo-600 font-black tracking-widest uppercase shadow-2xl"
				>
					Initialize Synthesis
				</Button>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				{#each decks as deck, i}
					<div 
						in:fly={{ y: 20, delay: i * 50 }}
						class="group relative h-full flex flex-col p-8 rounded-[2.5rem] bg-slate-900/40 border border-white/5 backdrop-blur-xl transition-all duration-500 hover:bg-slate-900/60 hover:border-indigo-500/30 hover:shadow-[0_20px_50px_rgba(0,0,0,0.5)] cursor-pointer overflow-hidden"
						onclick={() => goto(`/decks/${deck.id}`)}
					>
						<!-- Decorative Glow -->
						<div class="absolute -top-10 -right-10 w-40 h-40 bg-indigo-500/10 blur-[80px] rounded-full transition-opacity duration-700 opacity-0 group-hover:opacity-100"></div>
						
						<div class="relative z-10 flex flex-col h-full space-y-6">
							<div class="flex items-center justify-between">
								<div class="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
									<Layers class="w-6 h-6 text-indigo-400" />
								</div>
								<div class="flex items-center gap-2 text-[10px] font-black tracking-widest text-slate-500 uppercase">
									<Calendar class="w-3 h-3" />
									{formatDate(deck.created_at)}
								</div>
							</div>

							<div class="space-y-2 flex-grow">
								<h3 class="text-2xl font-unbounded font-black text-white uppercase tracking-tighter group-hover:text-indigo-400 transition-colors">
									{deck.title}
								</h3>
								<p class="text-slate-400 font-serif italic line-clamp-3 leading-relaxed">
									{deck.description || 'No neural context provided.'}
								</p>
							</div>

							<div class="pt-6 border-t border-white/5 flex items-center justify-between">
								<div class="flex items-center gap-2">
									<Sparkles class="w-4 h-4 text-indigo-400" />
									<span class="text-[10px] font-black tracking-widest text-slate-500 uppercase">Interactive Deck</span>
								</div>
								<div class="flex items-center gap-1 text-indigo-400 font-black tracking-widest text-[10px] uppercase group-hover:translate-x-1 transition-transform">
									Link
									<ChevronRight class="w-4 h-4" />
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.font-unbounded { font-family: var(--font-display); }
	.font-serif { font-family: var(--font-serif); }
</style>
