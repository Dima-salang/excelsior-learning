<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import FilterBar from '$lib/components/FilterBar.svelte';
	import { Layers, Plus, Calendar, ChevronRight, Loader2, BookOpen, Clock } from '@lucide/svelte';
	import { goto } from '$app/navigation';

	interface Deck {
		id: number;
		title: string;
		description: string | null;
		created_at: string;
		due_count?: number;
	}

	let decks = $state<Deck[]>([]);
	let dueCounts = $state<Record<number, number>>({});
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');
	let currentPage = $state(1);
	let totalDecks = $state(0);
	const pageSize = 12;

	// Filter state
	let searchQuery = $state('');
	let sortBy = $state('descending');
	let searchTimeout: number;

	let hasMoreDecks = $derived(currentPage * pageSize < totalDecks);

	async function fetchDecks(append = false) {
		if (!auth.user) return;

		const params = new URLSearchParams({
			user_id: auth.user.id.toString(),
			limit: pageSize.toString(),
			offset: append ? ((currentPage) * pageSize).toString() : '0'
		});

		// Add search filter
		if (searchQuery.trim()) {
			params.set('search', searchQuery.trim());
		}

		// Add sort
		if (sortBy === 'ascending') {
			params.set('sort', 'ascending');
		}

		try {
			if (!append) {
				isLoading = true;
				currentPage = 1;
			}
			const response = await apiFetch(`/decks?${params.toString()}`);

			if (append) {
				decks = [...decks, ...(response.items || [])];
				currentPage++;
			} else {
				decks = response.items || [];
				totalDecks = response.total || 0;
			}
		} catch (err: any) {
			error = err.message || 'Failed to retrieve decks.';
		} finally {
			isLoading = false;
			isLoadingMore = false;
		}
	}

	async function fetchDueCounts() {
		if (!auth.user) return;
		try {
			const stats = await apiFetch(`/decks/stats/by-deck?user_id=${auth.user.id}`);
			const counts: Record<number, number> = {};
			for (const item of stats || []) {
				counts[item.deck_id] = item.due_count;
			}
			dueCounts = counts;
		} catch (err) {
			console.error('Failed to fetch due counts', err);
		}
	}

	function handleSearchChange(value: string) {
		clearTimeout(searchTimeout);
		searchTimeout = window.setTimeout(() => {
			fetchDecks();
		}, 300);
	}

	function handleSortChange(value: string) {
		sortBy = value;
		fetchDecks();
	}

	function handleClearFilters() {
		searchQuery = '';
		sortBy = 'descending';
		fetchDecks();
	}

	async function loadMoreDecks() {
		if (isLoadingMore || !hasMoreDecks) return;
		isLoadingMore = true;
		await fetchDecks(true);
	}

	onMount(() => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		fetchDecks();
		fetchDueCounts();
	});

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>Decks — Excelsior</title>
</svelte:head>

<div class="container mx-auto max-w-7xl space-y-8 p-6 py-12 lg:p-12">
	<header class="flex flex-col justify-between gap-6 md:flex-row md:items-end" in:fade>
		<div class="space-y-2">
			<p class="text-xs font-medium tracking-wide text-primary uppercase">
				{#if totalDecks > 0}
					{decks.length}{totalDecks > decks.length ? `/${totalDecks}` : ''} Decks
				{:else}
					Study Decks
				{/if}
			</p>
			<h1 class="font-display text-4xl font-bold tracking-tight md:text-5xl">
				Your <span class="text-primary">Decks</span>
			</h1>
			<p class="text-muted-foreground">
				Flashcard decks generated from your courses.
			</p>
		</div>

		<Button onclick={() => goto('/lectures')} class="gap-2">
			<BookOpen class="h-4 w-4" />
			View Courses
		</Button>
	</header>

	<!-- Filter Bar -->
	<FilterBar
		bind:searchValue={searchQuery}
		searchPlaceholder="Search decks..."
		onSearchChange={handleSearchChange}
		sortOptions={[
			{ value: 'descending', label: 'Newest First' },
			{ value: 'ascending', label: 'Oldest First' }
		]}
		bind:sortValue={sortBy}
		onSortChange={handleSortChange}
		onClear={handleClearFilters}
	/>

	{#if isLoading}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each Array(6) as _}
				<div class="h-64 rounded-xl border border-border bg-muted/50 p-6">
					<div class="flex h-full flex-col justify-between">
						<div class="space-y-4">
							<Skeleton class="h-12 w-12 rounded-lg" />
							<div class="space-y-2">
								<Skeleton class="h-6 w-3/4" />
								<Skeleton class="h-4 w-full" />
								<Skeleton class="h-4 w-2/3" />
							</div>
						</div>
						<Skeleton class="h-4 w-20" />
					</div>
				</div>
			{/each}
		</div>
	{:else if error}
		<div class="flex flex-col items-center justify-center space-y-6 rounded-xl border border-destructive/20 bg-destructive/10 py-20 text-center">
			<p class="font-medium text-destructive">{error}</p>
			<Button onclick={() => fetchDecks()} variant="outline" size="sm">Retry</Button>
		</div>
	{:else if decks.length === 0}
		<div
			class="flex flex-col items-center justify-center space-y-6 rounded-2xl border border-dashed border-border bg-muted/30 py-20 text-center"
			in:scale
		>
			<div class="rounded-full bg-primary/10 p-4">
				<Layers class="h-10 w-10 text-primary" />
			</div>
			<div class="space-y-2">
				{#if searchQuery || sortBy !== 'descending'}
					<h2 class="text-xl font-semibold">No decks match your filters</h2>
					<p class="text-sm text-muted-foreground">
						Try adjusting your search or filter criteria.
					</p>
					<Button onclick={handleClearFilters} variant="outline" size="sm">Clear Filters</Button>
				{:else}
					<h2 class="text-xl font-semibold">No Decks Found</h2>
					<p class="text-sm text-muted-foreground">
						Decks are created when you generate a course.
					</p>
					<Button onclick={() => goto('/lectures')}>Generate a Course</Button>
				{/if}
			</div>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each decks as deck, i (deck.id)}
				{@const dueCount = dueCounts[deck.id] || 0}
				<div
					class="group flex h-full cursor-pointer flex-col rounded-xl border border-border bg-card p-6 text-left transition-all hover:border-primary/30 hover:shadow-md"
					onclick={() => goto(`/decks/${deck.id}`)}
				>
					<div class="flex h-full flex-col justify-between">
						<div class="space-y-4">
							<div class="flex items-center justify-between">
								<div class="rounded-lg bg-primary/10 p-2">
									<Layers class="h-5 w-5 text-primary" />
								</div>
								<span class="flex items-center gap-1 text-xs text-muted-foreground">
									<Calendar class="h-3 w-3" />
									{formatDate(deck.created_at)}
								</span>
							</div>

							<div class="space-y-2">
								<h3 class="text-lg font-semibold transition-colors group-hover:text-primary line-clamp-1">
									{deck.title}
								</h3>
								<p class="line-clamp-3 text-sm text-muted-foreground">
									{deck.description || 'No description provided.'}
								</p>
							</div>
						</div>

						<div class="mt-4 flex items-center justify-between">
							{#if dueCount > 0}
								<button
									onclick={(e) => { e.stopPropagation(); goto(`/quiz/${deck.id}`); }}
									class="flex items-center gap-2 rounded-lg bg-warning/10 px-3 py-2 text-xs font-bold text-warning transition-all hover:bg-warning/20"
								>
									<Clock class="h-3.5 w-3.5" />
									<span>{dueCount} Due</span>
								</button>
							{:else}
								<button
									onclick={(e) => e.stopPropagation()}
									class="flex items-center gap-1 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
								>
									<span>View Cards</span>
								</button>
							{/if}
							<ChevronRight class="h-4 w-4 text-primary transition-transform group-hover:translate-x-1" />
						</div>
					</div>
				</div>
			{/each}
		</div>

		{#if hasMoreDecks && !isLoading}
			<div class="flex justify-center pt-4">
				<Button onclick={loadMoreDecks} disabled={isLoadingMore} variant="outline" class="gap-2">
					{#if isLoadingMore}
						<Loader2 class="h-4 w-4 animate-spin" />
						Loading...
					{:else}
						<ChevronRight class="h-4 w-4" />
						Load More
					{/if}
				</Button>
			</div>
		{/if}
	{/if}
</div>
