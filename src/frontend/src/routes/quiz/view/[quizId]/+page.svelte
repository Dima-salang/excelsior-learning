<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { apiFetch } from '$lib/api';
	import { fade, fly, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import {
		Trophy,
		Timer,
		RotateCcw,
		ChevronLeft,
		Calendar,
		BrainCircuit,
		Loader2,
		ArrowLeft,
		Target,
		Zap
	} from '@lucide/svelte';
	import { goto } from '$app/navigation';
	import { marked } from 'marked';

	let quizId = $derived((page.params as any).quizId as string);
	let quiz = $state<any>(null);
	let isLoading = $state(true);
	let error = $state('');

	async function fetchQuiz() {
		try {
			isLoading = true;
			quiz = await apiFetch(`/quiz/${quizId}`);
		} catch (err: any) {
			error = err.message || 'Quiz record retrieval failed.';
		} finally {
			isLoading = false;
		}
	}

	function formatTime(seconds: number) {
		const mins = Math.floor(seconds / 60);
		const secs = Math.floor(seconds % 60);
		return `${mins}m ${secs}s`;
	}

	function formatDate(dateStr: string | undefined | null) {
		if (!dateStr) return 'N/A';
		const date = new Date(dateStr);
		if (isNaN(date.getTime())) return 'Invalid Date';
		return date.toLocaleDateString('en-US', {
			weekday: 'long',
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		});
	}

	onMount(fetchQuiz);
</script>

<svelte:head>
	<title>Session Review — Excelsior</title>
</svelte:head>

<div class="relative min-h-[calc(100vh-64px)] w-full overflow-hidden">
	<!-- Background Effects -->
	<div class="pointer-events-none fixed inset-0">
		<div
			class="absolute top-[20%] right-[-10%] h-[50%] w-[50%] rounded-full bg-primary/5 blur-[120px]"
		></div>
		<div
			class="absolute bottom-[-10%] left-[-10%] h-[50%] w-[50%] rounded-full bg-accent/5 blur-[120px]"
		></div>
	</div>

	<div class="relative z-10 container mx-auto max-w-4xl px-6 py-12 md:py-24">
		{#if isLoading}
			<div class="flex flex-col items-center justify-center space-y-8 py-32" in:fade>
				<Loader2 class="h-16 w-16 animate-spin text-primary" />
				<p class="font-display text-sm font-black tracking-widest text-muted-foreground uppercase">
					Loading Results...
				</p>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center space-y-8 py-20 text-center" in:fade>
				<div class="rounded-[2.5rem] border border-destructive/10 bg-destructive/5 p-8">
					<p class="font-display font-black text-destructive uppercase">{error}</p>
				</div>
				<Button
					onclick={() => goto('/quiz')}
					variant="outline"
					class="rounded-2xl border-border px-8"
				>
					<ArrowLeft class="mr-2 h-4 w-4" /> Return to History
				</Button>
			</div>
		{:else if quiz}
			<div class="space-y-16" in:fly={{ y: 40, duration: 1000 }}>
				<header class="space-y-8 text-center">
					<div class="flex flex-col items-center gap-6">
						<Button
							variant="ghost"
							onclick={() => goto('/quiz')}
							class="group mb-4 flex items-center gap-2 text-muted-foreground hover:text-foreground"
						>
							<ChevronLeft class="h-4 w-4 transition-transform group-hover:-translate-x-1" />
							<span class="text-[10px] font-black tracking-widest uppercase">Back to History</span>
						</Button>

						<div class="relative">
							<div class="absolute inset-0 scale-150 rounded-full bg-primary/20 blur-3xl"></div>
							<div
								class="relative flex h-24 w-24 items-center justify-center rounded-[2rem] border border-primary/20 bg-card shadow-2xl"
							>
								<Trophy class="h-12 w-12 text-primary" />
							</div>
						</div>
					</div>

					<div class="space-y-4">
						<div
							class="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-black tracking-widest text-accent uppercase"
						>
							<Calendar class="h-3.5 w-3.5" />
							{formatDate(quiz.created_at)}
						</div>
						<h1
							class="font-display text-5xl leading-tight font-black tracking-tighter uppercase md:text-7xl"
						>
							Quiz <span class="text-primary italic">Result</span>
						</h1>
					</div>
				</header>

				<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
					<!-- Accuracy Card -->
					<div
						class="group space-y-4 rounded-[2.5rem] border border-border bg-card/50 p-8 text-center backdrop-blur-xl transition-all hover:border-primary/50"
					>
						<div
							class="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10"
						>
							<Target class="h-6 w-6 text-primary" />
						</div>
						<div class="space-y-1">
							<span class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
								>Accuracy</span
							>
							<div class="font-display text-5xl font-black text-foreground">
								{Math.round(quiz.score * 10)}%
							</div>
						</div>
					</div>

					<!-- Time Spent Card -->
					<div
						class="group space-y-4 rounded-[2.5rem] border border-border bg-card/50 p-8 text-center backdrop-blur-xl transition-all hover:border-accent/50"
					>
						<div
							class="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-accent/10"
						>
							<Timer class="h-6 w-6 text-accent" />
						</div>
						<div class="space-y-1">
							<span class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
								>Time Spent</span
							>
							<div class="font-display text-5xl font-black text-foreground">
								{formatTime(quiz.time_spent)}
							</div>
						</div>
					</div>

					<!-- Points Card -->
					<div
						class="group space-y-4 rounded-[2.5rem] border border-border bg-card/50 p-8 text-center backdrop-blur-xl transition-all hover:border-emerald-500/50"
					>
						<div
							class="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/10"
						>
							<Zap class="h-6 w-6 text-emerald-500" />
						</div>
						<div class="space-y-1">
							<span class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
								>Total Score</span
							>
							<div class="font-display text-5xl font-black text-foreground">
								{quiz.score}
							</div>
						</div>
					</div>
				</div>

				<div
					class="flex flex-col items-center justify-between gap-8 rounded-[3rem] border border-primary/10 bg-primary/5 p-10 md:flex-row"
				>
					<div class="flex items-center gap-6">
						<div
							class="flex h-16 w-16 items-center justify-center rounded-2xl border border-border bg-card shadow-xl"
						>
							<BrainCircuit class="h-8 w-8 text-primary" />
						</div>
						<div>
							<h3 class="font-display text-2xl font-black uppercase">Ready for another?</h3>
							<p class="text-muted-foreground">
								Practice again with this deck to improve your score.
							</p>
						</div>
					</div>
					<Button
						size="lg"
						onclick={() => goto(`/quiz/${quiz.deck_id}`)}
						class="h-16 rounded-2xl px-10 font-black tracking-widest uppercase shadow-[0_0_30px_rgba(var(--color-primary),0.3)] transition-all hover:scale-105"
					>
						<RotateCcw class="mr-3 h-5 w-5" />
						New Session
					</Button>
				</div>

				<!-- Card Review Section -->
				<div class="space-y-8" in:fade={{ delay: 200 }}>
					<div class="flex items-center gap-4">
						<div class="h-[1px] flex-1 bg-border"></div>
						<h2
							class="font-display text-xs font-black tracking-[0.3em] text-muted-foreground uppercase"
						>
							Session Review
						</h2>
						<div class="h-[1px] flex-1 bg-border"></div>
					</div>

					<div class="grid grid-cols-1 gap-6">
						{#each quiz.cards as card, i}
							<div
								class="group relative overflow-hidden rounded-[2.5rem] border border-border bg-card/50 p-8 backdrop-blur-xl transition-all"
							>
								<!-- Correct/Incorrect Indicator -->
								<div class="absolute top-0 right-0 p-6">
									{#if card.is_correct}
										<div
											class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500"
										>
											<Target class="h-5 w-5" />
										</div>
									{:else}
										<div
											class="flex h-10 w-10 items-center justify-center rounded-xl bg-destructive/10 text-destructive"
										>
											<Zap class="h-5 w-5" />
										</div>
									{/if}
								</div>

								<div class="mb-6 flex items-center gap-3">
									<span
										class="font-display text-[10px] font-black tracking-widest text-primary uppercase"
										>Question {i + 1}</span
									>
									<span class="h-1 w-1 rounded-full bg-border"></span>
									<span
										class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
										>{card.type}</span
									>
								</div>

								<h3 class="markdown-content mb-8 font-display text-xl leading-relaxed font-black">
									{@html marked.parse(card.front)}
								</h3>

								{#if card.options && card.options.length > 0}
									<div class="grid grid-cols-1 gap-3">
										{#each card.options as option, idx}
											<div
												class="flex items-center justify-between rounded-2xl border p-4 transition-all
                                                {idx === card.options_ans
													? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-500'
													: idx === card.user_selected_ans && !card.is_correct
														? 'border-destructive/30 bg-destructive/5 text-destructive'
														: 'border-border bg-muted/30 text-muted-foreground'}"
											>
												<span class="markdown-content text-sm font-medium"
													>{@html marked.parse(option)}</span
												>
												{#if idx === card.options_ans}
													<Target class="h-4 w-4" />
												{:else if idx === card.user_selected_ans && !card.is_correct}
													<Zap class="h-4 w-4" />
												{/if}
											</div>
										{/each}
									</div>
								{/if}

								{#if card.explanation}
									<div
										class="mt-8 rounded-2xl bg-muted/50 p-6 text-sm text-muted-foreground italic"
									>
										<p class="mb-2 font-display text-[8px] font-black tracking-[0.2em] uppercase">
											Explanation
										</p>
										<div class="markdown-content">
											{@html marked.parse(card.explanation)}
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	:global(.font-display) {
		font-family: var(--font-display, 'Unbounded', sans-serif);
	}
</style>
