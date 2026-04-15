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

	let isLoading = $state(false);
	let error = $state('');
	let quizStarted = $state(false);
	let quizFinished = $state(false);

	let randomOrder = $state(true);
	let ignoreInterval = $state(true);
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
		error = '';
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
				startTime = Date.now();
				startTimer();
			} else {
				error = 'No cards are due for review. Enable "Include All Cards" to study anyway.';
			}
		} catch (err: any) {
			error = err.message || 'Failed to start quiz. Please try again.';
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
		// If incorrect, instantly set rating to 1 and don't auto-advance so the user
		// can read the explanation. They will click "Next Question" manually.
		if (!isCorrect) {
			submitRating(1, false);
		}
	}

	function submitRating(rating: number, autoAdvance: boolean = true) {
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

				if (autoAdvance) {
					// Auto-advance after a short pause so the rating registers visually
					setTimeout(() => {
						nextCard();
					}, 350);
				}
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
		{#if !quizStarted && !quizFinished}
			<!-- Setup Screen -->
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
						<!-- Card count slider -->
						<div class="space-y-4">
							<div class="flex items-center justify-between">
								<label for="num-cards" class="flex flex-col gap-1">
									<span
										class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
										>Number of Cards</span
									>
									<span class="text-xs text-muted-foreground"
										>How many flashcards to include in this session</span
									>
								</label>
								<span class="font-display text-2xl font-black text-primary">{numFlashcards}</span>
							</div>
							<input
								type="range"
								min="5"
								max="50"
								step="5"
								bind:value={numFlashcards}
								id="num-cards"
								class="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-800 accent-primary"
							/>
							<div
								class="flex justify-between text-[9px] font-black tracking-widest text-muted-foreground uppercase"
							>
								<span>5</span>
								<span>10</span>
								<span>15</span>
								<span>20</span>
								<span>25</span>
								<span>30</span>
								<span>35</span>
								<span>40</span>
								<span>45</span>
								<span>50</span>
							</div>
						</div>

						<!-- Divider -->
						<div class="h-px bg-border"></div>

						<!-- Randomize Order toggle -->
						<div
							class="flex items-center justify-between rounded-2xl border border-border bg-muted/30 p-5"
						>
							<div class="flex items-center gap-4">
								<div
									class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10"
								>
									<Shuffle class="h-5 w-5 text-primary" />
								</div>
								<div>
									<span class="block font-display text-sm font-black uppercase">Shuffle Cards</span>
									<span class="text-xs text-muted-foreground"
										>Present cards in a random order each time</span
									>
								</div>
							</div>
							<!-- Toggle -->
							<button
								type="button"
								role="switch"
								aria-checked={randomOrder}
								onclick={() => (randomOrder = !randomOrder)}
								class="relative h-7 w-14 shrink-0 overflow-hidden rounded-full transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none {randomOrder
									? 'bg-primary'
									: 'bg-slate-700'}"
							>
								<span
									class="pointer-events-none absolute top-[3px] left-[3px] h-[22px] w-[22px] rounded-full bg-white shadow-md transition-transform duration-200 {randomOrder
										? 'translate-x-7'
										: 'translate-x-0'}"
								></span>
								<span class="sr-only">{randomOrder ? 'On' : 'Off'}</span>
							</button>
						</div>

						<!-- Ignore Interval toggle -->
						<div
							class="flex items-center justify-between rounded-2xl border border-border bg-muted/30 p-5"
						>
							<div class="flex items-center gap-4">
								<div
									class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent/10"
								>
									<Calendar class="h-5 w-5 text-accent" />
								</div>
								<div>
									<span class="block font-display text-sm font-black uppercase"
										>Include All Cards</span
									>
									<span class="text-xs text-muted-foreground"
										>Study all cards now, ignoring the spaced repetition schedule</span
									>
								</div>
							</div>
							<!-- Toggle -->
							<button
								type="button"
								role="switch"
								aria-checked={ignoreInterval}
								onclick={() => (ignoreInterval = !ignoreInterval)}
								class="relative h-7 w-14 shrink-0 overflow-hidden rounded-full transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none {ignoreInterval
									? 'bg-primary'
									: 'bg-slate-700'}"
							>
								<span
									class="pointer-events-none absolute top-[3px] left-[3px] h-[22px] w-[22px] rounded-full bg-white shadow-md transition-transform duration-200 {ignoreInterval
										? 'translate-x-7'
										: 'translate-x-0'}"
								></span>
								<span class="sr-only">{ignoreInterval ? 'On' : 'Off'}</span>
							</button>
						</div>

						<!-- Info note about interval -->
						{#if !ignoreInterval}
							<div
								class="flex items-start gap-3 rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4"
								in:slide
							>
								<AlertCircle class="mt-0.5 h-4 w-4 shrink-0 text-yellow-400" />
								<p class="text-xs text-yellow-300/80">
									Only cards that are <strong>due for review</strong> today will appear. If no cards
									are due, the quiz won't start. Toggle <strong>Include All Cards</strong> to study everything
									regardless.
								</p>
							</div>
						{/if}

						<!-- Error message inline on setup screen -->
						{#if error}
							<div
								class="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 p-4"
								in:slide
							>
								<XCircle class="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
								<p class="text-sm text-destructive">{error}</p>
							</div>
						{/if}
					</div>
				</div>

				<div class="flex flex-col justify-center gap-4 sm:flex-row">
					<Button
						size="lg"
						onclick={() => startQuiz()}
						disabled={isLoading}
						class="h-16 rounded-2xl bg-primary px-12 font-black tracking-widest uppercase shadow-[0_0_30px_rgba(var(--color-primary),0.3)] transition-all hover:scale-105 disabled:opacity-60"
					>
						{#if isLoading}
							<Loader2 class="mr-3 h-5 w-5 animate-spin" />
							Starting...
						{:else}
							<Sparkles class="mr-3 h-5 w-5" />
							Start Quiz
						{/if}
					</Button>
					<Button
						variant="outline"
						size="lg"
						onclick={() => goto(`/decks/${deckId}`)}
						class="h-16 rounded-2xl border-border px-10 font-black tracking-widest uppercase hover:bg-card"
					>
						<ArrowRight class="mr-3 h-5 w-5 rotate-180" />
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
							<div
								in:fly={{ x: 50, duration: 250, delay: 100 }}
								out:fly={{ x: -50, duration: 150 }}
							>
								<Flashcard
									{...currentCard}
									onAnswered={handleAnswer}
									showRating={pendingAnswer !== null && pendingRating === null}
								/>
							</div>
						{/key}
					</div>

					{#if pendingAnswer !== null && pendingAnswer.isCorrect && pendingRating === null}
						<div
							class="fixed right-0 bottom-0 left-0 z-50 flex justify-center p-6 sm:bottom-6 sm:p-0"
							in:fly={{ y: 50, duration: 250, opacity: 0 }}
						>
							<div
								class="w-full max-w-sm rounded-[2rem] border border-border/50 bg-card/95 p-6 shadow-2xl backdrop-blur-2xl sm:max-w-md"
							>
								<p
									class="mb-4 text-center text-xs font-black tracking-widest text-muted-foreground uppercase"
								>
									How well did you know this?
								</p>
								<div class="grid w-full grid-cols-5 gap-2 sm:gap-3">
									{#each [1, 2, 3, 4, 5] as rating}
										<div class="flex flex-col items-center justify-start gap-3">
											<button
												onclick={() => submitRating(rating)}
												disabled={pendingRating !== null}
												class="flex h-12 w-full max-w-[3.5rem] items-center justify-center rounded-xl border font-display text-lg font-black transition-all hover:-translate-y-1 hover:shadow-lg active:scale-95 {rating <=
												2
													? 'border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20 hover:shadow-red-500/10'
													: rating === 3
														? 'border-yellow-500/30 bg-yellow-500/10 text-yellow-400 hover:bg-yellow-500/20 hover:shadow-yellow-500/10'
														: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 hover:shadow-emerald-500/10'}"
											>
												{rating}
											</button>
											<span
												class="text-center text-[7px] font-black tracking-widest text-muted-foreground uppercase sm:text-[9px]"
											>
												{#if rating === 1}
													Again
												{:else if rating === 2}
													Hard
												{:else if rating === 3}
													Good
												{:else if rating === 4}
													Easy
												{:else}
													Perfect
												{/if}
											</span>
										</div>
									{/each}
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
					<div class="mt-12 flex justify-center" in:scale={{ start: 0.5, duration: 400 }}>
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
