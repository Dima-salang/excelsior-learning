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
				await apiFetch('/quiz/save', {
					method: 'POST',
					body: JSON.stringify(quiz)
				});
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

<div class="min-h-screen bg-slate-950 text-slate-50 selection:bg-indigo-500/30">
	<!-- Background grid/blobs -->
	<div class="fixed inset-0 overflow-hidden pointer-events-none">
		<div class="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full"></div>
		<div class="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-emerald-500/10 blur-[120px] rounded-full"></div>
		<div class="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:radial-gradient(white,transparent)] opacity-20"></div>
	</div>

	<div class="relative z-10 container mx-auto max-w-4xl px-6 py-12 md:py-24">
		{#if isLoading}
			<div class="flex flex-col items-center justify-center py-32 space-y-8" in:fade>
				<div class="relative">
					<div class="absolute inset-0 bg-indigo-500/20 blur-2xl rounded-full animate-pulse"></div>
					<Loader2 class="w-16 h-16 text-indigo-400 animate-spin relative z-10" />
				</div>
				<div class="text-center space-y-2">
					<h2 class="text-xl font-unbounded font-black tracking-widest uppercase italic">Synthesizing Evaluation</h2>
					<p class="text-slate-400 font-sans italic">Calibrating neural synapses...</p>
				</div>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center py-20 text-center space-y-8" in:fade>
				<div class="p-8 rounded-[2.5rem] bg-red-500/5 border border-red-500/10 shadow-2xl">
					<XCircle class="w-16 h-16 text-red-500 mx-auto" />
				</div>
				<div class="space-y-4">
					<h2 class="text-3xl font-unbounded font-black text-white uppercase italic">{error}</h2>
					<p class="text-slate-400 max-w-md mx-auto">The connection to the knowledge base was interrupted. Please re-initialize the link.</p>
				</div>
				<Button onclick={() => goto(`/decks/${deckId}`)} variant="outline" class="rounded-2xl border-white/10 px-8 h-14 uppercase font-black tracking-widest">
					Return to Deck
				</Button>
			</div>
		{:else if quizFinished && quiz}
			<div class="space-y-12" in:fly={{ y: 40, duration: 800 }}>
				<header class="text-center space-y-6">
					<div class="inline-flex items-center gap-3 px-6 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
						<Trophy class="w-5 h-5" />
						<span class="text-sm font-black tracking-[0.2em] uppercase">Evaluation Terminated</span>
					</div>
					<h1 class="text-5xl md:text-7xl font-unbounded font-black tracking-tighter uppercase leading-tight">
						Neural Sync Complete
					</h1>
				</header>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div class="p-8 rounded-[2.5rem] bg-slate-900/50 border border-white/5 backdrop-blur-xl space-y-2 flex flex-col items-center justify-center text-center">
						<span class="text-[10px] font-black tracking-widest text-slate-500 uppercase">Accuracy</span>
						<div class="text-4xl font-unbounded font-black text-indigo-400">
							{Math.round((quiz.score / totalCards) * 100)}%
						</div>
					</div>
					<div class="p-8 rounded-[2.5rem] bg-slate-900/50 border border-white/5 backdrop-blur-xl space-y-2 flex flex-col items-center justify-center text-center">
						<span class="text-[10px] font-black tracking-widest text-slate-500 uppercase">Correct Nodes</span>
						<div class="text-4xl font-unbounded font-black text-emerald-400">
							{quiz.score} / {totalCards}
						</div>
					</div>
					<div class="p-8 rounded-[2.5rem] bg-slate-900/50 border border-white/5 backdrop-blur-xl space-y-2 flex flex-col items-center justify-center text-center">
						<span class="text-[10px] font-black tracking-widest text-slate-500 uppercase">Time Spent</span>
						<div class="text-4xl font-unbounded font-black text-amber-400">
							{formatTime(elapsedTime)}
						</div>
					</div>
				</div>

				<div class="flex flex-col sm:flex-row gap-4 justify-center pt-8">
					<Button 
						size="lg"
						onclick={() => location.reload()}
						class="h-16 px-10 rounded-2xl bg-white text-slate-950 font-black tracking-widest uppercase hover:scale-105 transition-transform"
					>
						<RotateCcw class="w-5 h-5 mr-3" />
						Re-Synchronize
					</Button>
					<Button 
						variant="outline"
						size="lg"
						onclick={() => goto(`/decks/${deckId}`)}
						class="h-16 px-10 rounded-2xl border-white/10 font-black tracking-widest uppercase hover:bg-white/5"
					>
						Return to Nexus
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
						class="flex items-center gap-2 text-slate-500 hover:text-white group"
					>
						<ChevronLeft class="w-4 h-4 transition-transform group-hover:-translate-x-1" />
						<span class="text-[10px] font-black tracking-widest uppercase">Abort Session</span>
					</Button>

					<div class="flex items-center gap-6">
						<div class="hidden md:flex items-center gap-2 text-slate-400">
							<Timer class="w-4 h-4" />
							<span class="text-[10px] font-black tracking-widest tabular-nums uppercase">{formatTime(elapsedTime)}</span>
						</div>
						<div class="flex items-center gap-3">
							<span class="text-[10px] font-black tracking-widest text-indigo-400 uppercase">
								Node {currentIndex + 1} of {totalCards}
							</span>
							<div class="w-32 h-1.5 rounded-full bg-slate-800 overflow-hidden">
								<div 
									class="h-full bg-indigo-500 transition-all duration-700 ease-out"
									style="width: {((currentIndex + 1) / totalCards) * 100}%"
								></div>
							</div>
						</div>
					</div>
				</div>

				<!-- Main Card Area -->
				<div class="relative py-8 flex items-center justify-center gap-4">
					<!-- Previous Arrow -->
					<button 
						onclick={(e) => { e.preventDefault(); e.stopPropagation(); prevCard(); }}
						disabled={currentIndex === 0}
						class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-white/10 bg-slate-900/80 text-white shadow-2xl transition-all hover:bg-indigo-600 disabled:opacity-10 disabled:cursor-not-allowed relative z-50 cursor-pointer"
						aria-label="Previous card"
					>
						<ChevronLeft class="w-8 h-8" />
					</button>

					<div class="flex-grow max-w-2xl min-w-0 relative z-10">
						{#key currentIndex}
							<div in:fly={{ x: 20, duration: 400 }} out:fade={{ duration: 200 }}>
								<Flashcard 
									{...currentCard}
									onAnswered={handleAnswer}
								/>
							</div>
						{/key}
					</div>

					<!-- Next Arrow -->
					<button 
						onclick={(e) => { e.preventDefault(); e.stopPropagation(); nextCard(); }}
						disabled={!isCurrentAnswered && currentIndex < totalCards - 1}
						class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-white/10 bg-slate-900/80 text-white shadow-2xl transition-all hover:bg-indigo-600 disabled:opacity-10 disabled:cursor-not-allowed relative z-50 cursor-pointer"
						aria-label="Next card"
					>
						<ChevronRight class="w-8 h-8" />
					</button>
				</div>
					
				<!-- Floating Action Button - Only appears after answer or at the end -->
				{#if isCurrentAnswered || currentIndex === totalCards - 1}
					<div class="flex justify-center mt-12" in:scale={{ start: 0.8, duration: 400 }}>
						{#if currentIndex === totalCards - 1}
							<Button 
								onclick={finishQuiz}
								size="lg"
								class="h-16 px-12 rounded-2xl bg-emerald-600 font-black tracking-[0.2em] uppercase shadow-[0_0_40px_rgba(16,185,129,0.4)] hover:scale-105 active:scale-95 transition-all group"
							>
								Conclude Sync
								<CheckCircle2 class="w-5 h-5 ml-3" />
							</Button>
						{:else}
							<Button 
								onclick={nextCard}
								size="lg"
								class="h-16 px-12 rounded-2xl bg-indigo-600 font-black tracking-[0.2em] uppercase shadow-[0_0_40px_rgba(79,70,229,0.4)] hover:scale-105 active:scale-95 transition-all group"
							>
								Next Node
								<ArrowRight class="w-5 h-5 ml-3 transition-transform group-hover:translate-x-1" />
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
		background-color: #020617;
	}

	.font-unbounded {
		font-family: var(--font-display, 'Inter', sans-serif);
	}
	
	.font-sans {
		font-family: var(--font-sans, 'Inter', sans-serif);
	}

	/* Custom font fallback if needed, but we should use the one from theme */
</style>
