<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import { fade, fly, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import {
		Clock,
		Trophy,
		Timer,
		ChevronRight,
		History,
		BrainCircuit,
		Loader2,
		Search,
		Filter,
		ChevronDown
	} from '@lucide/svelte';
	import { goto } from '$app/navigation';

	interface QuizHistory {
		id: number;
		deck_id: number;
		deck_title?: string;
		time_started: string;
		time_spent: number;
		score: number;
		created_at: string;
	}

	interface PaginatedResponse<T> {
		items: T[];
		total: number;
		page: number;
		size: number;
	}

	let quizzes = $state<QuizHistory[]>([]);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');
	let currentPage = $state(1);
	let totalQuizzes = $state(0);
	const pageSize = 10;
	let hasMoreQuizzes = $derived(currentPage * pageSize < totalQuizzes);

	async function fetchQuizzes() {
		try {
			isLoading = true;
			const response = await apiFetch(`/quiz/?limit=${pageSize}&offset=0`);
			quizzes = response.items || [];
			totalQuizzes = response.total || 0;
			currentPage = 1;
		} catch (err: any) {
			error = err.message || 'Failed to load quiz history.';
		} finally {
			isLoading = false;
		}
	}

	async function loadMoreQuizzes() {
		if (isLoadingMore || !hasMoreQuizzes) return;

		isLoadingMore = true;
		try {
			const nextPage = currentPage + 1;
			const offset = (nextPage - 1) * pageSize;
			const response = await apiFetch(`/quiz/?limit=${pageSize}&offset=${offset}`);
			quizzes = [...quizzes, ...(response.items || [])];
			currentPage = nextPage;
		} catch (err: any) {
			error = err.message || 'Failed to load more quizzes.';
		} finally {
			isLoadingMore = false;
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
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	onMount(fetchQuizzes);
</script>

<svelte:head>
	<title>Quiz History — Excelsior</title>
</svelte:head>

<div class="relative min-h-[calc(100vh-64px)] w-full">
	<div class="relative z-10 container mx-auto max-w-6xl px-6 py-12 md:py-20">
		<header class="mb-16 space-y-4" in:fly={{ y: -20, duration: 800 }}>
			<div
				class="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-black tracking-widest text-primary uppercase"
			>
				<History class="h-3.5 w-3.5" />
				{#if totalQuizzes > 0}
					{quizzes.length}{totalQuizzes > quizzes.length ? `/${totalQuizzes}` : ''} Records
				{:else}
					Past Results
				{/if}
			</div>
			<div class="flex flex-col justify-between gap-6 md:flex-row md:items-end">
				<div class="space-y-2">
					<h1
						class="font-display text-4xl leading-none font-black tracking-tighter uppercase md:text-6xl"
					>
						Quiz <span class="text-primary italic">History</span>
					</h1>
					<p class="max-w-xl font-sans text-lg text-muted-foreground">
						Review your past performance and study records.
					</p>
				</div>

				<div class="flex items-center gap-3">
					<div class="group relative">
						<div
							class="absolute inset-0 rounded-full bg-primary/5 blur-xl transition-all group-hover:bg-primary/10"
						></div>
						<div
							class="relative flex w-full items-center rounded-2xl border border-border bg-card/50 px-4 py-2 backdrop-blur-xl md:w-64"
						>
							<Search class="mr-2 h-4 w-4 text-muted-foreground" />
							<input
								type="text"
								placeholder="Search records..."
								class="w-full border-none bg-transparent text-sm outline-none placeholder:text-muted-foreground/50"
							/>
						</div>
					</div>
					<Button
						variant="outline"
						class="rounded-2xl border-border px-4 py-6 transition-all hover:bg-primary/5"
					>
						<Filter class="h-4 w-4" />
					</Button>
				</div>
			</div>
		</header>

		{#if isLoading}
			<div class="flex flex-col items-center justify-center space-y-8 py-32" in:fade>
				<div class="relative">
					<div class="absolute inset-0 animate-pulse rounded-full bg-primary/20 blur-2xl"></div>
					<Loader2 class="relative z-10 h-16 w-16 animate-spin text-primary" />
				</div>
				<p class="font-sans text-sm tracking-widest text-muted-foreground uppercase italic">
					Loading quizzes...
				</p>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center space-y-8 py-20 text-center" in:fade>
				<div class="rounded-[2.5rem] border border-destructive/10 bg-destructive/5 p-8">
					<p class="font-display font-black text-destructive uppercase">{error}</p>
				</div>
				<Button onclick={fetchQuizzes} variant="outline" class="rounded-2xl border-border px-8">
					Retry Connection
				</Button>
			</div>
		{:else if quizzes.length === 0}
			<div class="flex flex-col items-center justify-center space-y-8 py-32 text-center" in:fade>
				<div
					class="flex h-24 w-24 items-center justify-center rounded-full border border-border/50 bg-muted/20"
				>
					<BrainCircuit class="h-12 w-12 text-muted-foreground" />
				</div>
				<div class="space-y-2">
					<h3 class="font-display text-2xl font-black uppercase">No Data Found</h3>
					<p class="mx-auto max-w-md text-muted-foreground">
						You haven't completed any quizzes yet. Start a quiz from your decks to begin building
						your record.
					</p>
				</div>
				<Button
					onclick={() => goto('/dashboard')}
					class="h-14 rounded-2xl px-8 font-black tracking-widest uppercase"
				>
					Go to Dashboard
				</Button>
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-6">
				{#each quizzes as quiz, i (quiz.id)}
					<div in:fly={{ y: 20, delay: i * 50, duration: 600 }} class="group relative">
						<!-- Hover Effect Backdrop -->
						<div
							class="absolute -inset-1 rounded-[2rem] bg-gradient-to-r from-primary/20 to-accent/20 opacity-0 blur transition duration-500 group-hover:opacity-100"
						></div>

						<button
							class="relative flex w-full cursor-pointer flex-col justify-between gap-6 rounded-[2rem] border border-border bg-card/40 p-6 text-left backdrop-blur-xl transition-all hover:border-primary/50 focus:ring-2 focus:ring-primary/50 focus:outline-none md:flex-row md:items-center md:p-8"
							onclick={() => goto(`/quiz/view/${quiz.id}`)}
						>
							<div class="flex items-center gap-6">
								<div
									class="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10 transition-transform duration-500 group-hover:scale-110"
								>
									<Trophy class="h-8 w-8 text-primary" />
								</div>

								<div class="space-y-1">
									<h3
										class="font-display text-xl font-black uppercase transition-colors group-hover:text-primary md:text-2xl"
									>
										{quiz.deck_title}
									</h3>
									<div class="flex items-center gap-4 text-sm font-medium text-muted-foreground">
										<span class="flex items-center gap-1.5">
											<Clock class="h-3.5 w-3.5" />
											{formatDate(quiz.created_at)}
										</span>
										<span class="h-1 w-1 rounded-full bg-border"></span>
										<span
											class="flex items-center gap-1.5 text-[10px] font-black tracking-wider text-primary/70 uppercase"
										>
											{quiz.deck_title}
										</span>
									</div>
								</div>
							</div>

							<div class="flex items-center gap-4 md:gap-12">
								<div class="flex flex-col items-center md:items-end">
									<span
										class="pb-1 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
										>Accuracy</span
									>
									<span
										class="font-display text-2xl font-black {quiz.score > 7
											? 'text-emerald-400'
											: 'text-primary'}"
									>
										{Math.round(quiz.score * 10)}%
									</span>
								</div>

								<div
									class="flex flex-col items-center border-l border-border pl-4 md:items-end md:pl-12"
								>
									<span
										class="pb-1 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
										>Time Spent</span
									>
									<div
										class="flex items-center gap-2 font-display text-xl font-black text-foreground"
									>
										<Timer class="h-4 w-4 text-accent" />
										{formatTime(quiz.time_spent)}
									</div>
								</div>

								<div class="ml-4 hidden flex-shrink-0 md:block">
									<div
										class="flex h-10 w-10 items-center justify-center rounded-full bg-border/50 transition-all group-hover:bg-primary group-hover:text-primary-foreground"
									>
										<ChevronRight class="h-6 w-6" />
									</div>
								</div>
							</div>
						</button>
					</div>
				{/each}
			</div>

			{#if hasMoreQuizzes && !isLoading}
				<div class="mt-12 flex justify-center">
					<Button
						onclick={loadMoreQuizzes}
						disabled={isLoadingMore}
						variant="outline"
						class="group flex h-14 items-center gap-3 rounded-2xl border-border px-10 font-black tracking-widest uppercase transition-all hover:bg-primary/5 disabled:opacity-50"
					>
						{#if isLoadingMore}
							<Loader2 class="h-5 w-5 animate-spin" />
							Loading...
						{:else}
							<ChevronDown class="h-5 w-5 transition-transform group-hover:translate-y-1" />
							Load More
						{/if}
					</Button>
				</div>
			{/if}
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
