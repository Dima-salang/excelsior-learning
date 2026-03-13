<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { apiFetch } from '$lib/api';
	import { fade, fly, slide } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import { 
		ArrowLeft, 
		BrainCircuit, 
		Layers,
		CheckCircle2,
		RotateCcw,
		Sparkles,
		Clock,
		Loader2
	} from '@lucide/svelte';
	import { goto } from '$app/navigation';
	import Flashcard from '$lib/components/Flashcard.svelte';

	interface Card {
		id: number;
		type: string;
		front: string;
		options?: string[];
		options_ans?: number;
		explanation?: string;
		is_correct?: boolean;
		user_selected_ans?: number;
	}

	interface Deck {
		id: number;
		title: string;
		description: string | null;
		created_at: string;
		cards: Card[];
	}

	let id = $derived(page.params.id);
	let deck = $state<Deck | null>(null);
	let isLoading = $state(true);
	let error = $state('');

	async function fetchDeck() {
		try {
			isLoading = true;
			deck = await apiFetch(`/decks/${id}`);
		} catch (err: any) {
			error = err.message || 'Quantum interface failed to retrieve deck architecture.';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		fetchDeck();
	});

	async function updateCardMastery(cardId: number, isCorrect: boolean, selectedAns: number) {
		try {
			// Update backend via the existing lectures/cards endpoint (which handles general card updates)
			await apiFetch(`/lectures/cards/${cardId}`, {
				method: 'PATCH',
				body: JSON.stringify({
					user_selected_ans: selectedAns,
					is_correct: isCorrect
				})
			});
		} catch (err) {
			console.error('Mastery update failed:', err);
		}
	}

	let masteredCount = $derived(deck?.cards.filter(c => c.is_correct).length || 0);
	let totalCount = $derived(deck?.cards.length || 0);
	let progress = $derived(totalCount > 0 ? (masteredCount / totalCount) * 100 : 0);
</script>

<svelte:head>
	<title>{deck?.title || 'Neural Deck'} — Excelsior</title>
</svelte:head>

<div class="min-h-screen bg-transparent pt-32 pb-32 px-6">
	<div class="max-w-6xl mx-auto space-y-12">
		<!-- Navigation and Progress -->
		<div class="flex flex-col md:flex-row md:items-center justify-between gap-6" in:fade>
			<Button 
				variant="ghost" 
				onclick={() => goto('/decks')}
				class="w-fit flex items-center gap-2 text-slate-500 hover:text-white group px-0"
			>
				<ArrowLeft class="w-4 h-4 transition-transform group-hover:-translate-x-1" />
				<span class="text-[10px] font-black tracking-widest uppercase">Back to Decks</span>
			</Button>

			{#if deck}
				<div class="flex items-center gap-6">
					<div class="flex items-center gap-2">
						<CheckCircle2 class="w-4 h-4 text-emerald-400" />
						<span class="text-[10px] font-black tracking-widest text-emerald-400 uppercase">
							{masteredCount} / {totalCount} Mastered
						</span>
					</div>
					<div class="w-32 h-1.5 rounded-full bg-white/5 overflow-hidden">
						<div 
							class="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 transition-all duration-1000"
							style="width: {progress}%"
						></div>
					</div>
				</div>
			{/if}
		</div>

		{#if isLoading}
			<div class="flex flex-col items-center justify-center py-32 space-y-6">
				<Loader2 class="w-12 h-12 text-indigo-500 animate-spin" />
				<p class="font-serif italic text-slate-500">Accessing neural storage units...</p>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center py-20 text-center space-y-6">
				<div class="p-6 rounded-full bg-red-500/10 border border-red-500/20">
					<BrainCircuit class="w-12 h-12 text-red-500" />
				</div>
				<h2 class="text-2xl font-unbounded font-black text-white uppercase italic">{error}</h2>
				<Button onclick={fetchDeck} variant="outline" class="rounded-xl border-white/10">Retry Sync</Button>
			</div>
		{:else if deck}
			<header class="flex flex-col md:flex-row md:items-end justify-between gap-8" in:fade>
				<div class="space-y-6">
					<div class="flex items-center gap-4 text-[10px] font-black tracking-[0.4em] text-indigo-400 uppercase">
						<Sparkles class="w-4 h-4" />
						<span>Deck Interface v1.0</span>
					</div>
					<h1 class="text-4xl md:text-6xl font-unbounded font-black tracking-tighter text-white uppercase leading-tight">
						{deck.title}
					</h1>
					<p class="text-xl text-slate-400 font-serif italic leading-relaxed max-w-2xl">
						{deck.description || 'Synergizing multiple concepts into unified neural mapping.'}
					</p>
				</div>
				<Button 
					size="lg"
					class="h-16 px-12 rounded-2xl bg-indigo-600 font-black tracking-widest uppercase shadow-[0_0_30_rgba(79,70,229,0.3)] hover:-translate-y-1 transition-all"
				>
					Start Quiz
				</Button>
			</header>

			<!-- Flashcards Grid -->
			<div class="space-y-12">
				<div class="flex items-center gap-4">
					<div class="h-px flex-grow bg-white/5"></div>
					<span class="text-[10px] font-black tracking-[0.4em] text-slate-500 uppercase">Interactive Nodes</span>
					<div class="h-px flex-grow bg-white/5"></div>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					{#each deck.cards as card, i}
						<div in:fly={{ y: 20, delay: i * 100 }}>
							<Flashcard 
								{...card} 
								compact={true}
								onAnswered={(isCorrect, selectedIdx) => updateCardMastery(card.id, isCorrect, selectedIdx)}
							/>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.font-unbounded { font-family: var(--font-display); }
	.font-serif { font-family: var(--font-serif); }
</style>
