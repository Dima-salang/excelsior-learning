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
		ChevronRight,
		Shuffle,
		Calendar,
		AlertCircle
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
	let showSetupScreen = $state(true);

	let randomOrder = $state(true);
	let ignoreInterval = $state(false);
	let numFlashcards = $state(10);
	let pendingAnswer = $state<{ isCorrect: boolean; selectedIdx: number } | null>(null);
	let pendingRating = $state<number | null>(null);

	let answeredIndices = $state<boolean[]>([]);
	let isCurrentAnswered = $derived(answeredIndices[currentIndex] || false);

	let totalCards = $derived(allCards.length);
	let startTime = $state(0);
	let elapsedTime = $state(0);
	let timerInterval = $state<number | null>(null);

	async function startQuiz() {
		try {
			isLoading = true;
			const response = await apiFetch(
				`/quiz/start/${deckId}?num_flashcards=${numFlashcards}&random_order=${randomOrder}&ignore_interval=${ignoreInterval}`,
				{ method: 'POST' }
			);
			quiz = response;
			if (quiz && quiz.cards.length > 0) {
				allCards = [...quiz.cards];
				answeredIndices = new Array(allCards.length).fill(false);
				currentIndex = 0;
				quizStarted = true;
				showSetupScreen = false;
				startTime = Date.now();
				startTimer();
			} else {
				error = 'No flashcards available in this node.';
			}
		} catch (err: any) {
			error = err.message || 'Connection failed to initialize.';
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

	function handleAnswer(isCorrect: boolean, selectedIdx: number) {
		pendingAnswer = { isCorrect, selectedIdx };
	}

	function submitRating(rating: number) {
		if (!quiz || !currentCard || !pendingAnswer) return;

		pendingRating = rating;

		apiFetch('/quiz/submit', {
			method: 'POST',
			body: JSON.stringify({
				card_id: currentCard.id,
				user_selected_ans: pendingAnswer.selectedIdx,
				quiz: quiz,
				user_rating: rating
			})
		})
			.then((response) => {
				const { quiz: updatedQuiz, is_correct: wasCorrect } = response;
				quiz = updatedQuiz;

				if (allCards[currentIndex]) {
					allCards[currentIndex].status = wasCorrect ? 'MASTERED' : 'NOT_MASTERED';
				}

				answeredIndices[currentIndex] = true;
				pendingAnswer = null;
				pendingRating = null;
			})
			.catch((err) => {
				console.error('Submission failed:', err);
				pendingAnswer = null;
				pendingRating = null;
			});
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
			} catch (err) {
				console.error('Failed to save quiz results:', err);
			}
		}
	}
</script>

<svelte:head>
	<title>Quiz — Excelsior</title>
</svelte:head>

	<div class="min-h-[calc(100vh-64px)] w-full text-foreground selection:bg-primary/30">
	<div class="relative z-10 container mx-auto max-w-4xl px-6 py-12 md:py-20">
		{#if showSetupScreen && !quizStarted}
			<div class="space-y-12" in:fade>
				<header class="space-y-6 text-center">
					<div class="relative inline-block">
						<div class="absolute inset-0 scale-150 rounded-full bg-primary/20 blur-3xl"></div>
						<div
							class="relative flex h-24 w-24 items-center justify-center rounded-[2rem] border border-primary/20 bg-card shadow-2xl"
						>
							<BrainCircuit class="h-12 w-12 text-primary" />
						</div>
					</div>
					<h1
						class="font-display text-5xl leading-tight font-black tracking-tighter uppercase md:text-7xl"
					>
						Configure <span class="text-primary italic">Quiz</span>
					</h1>
					<p class="mx-auto max-w-md text-muted-foreground">
						Customize your study session to match your learning goals.
					</p>
				</header>

				<div class="rounded-[2.5rem] border border-border bg-card/50 p-8 backdrop-blur-xl">
					<div class="space-y-8">
						<div class="space-y-4">
							<label class="flex items-center gap-3">
								<span class="text-[10px] font-black tracking-widest uppercase text-muted-foreground">Number of Cards</span>
							</label>
							<div class="flex items-center gap-4">
								<input
									type="range"
									min="5"
									max="50"
									step="5"
									bind:value={numFlashcards}
									class="h-2 flex-1 cursor-pointer appearance-none rounded-full bg-slate-800 accent-primary"
								/>
								<span class="w-12 text-center font-display text-lg font-black text-primary">{numFlashcards}</span>
							</div>
						</div>

						<div class="flex items-center justify-between rounded-2xl border border-border bg-muted/30 p-4">
							<div class="flex items-center gap-3">
								<Shuffle class="h-5 w-5 text-primary" />
								<div>
									<span class="block font-display text-sm font-black uppercase">Randomize Order</span>
									<span class="text-xs text-muted-foreground">Shuffle cards for varied practice</span>
								</div>
							</div>
							<button
								onclick={() => randomOrder = !randomOrder}
								class="relative h-6 w-12 rounded-full transition-colors {randomOrder ? 'bg-primary' : 'bg-slate-700'}"
							>
								<span
									class="absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform {randomOrder ? 'translate-x-7' : 'translate-x-1'}"
								></span>
							</button>
						</div>

						<div class="flex items-center justify-between rounded-2xl border border-border bg-muted/30 p-4">
							<div class="flex items-center gap-3">
								<AlertCircle class="h-5 w-5 text-accent" />
								<div>
									<span class="block font-display text-sm font-black uppercase">Ignore Interval</span>
									<span class="text-xs text-muted-foreground">Include all cards regardless of due date</span>
								</div>
							</div>
							<button
								onclick={() => ignoreInterval = !ignoreInterval}
								class="relative h-6 w-12 rounded-full transition-colors {ignoreInterval ? 'bg-primary' : 'bg-slate-700'}"
							>
								<span
									class="absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform {ignoreInterval ? 'translate-x-7' : 'translate-x-1'}"
								></span>
							</button>
						</div>
					</div>
				</div>

				<div class="flex flex-col justify-center gap-4 sm:flex-row">
					<Button
						size="lg"
						onclick={() => startQuiz()}
						class="h-16 rounded-2xl bg-primary px-12 font-black tracking-widest uppercase shadow-[0_0_30px_rgba(var(--color-primary),0.3)] transition-all hover:scale-105"
					>
						<Sparkles class="mr-3 h-5 w-5" />
						Start Quiz
					</Button>
					<Button
						variant="outline"
						size="lg"
						onclick={() => goto(`/decks/${deckId}`)}
						class="h-16 rounded-2xl border-border px-10 font-black tracking-widest uppercase hover:bg-card"
					>
						<ArrowRight class="mr-3 h-5 w-5" />
						Back to Deck
					</Button>
				</div>
			</div>
		{:else if isLoading}
			<div class="flex flex-col items-center justify-center space-y-8 py-32" in:fade>
				<div class="relative">
					<div class="absolute inset-0 animate-pulse rounded-full bg-primary/20 blur-2xl"></div>
					<Loader2 class="relative z-10 h-16 w-16 animate-spin text-primary" />
				</div>
				<div class="space-y-2 text-center">
					<h2 class="font-display text-xl font-black tracking-widest uppercase italic">
						Preparing Quiz
					</h2>
					<p class="font-sans text-muted-foreground italic">Setting up your questions...</p>
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
						The connection to the server was interrupted. Please try again.
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
						<span class="text-[10px] font-black tracking-[0.2em] uppercase">Quiz Completed</span>
					</div>
					<h1
						class="font-display text-5xl leading-tight font-black tracking-tighter uppercase md:text-7xl"
					>
						Quiz <span class="text-primary italic">Result</span>
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
							>Correct Answers</span
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
						Try Again
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
						<span class="text-[10px] font-black tracking-widest uppercase">Quit Quiz</span>
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
								Question {currentIndex + 1} of {totalCards}
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
								<Flashcard {...currentCard} onAnswered={handleAnswer} showRating={pendingAnswer !== null && pendingRating === null} />
							</div>
						{/key}
					</div>

					{#if pendingAnswer !== null && pendingRating === null}
						<div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full pt-6" in:scale={{ start: 0.8, duration: 400 }}>
							<div class="rounded-2xl border border-border bg-card/80 p-6 backdrop-blur-xl">
								<p class="mb-4 text-center text-xs font-black tracking-widest uppercase text-muted-foreground">
									How well did you know this?
								</p>
								<div class="flex gap-2">
									{#each [1, 2, 3, 4, 5] as rating}
										<button
											onclick={() => submitRating(rating)}
											disabled={pendingRating !== null}
											class="flex h-12 w-12 items-center justify-center rounded-xl border font-display text-lg font-black transition-all hover:scale-110 {rating <= 2 ? 'border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20' : rating === 3 ? 'border-yellow-500/30 bg-yellow-500/10 text-yellow-400 hover:bg-yellow-500/20' : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20'}"
										>
											{rating}
										</button>
									{/each}
								</div>
								<div class="mt-2 flex justify-between text-[9px] font-black tracking-widest uppercase text-muted-foreground">
									<span>Again</span>
									<span>Hard</span>
									<span>Good</span>
									<span>Easy</span>
								</div>
							</div>
						</div>
					{/if}

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
								Finish Quiz
								<CheckCircle2 class="ml-3 h-5 w-5" />
							</Button>
						{:else}
							<Button
								onclick={nextCard}
								size="lg"
								class="group h-16 rounded-2xl bg-indigo-600 px-12 font-black tracking-[0.2em] uppercase shadow-[0_0_40px_rgba(79,70,229,0.4)] transition-all hover:scale-105 active:scale-95"
							>
								Next Question
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
