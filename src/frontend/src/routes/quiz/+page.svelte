<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import { fade, fly, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import {
		Clock,
		Trophy,
		Timer,
		ChevronRight,
		History,
		BrainCircuit,
		Loader2,
		ChevronDown
	} from 'lucide-svelte';
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

<div class="container mx-auto max-w-5xl px-6 py-12">
	<header class="mb-10 space-y-2" in:fly={{ y: -20, duration: 400 }}>
		<div class="flex items-center gap-3">
			<div class="rounded-lg bg-primary/10 p-2">
				<History class="h-5 w-5 text-primary" />
			</div>
			<span class="text-sm font-medium text-muted-foreground">
				{totalQuizzes > 0
					? `${quizzes.length}${totalQuizzes > quizzes.length ? `/${totalQuizzes}` : ''} Records`
					: 'Quiz History'}
			</span>
		</div>
		<h1 class="text-3xl font-bold tracking-tight md:text-4xl">
			Quiz <span class="text-primary">History</span>
		</h1>
		<p class="text-muted-foreground">Review your past performance and study records.</p>
	</header>

	{#if isLoading}
		<div class="flex flex-col items-center justify-center space-y-6 py-20">
			<Loader2 class="h-10 w-10 animate-spin text-primary" />
			<p class="text-sm text-muted-foreground">Loading quizzes...</p>
		</div>
	{:else if error}
		<div
			class="flex flex-col items-center justify-center space-y-4 rounded-xl border border-destructive/20 bg-destructive/10 py-12 text-center"
		>
			<p class="font-medium text-destructive">{error}</p>
			<Button onclick={fetchQuizzes} variant="outline" size="sm">Retry</Button>
		</div>
	{:else if quizzes.length === 0}
		<div
			class="flex flex-col items-center justify-center space-y-6 rounded-xl border border-dashed border-border bg-muted/30 py-20 text-center"
			in:fade
		>
			<div class="rounded-full bg-muted p-4">
				<BrainCircuit class="h-10 w-10 text-muted-foreground" />
			</div>
			<div class="space-y-2">
				<h2 class="text-xl font-semibold">No Data Found</h2>
				<p class="text-sm text-muted-foreground">
					You haven't completed any quizzes yet. Start a quiz from your decks to begin building your
					record.
				</p>
			</div>
			<Button onclick={() => goto('/dashboard')}>Go to Dashboard</Button>
		</div>
	{:else}
		<div class="space-y-4">
			{#each quizzes as quiz, i (quiz.id)}
				<button
					in:fly={{ y: 10, delay: i * 30 }}
					class="group flex w-full cursor-pointer flex-col gap-4 rounded-xl border border-border bg-card p-4 text-left transition-all hover:border-primary/30 hover:shadow-md md:flex-row md:items-center md:p-6"
					onclick={() => goto(`/quiz/view/${quiz.id}`)}
				>
					<div class="flex items-center gap-4">
						<div class="rounded-lg bg-primary/10 p-3">
							<Trophy class="h-6 w-6 text-primary" />
						</div>
						<div class="space-y-1">
							<h3 class="font-semibold transition-colors group-hover:text-primary">
								{quiz.deck_title}
							</h3>
							<div class="flex items-center gap-3 text-xs text-muted-foreground">
								<span class="flex items-center gap-1">
									<Clock class="h-3 w-3" />
									{formatDate(quiz.created_at)}
								</span>
							</div>
						</div>
					</div>

					<div class="flex items-center gap-6">
						<div class="text-center">
							<span class="block text-xs text-muted-foreground uppercase">Accuracy</span>
							<span
								class="text-xl font-bold {quiz.score > 7
									? 'text-green-600 dark:text-green-400'
									: 'text-primary'}"
							>
								{Math.round(quiz.score * 10)}%
							</span>
						</div>

						<div class="border-l border-border pl-6">
							<span class="block text-xs text-muted-foreground uppercase">Time Spent</span>
							<div class="flex items-center gap-2 font-semibold">
								<Timer class="h-4 w-4 text-muted-foreground" />
								{formatTime(quiz.time_spent)}
							</div>
						</div>

						<ChevronRight
							class="hidden h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1 md:block"
						/>
					</div>
				</button>
			{/each}
		</div>

		{#if hasMoreQuizzes}
			<div class="flex justify-center pt-6">
				<Button onclick={loadMoreQuizzes} disabled={isLoadingMore} variant="outline" class="gap-2">
					{#if isLoadingMore}
						<Loader2 class="h-4 w-4 animate-spin" />
						Loading...
					{:else}
						<ChevronDown class="h-4 w-4" />
						Load More
					{/if}
				</Button>
			</div>
		{/if}
	{/if}
</div>
