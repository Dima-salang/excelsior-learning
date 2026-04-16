<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import {
		BrainCircuit,
		BookOpen,
		Layers,
		CalendarClock,
		TrendingUp,
		ChevronRight,
		Sparkles,
		Loader2
	} from '@lucide/svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';

	interface Lecture {
		id: number;
		title: string;
		description: string | null;
		completion_percentage: number;
		created_at: string;
		last_accessed_at: string;
	}

	interface Deck {
		id: number;
		title: string;
		description: string | null;
		created_at: string;
	}

	interface DueCardsStats {
		due_today: number;
		past_due: number;
	}

	let recentLectures = $state<Lecture[]>([]);
	let recentDecks = $state<Deck[]>([]);
	let dueCards = $state<DueCardsStats>({ due_today: 0, past_due: 0 });
	let isLoading = $state(true);
	let error = $state('');

	$effect(() => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		if (auth.user && isLoading) {
			fetchData();
		}
	});

	async function fetchData() {
		const user = auth.user;
		if (!user?.id) return;

		try {
			const [lecturesRes, decksRes, statsRes] = await Promise.all([
				apiFetch(`/lectures/?user_id=${user.id}&limit=3`),
				apiFetch(`/decks?user_id=${user.id}&limit=3`),
				apiFetch(`/decks/stats/due?user_id=${user.id}`)
			]);

			recentLectures = lecturesRes.items || [];
			recentDecks = decksRes.items || [];
			dueCards = statsRes || { due_today: 0, past_due: 0 };
		} catch (err) {
			console.error('Failed to fetch dashboard data:', err);
			error = 'Failed to load dashboard';
		} finally {
			isLoading = false;
		}
	}

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric'
		});
	}

	let totalDue = $derived(dueCards.due_today + dueCards.past_due);
</script>

<svelte:head>
	<title>Dashboard — Excelsior</title>
</svelte:head>

<div class="container mx-auto max-w-6xl space-y-10 p-6 py-12 lg:p-12">
	<header class="space-y-3" in:fade={{ duration: 400 }}>
		<div class="flex items-center gap-3">
			<div class="rounded-lg bg-primary/10 p-2">
				<BrainCircuit class="h-5 w-5 text-primary" />
			</div>
			<span class="text-sm font-medium text-muted-foreground">Dashboard</span>
		</div>
		<h1 class="font-display text-4xl font-bold tracking-tight">
			Welcome back, <span class="text-primary">{auth.user?.username || 'Learner'}</span>
		</h1>
		<p class="text-muted-foreground">Here's your learning overview for today.</p>
	</header>

	{#if isLoading}
		<div class="grid gap-6 md:grid-cols-3">
			{#each Array(3) as _}
				<div class="h-32 rounded-xl border border-border bg-muted/50"></div>
			{/each}
		</div>
	{:else}
		<!-- Stats Cards -->
		<div class="grid gap-4 md:grid-cols-3" in:fly={{ y: 20, duration: 400, delay: 100 }}>
			<button
				onclick={() => goto('/lectures')}
				class="group flex items-center gap-4 rounded-xl border border-border bg-card p-5 text-left transition-all hover:border-primary/30 hover:shadow-md"
			>
				<div class="rounded-lg bg-primary/10 p-3">
					<BookOpen class="h-6 w-6 text-primary" />
				</div>
				<div class="flex-1">
					<p class="text-2xl font-bold">{recentLectures.length}</p>
					<p class="text-sm text-muted-foreground">Active Courses</p>
				</div>
				<ChevronRight class="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
			</button>

			<button
				onclick={() => goto('/decks')}
				class="group flex items-center gap-4 rounded-xl border border-border bg-card p-5 text-left transition-all hover:border-primary/30 hover:shadow-md"
			>
				<div class="rounded-lg bg-accent/10 p-3">
					<Layers class="h-6 w-6 text-accent" />
				</div>
				<div class="flex-1">
					<p class="text-2xl font-bold">{recentDecks.length}</p>
					<p class="text-sm text-muted-foreground">Study Decks</p>
				</div>
				<ChevronRight class="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
			</button>

			<button
				onclick={() => goto('/quiz')}
				class="group flex items-center gap-4 rounded-xl border border-border bg-card p-5 text-left transition-all hover:border-primary/30 hover:shadow-md {totalDue > 0 ? 'border-warning/30' : ''}"
			>
				<div class="rounded-lg {totalDue > 0 ? 'bg-warning/10' : 'bg-muted'} p-3">
					<CalendarClock class="h-6 w-6 {totalDue > 0 ? 'text-warning' : 'text-muted-foreground'}" />
				</div>
				<div class="flex-1">
					<p class="text-2xl font-bold">{totalDue}</p>
					<p class="text-sm text-muted-foreground">Cards Due</p>
				</div>
				{#if totalDue > 0}
					<span class="rounded-full bg-warning/10 px-2 py-1 text-xs font-bold text-warning">
						Review
					</span>
				{:else}
					<ChevronRight class="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
				{/if}
			</button>
		</div>

		<!-- Recent Courses -->
		{#if recentLectures.length > 0}
			<section class="space-y-4" in:fly={{ y: 20, duration: 400, delay: 200 }}>
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<BookOpen class="h-5 w-5 text-primary" />
						<h2 class="text-lg font-semibold">Recent Courses</h2>
					</div>
					<Button onclick={() => goto('/lectures')} variant="ghost" size="sm" class="gap-1 text-muted-foreground">
						View All
						<ChevronRight class="h-4 w-4" />
					</Button>
				</div>

				<div class="grid gap-4 md:grid-cols-3">
					{#each recentLectures as lecture}
						<button
							onclick={() => goto(`/lectures/${lecture.id}`)}
							class="group flex flex-col rounded-xl border border-border bg-card p-4 text-left transition-all hover:border-primary/30 hover:shadow-md"
						>
							<div class="mb-3 flex items-center justify-between">
								<span class="text-lg font-semibold transition-colors group-hover:text-primary line-clamp-1">
									{lecture.title}
								</span>
								<span class="text-sm font-bold text-primary">
									{Math.round(lecture.completion_percentage)}%
								</span>
							</div>
							<div class="mt-auto h-1 w-full overflow-hidden rounded-full bg-secondary">
								<div
									class="h-full bg-primary transition-all"
									style="width: {lecture.completion_percentage}%"
								></div>
							</div>
							<p class="mt-2 text-xs text-muted-foreground">
								{formatDate(lecture.last_accessed_at)}
							</p>
						</button>
					{/each}
				</div>
			</section>
		{/if}

		<!-- Recent Decks -->
		{#if recentDecks.length > 0}
			<section class="space-y-4" in:fly={{ y: 20, duration: 400, delay: 300 }}>
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<Layers class="h-5 w-5 text-accent" />
						<h2 class="text-lg font-semibold">Recent Decks</h2>
					</div>
					<Button onclick={() => goto('/decks')} variant="ghost" size="sm" class="gap-1 text-muted-foreground">
						View All
						<ChevronRight class="h-4 w-4" />
					</Button>
				</div>

				<div class="grid gap-4 md:grid-cols-3">
					{#each recentDecks as deck}
						<button
							onclick={() => goto(`/decks/${deck.id}`)}
							class="group flex flex-col rounded-xl border border-border bg-card p-4 text-left transition-all hover:border-primary/30 hover:shadow-md"
						>
							<span class="text-lg font-semibold transition-colors group-hover:text-primary line-clamp-1">
								{deck.title}
							</span>
							<p class="mt-1 line-clamp-2 text-sm text-muted-foreground">
								{deck.description || 'No description'}
							</p>
							<p class="mt-auto pt-3 text-xs text-muted-foreground">
								{formatDate(deck.created_at)}
							</p>
						</button>
					{/each}
				</div>
			</section>
		{/if}

		<!-- Empty State -->
		{#if recentLectures.length === 0 && recentDecks.length === 0}
			<div
				class="flex flex-col items-center justify-center space-y-6 rounded-2xl border border-dashed border-border bg-muted/20 py-16 text-center"
				in:fade
			>
				<div class="rounded-full bg-primary/10 p-4">
					<Sparkles class="h-10 w-10 text-primary" />
				</div>
				<div class="space-y-2">
					<h2 class="text-xl font-semibold">Start Your Learning Journey</h2>
					<p class="text-muted-foreground">
						Create your first course to begin studying with AI-generated content.
					</p>
				</div>
				<Button onclick={() => goto('/lectures')}>
					<Sparkles class="mr-2 h-4 w-4" />
					Create First Course
				</Button>
			</div>
		{/if}
	{/if}
</div>
