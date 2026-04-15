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
		Loader2,
		Calendar,
		AlertCircle,
		CalendarClock
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
		next_review?: string | null;
		status?: string;
		repetition_count?: number;
		ease_factor?: number;
		day_interval?: number;
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
			error = err.message || 'System failed to retrieve deck data.';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		fetchDeck();
	});

	async function updateCardMastery(cardId: number, isCorrect: boolean, selectedAns: number) {
		try {
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

	function formatNextReview(dateStr: string | null | undefined): string {
		if (!dateStr) return 'Not scheduled';
		const date = new Date(dateStr);
		const now = new Date();
		const diff = date.getTime() - now.getTime();
		const days = Math.ceil(diff / (1000 * 60 * 60 * 24));

		if (days < 0) return 'Past due';
		if (days === 0) return 'Due today';
		if (days === 1) return 'Due tomorrow';
		return `Due in ${days} days`;
	}

	function isDue(dateStr: string | null | undefined): boolean {
		if (!dateStr) return false;
		const date = new Date(dateStr);
		return date <= new Date();
	}

	function isPastDue(dateStr: string | null | undefined): boolean {
		if (!dateStr) return false;
		const date = new Date(dateStr);
		const now = new Date();
		return date < now;
	}

	let masteredCount = $derived(deck?.cards.filter((c) => c.is_correct).length || 0);
	let totalCount = $derived(deck?.cards.length || 0);
	let progress = $derived(totalCount > 0 ? (masteredCount / totalCount) * 100 : 0);
	let dueCount = $derived(deck?.cards.filter((c) => isDue(c.next_review)).length || 0);
	let pastDueCount = $derived(deck?.cards.filter((c) => isPastDue(c.next_review)).length || 0);
</script>

<svelte:head>
	<title>{deck?.title || 'Neural Deck'} — Excelsior</title>
</svelte:head>

<div class="min-h-screen bg-transparent px-6 pt-32 pb-32">
	<div class="mx-auto max-w-6xl space-y-12">
		<!-- Navigation and Progress -->
		<div class="flex flex-col justify-between gap-6 md:flex-row md:items-center" in:fade>
			<Button
				variant="ghost"
				onclick={() => goto('/decks')}
				class="group flex w-fit items-center gap-2 px-0 text-muted-foreground hover:text-foreground"
			>
				<ArrowLeft class="h-4 w-4 transition-transform group-hover:-translate-x-1" />
				<span class="text-[10px] font-black tracking-widest uppercase">Back to Decks</span>
			</Button>

			{#if deck}
				<div class="flex flex-wrap items-center gap-6">
					<div class="flex items-center gap-2">
						<CheckCircle2 class="h-4 w-4 text-emerald-400" />
						<span class="text-[10px] font-black tracking-widest text-emerald-400 uppercase">
							{masteredCount} / {totalCount} Mastered
						</span>
					</div>
					<div class="h-1.5 w-32 overflow-hidden rounded-full bg-muted">
						<div
							class="h-full bg-primary transition-all duration-1000"
							style="width: {progress}%"
						></div>
					</div>
					{#if pastDueCount > 0}
						<div class="flex items-center gap-2">
							<AlertCircle class="h-4 w-4 text-red-400" />
							<span class="text-[10px] font-black tracking-widest text-red-400 uppercase">
								{pastDueCount} Past Due
							</span>
						</div>
					{/if}
					{#if dueCount > 0}
						<div class="flex items-center gap-2">
							<CalendarClock class="h-4 w-4 text-yellow-400" />
							<span class="text-[10px] font-black tracking-widest text-yellow-400 uppercase">
								{dueCount} Due
							</span>
						</div>
					{/if}
				</div>
			{/if}
		</div>

		{#if isLoading}
			<div class="flex flex-col items-center justify-center space-y-6 py-32">
				<Loader2 class="h-12 w-12 animate-spin text-primary" />
				<p class="max-w-2xl font-sans text-lg leading-relaxed text-muted-foreground opacity-80">
					Retrieving your study materials...
				</p>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center space-y-6 py-20 text-center">
				<div class="rounded-full border border-red-500/20 bg-red-500/10 p-6">
					<BrainCircuit class="h-12 w-12 text-red-500" />
				</div>
				<h2 class="font-display text-2xl font-black text-white uppercase italic">{error}</h2>
				<Button onclick={fetchDeck} variant="outline" class="rounded-xl border-white/10"
					>Retry Connection</Button
				>
			</div>
		{:else if deck}
			<header class="flex flex-col justify-between gap-8 md:flex-row md:items-end" in:fade>
				<div class="space-y-6">
					<h1
						class="font-display text-4xl leading-tight font-black tracking-tighter text-foreground uppercase md:text-6xl"
					>
						{deck.title}
					</h1>
					<p class="max-w-2xl font-sans text-xl leading-relaxed text-muted-foreground italic">
						{deck.description || 'Combining concepts into a unified study guide.'}
					</p>
				</div>
				<div class="flex flex-col gap-4 sm:flex-row">
					<Button
						size="lg"
						variant="outline"
						onclick={() => goto(`/quiz`)}
						class="h-16 rounded-2xl border-border px-8 font-black tracking-widest uppercase transition-all hover:bg-card"
					>
						View History
					</Button>
					<Button
						size="lg"
						onclick={() => goto(`/quiz/${id}`)}
						class="h-16 rounded-2xl bg-primary px-12 font-black tracking-widest uppercase shadow-[0_0_30_rgba(79,70,229,0.3)] transition-all hover:-translate-y-1"
					>
						Start Quiz
					</Button>
				</div>
			</header>

			<!-- Due Cards Section -->
			{#if dueCount > 0}
				<div class="space-y-8">
					<div class="flex items-center gap-4">
						<div class="h-px flex-grow bg-yellow-500/30"></div>
						<span class="flex items-center gap-2 text-[10px] font-black tracking-[0.4em] text-yellow-400 uppercase">
							<AlertCircle class="h-4 w-4" />
							Due for Review
						</span>
						<div class="h-px flex-grow bg-yellow-500/30"></div>
					</div>

					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						{#each deck.cards.filter(c => isDue(c.next_review)) as card, i}
							<div in:fly={{ y: 20, delay: i * 100 }}>
								<Flashcard
									{...card}
									compact={true}
									onAnswered={(isCorrect, selectedIdx) =>
										updateCardMastery(card.id, isCorrect, selectedIdx)}
								/>
								<div class="mt-2 flex items-center justify-between px-2">
									<span class="flex items-center gap-1 text-[9px] font-black tracking-widest {isPastDue(card.next_review) ? 'text-red-400' : 'text-yellow-400'} uppercase">
										{#if isPastDue(card.next_review)}
											<AlertCircle class="h-3 w-3" />
										{:else}
											<CalendarClock class="h-3 w-3" />
										{/if}
										{formatNextReview(card.next_review)}
									</span>
									<span class="text-[9px] font-black tracking-widest text-muted-foreground uppercase">
										Day {card.day_interval || 1}
									</span>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- All Cards Grid -->
			<div class="space-y-8">
				<div class="flex items-center gap-4">
					<div class="h-px flex-grow bg-border"></div>
					<span class="text-[10px] font-black tracking-[0.4em] text-muted-foreground uppercase"
						>All Study Cards</span
					>
					<div class="h-px flex-grow bg-border"></div>
				</div>

				<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
					{#each deck.cards as card, i}
						<div in:fly={{ y: 20, delay: i * 100 }}>
							<Flashcard
								{...card}
								compact={true}
								onAnswered={(isCorrect, selectedIdx) =>
									updateCardMastery(card.id, isCorrect, selectedIdx)}
							/>
							<div class="mt-2 flex items-center justify-between px-2">
								<span class="flex items-center gap-1 text-[9px] font-black tracking-widest {isPastDue(card.next_review) ? 'text-red-400' : isDue(card.next_review) ? 'text-yellow-400' : 'text-muted-foreground'} uppercase">
									<Calendar class="h-3 w-3" />
									{formatNextReview(card.next_review)}
								</span>
								<span class="text-[9px] font-black tracking-widest text-muted-foreground uppercase">
									{card.status || 'UNANSWERED'}
								</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	:global(.font-display) {
		font-family: var(--font-display, 'Unbounded', sans-serif);
	}
	:global(.font-sans) {
		font-family: var(--font-sans, 'Inter', sans-serif);
	}
</style>
