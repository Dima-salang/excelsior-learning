<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { apiFetch } from '$lib/api';
	import { fade, fly, slide, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import {
		BrainCircuit,
		CheckCircle2,
		XCircle,
		RotateCcw,
		Sparkles,
		Loader2,
		ArrowRight,
		Trophy,
		Timer,
		Target,
		ChevronLeft,
		ChevronRight
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
		status?: string;
	}

	interface QuizState {
		cards: Card[];
		deck_id: number;
		time_started: string;
		time_spent: number;
		score: number;
	}

	let deckId = $derived((page.params as any).deckId as string);
	let quiz = $state<QuizState | null>(null);
	let allCards = $state<Card[]>([]);
	let currentIndex = $state(0);
	let currentCard = $derived(allCards[currentIndex] || null);

	let isLoading = $state(true);
	let error = $state('');
	let quizStarted = $state(false);
	let quizFinished = $state(false);

	// Track which cards have been answered locally to allow navigation
	let answeredIndices = $state<boolean[]>([]);
	let isCurrentAnswered = $derived(answeredIndices[currentIndex] || false);

	let totalCards = $derived(allCards.length);
	let startTime = $state(0);
	let elapsedTime = $state(0);
	let timerInterval = $state<number | null>(null);

	async function startQuiz() {
		try {
			isLoading = true;
			// Default to 10 cards for now
			const response = await apiFetch(`/quiz/start/${deckId}?num_flashcards=10&random_order=true`, {
				method: 'POST'
			});
			quiz = response;
			if (quiz && quiz.cards.length > 0) {
				allCards = [...quiz.cards];
				answeredIndices = new Array(allCards.length).fill(false);
				currentIndex = 0;
				quizStarted = true;
				startTime = Date.now();
				startTimer();
			} else {
				error = 'No flashcards available in this node.';
			}
		} catch (err: any) {
			error = err.message || 'Neural link failed to initialize.';
		} finally {
			isLoading = false;
		}
	}

	function startTimer() {
		timerInterval = window.setInterval(() => {
			elapsedTime = Math.floor((Date.now() - startTime) / 1000);
		}, 1000);
	}

	function stopTimer() {
		if (timerInterval) clearInterval(timerInterval);
	}

	function formatTime(seconds: number) {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	async function handleAnswer(isCorrect: boolean, selectedIdx: number) {
		if (!quiz || !currentCard) return;

		try {
			// Notify backend (using the service logic)
			const response = await apiFetch('/quiz/submit', {
				method: 'POST',
				body: JSON.stringify({
					card_id: currentCard.id,
					user_selected_ans: selectedIdx,
					quiz: quiz
				})
			});

			const { quiz: updatedQuiz, is_correct: wasCorrect } = response;

			quiz = updatedQuiz;

			// Update local card status
			if (allCards[currentIndex]) {
				allCards[currentIndex].status = wasCorrect ? 'MASTERED' : 'NOT_MASTERED';
			}

			answeredIndices[currentIndex] = true;
		} catch (err) {
			console.error('Submission failed:', err);
		}
	}

	function nextCard() {
		if (currentIndex < totalCards - 1) {
			currentIndex++;
		} else {
			finishQuiz();
		}
	}

	function prevCard() {
		if (currentIndex > 0) {
			currentIndex--;
		}
	}

	async function finishQuiz() {
		stopTimer();
		quizFinished = true;
		if (quiz) {
			quiz.time_spent = elapsedTime;
			try {
				const response = await apiFetch('/quiz/save', {
					method: 'POST',
					body: JSON.stringify(quiz)
				});
				// Optionally redirect to the permanent results page
				// goto(`/quiz/view/${response.id}`);
			} catch (err) {
				console.error('Failed to save quiz results:', err);
			}
		}
	}

	onMount(() => {
		// Auto-start for now, or could show an intro screen
		startQuiz();
	});

	$inspect(quiz);
</script>

<svelte:head>
	<title>Neural Evaluation — Excelsior</title>
</svelte:head>

<div class="min-h-[calc(100vh-64px)] w-full text-foreground selection:bg-primary/30">
	<div class="relative z-10 container mx-auto max-w-4xl px-6 py-12 md:py-20">
		{#if isLoading}
			<div class="flex flex-col items-center justify-center space-y-8 py-32" in:fade>
				<div class="relative">
					<div class="absolute inset-0 animate-pulse rounded-full bg-primary/20 blur-2xl"></div>
					<Loader2 class="relative z-10 h-16 w-16 animate-spin text-primary" />
				</div>
				<div class="space-y-2 text-center">
					<h2 class="font-display text-xl font-black tracking-widest uppercase italic">
						Synthesizing Evaluation
					</h2>
					<p class="font-sans text-muted-foreground italic">Calibrating neural synapses...</p>
				</div>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center space-y-8 py-20 text-center" in:fade>
				<div class="rounded-[2.5rem] border border-destructive/10 bg-destructive/5 p-8 shadow-2xl">
					<XCircle class="mx-auto h-16 w-16 text-destructive" />
				</div>
				<div class="space-y-4">
					<h2 class="font-display text-3xl font-black text-foreground uppercase italic">{error}</h2>
					<p class="mx-auto max-w-md text-muted-foreground">
						The connection to the knowledge base was interrupted. Please re-initialize the link.
					</p>
				</div>
				<Button
					onclick={() => goto(`/decks/${deckId}`)}
					variant="outline"
					class="h-14 rounded-2xl border-border px-8 font-black tracking-widest uppercase"
				>
					Return to Deck
				</Button>
			</div>
		{:else if quizFinished && quiz}
			<div class="space-y-12" in:fly={{ y: 40, duration: 800 }}>
				<header class="space-y-6 text-center">
					<div
						class="inline-flex items-center gap-3 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-6 py-2 text-emerald-400"
					>
						<Trophy class="h-5 w-5" />
						<span class="text-[10px] font-black tracking-[0.2em] uppercase"
							>Evaluation Terminated</span
						>
					</div>
					<h1
						class="font-display text-5xl leading-tight font-black tracking-tighter uppercase md:text-7xl"
					>
						Neural Sync <span class="text-primary italic">Complete</span>
					</h1>
				</header>

				<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
					<div
						class="flex flex-col items-center justify-center space-y-2 rounded-[2.5rem] border border-border bg-card/50 p-8 text-center backdrop-blur-xl"
					>
						<span class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
							>Accuracy</span
						>
						<div class="font-display text-4xl font-black text-primary">
							{Math.round((quiz.score / totalCards) * 100)}%
						</div>
					</div>
					<div
						class="flex flex-col items-center justify-center space-y-2 rounded-[2.5rem] border border-border bg-card/50 p-8 text-center backdrop-blur-xl"
					>
						<span class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
							>Correct Nodes</span
						>
						<div class="font-display text-4xl font-black text-emerald-400">
							{quiz.score} / {totalCards}
						</div>
					</div>
					<div
						class="flex flex-col items-center justify-center space-y-2 rounded-[2.5rem] border border-border bg-card/50 p-8 text-center backdrop-blur-xl"
					>
						<span class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
							>Time Spent</span
						>
						<div class="font-display text-4xl font-black text-accent">
							{formatTime(elapsedTime)}
						</div>
					</div>
				</div>

				<div class="flex flex-col justify-center gap-4 pt-8 sm:flex-row">
					<Button
						size="lg"
						onclick={() => location.reload()}
						class="h-16 rounded-2xl bg-primary px-10 font-black tracking-widest text-primary-foreground uppercase transition-transform hover:scale-105"
					>
						<RotateCcw class="mr-3 h-5 w-5" />
						Re-Synchronize
					</Button>
					<Button
						variant="outline"
						size="lg"
						onclick={() => goto(`/quiz`)}
						class="h-16 rounded-2xl border-border px-10 font-black tracking-widest uppercase hover:bg-card"
					>
						View History
					</Button>
				</div>
			</div>
		{:else if quizStarted && currentCard}
			<div class="space-y-8" in:fade>
				<!-- Quiz Header / Progress -->
				<div class="flex items-center justify-between">
					<Button
						variant="ghost"
						onclick={() => goto(`/decks/${deckId}`)}
						class="group flex items-center gap-2 text-slate-500 hover:text-white"
					>
						<ChevronLeft class="h-4 w-4 transition-transform group-hover:-translate-x-1" />
						<span class="text-[10px] font-black tracking-widest uppercase">Abort Session</span>
					</Button>

					<div class="flex items-center gap-6">
						<div class="hidden items-center gap-2 text-slate-400 md:flex">
							<Timer class="h-4 w-4" />
							<span class="text-[10px] font-black tracking-widest uppercase tabular-nums"
								>{formatTime(elapsedTime)}</span
							>
						</div>
						<div class="flex items-center gap-3">
							<span class="text-[10px] font-black tracking-widest text-indigo-400 uppercase">
								Node {currentIndex + 1} of {totalCards}
							</span>
							<div class="h-1.5 w-32 overflow-hidden rounded-full bg-slate-800">
								<div
									class="h-full bg-indigo-500 transition-all duration-700 ease-out"
									style="width: {((currentIndex + 1) / totalCards) * 100}%"
								></div>
							</div>
						</div>
					</div>
				</div>

				<!-- Main Card Area -->
				<div class="relative flex items-center justify-center gap-4 py-8">
					<!-- Previous Arrow -->
					<button
						onclick={(e) => {
							e.preventDefault();
							e.stopPropagation();
							prevCard();
						}}
						disabled={currentIndex === 0}
						class="relative z-50 flex h-14 w-14 shrink-0 cursor-pointer items-center justify-center rounded-full border border-white/10 bg-slate-900/80 text-white shadow-2xl transition-all hover:bg-indigo-600 disabled:cursor-not-allowed disabled:opacity-10"
						aria-label="Previous card"
					>
						<ChevronLeft class="h-8 w-8" />
					</button>

					<div class="relative z-10 max-w-2xl min-w-0 flex-grow">
						{#key currentIndex}
							<div in:fly={{ x: 20, duration: 400 }} out:fade={{ duration: 200 }}>
								<Flashcard {...currentCard} onAnswered={handleAnswer} />
							</div>
						{/key}
					</div>

					<!-- Next Arrow -->
					<button
						onclick={(e) => {
							e.preventDefault();
							e.stopPropagation();
							nextCard();
						}}
						disabled={!isCurrentAnswered && currentIndex < totalCards - 1}
						class="relative z-50 flex h-14 w-14 shrink-0 cursor-pointer items-center justify-center rounded-full border border-white/10 bg-slate-900/80 text-white shadow-2xl transition-all hover:bg-indigo-600 disabled:cursor-not-allowed disabled:opacity-10"
						aria-label="Next card"
					>
						<ChevronRight class="h-8 w-8" />
					</button>
				</div>

				<!-- Floating Action Button - Only appears after answer or at the end -->
				{#if isCurrentAnswered || currentIndex === totalCards - 1}
					<div class="mt-12 flex justify-center" in:scale={{ start: 0.8, duration: 400 }}>
						{#if currentIndex === totalCards - 1}
							<Button
								onclick={finishQuiz}
								size="lg"
								class="group h-16 rounded-2xl bg-emerald-600 px-12 font-black tracking-[0.2em] uppercase shadow-[0_0_40px_rgba(16,185,129,0.4)] transition-all hover:scale-105 active:scale-95"
							>
								Conclude Sync
								<CheckCircle2 class="ml-3 h-5 w-5" />
							</Button>
						{:else}
							<Button
								onclick={nextCard}
								size="lg"
								class="group h-16 rounded-2xl bg-indigo-600 px-12 font-black tracking-[0.2em] uppercase shadow-[0_0_40px_rgba(79,70,229,0.4)] transition-all hover:scale-105 active:scale-95"
							>
								Next Node
								<ArrowRight class="ml-3 h-5 w-5 transition-transform group-hover:translate-x-1" />
							</Button>
						{/if}
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	:global(body) {
		background-color: var(--background);
	}

	:global(.font-display) {
		font-family: var(--font-display, 'Unbounded', sans-serif);
	}

	:global(.font-sans) {
		font-family: var(--font-sans, 'Inter', sans-serif);
	}
</style>
