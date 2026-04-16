<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import { Layers, Plus, Calendar, ChevronRight, Loader2, ChevronDown } from 'lucide-svelte';
	import { goto } from '$app/navigation';

	interface Deck {
		id: number;
		title: string;
		description: string | null;
		created_at: string;
	}

	let decks = $state<Deck[]>([]);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');
	let currentPage = $state(1);
	let totalDecks = $state(0);
	const pageSize = 12;
	let hasMoreDecks = $derived(currentPage * pageSize < totalDecks);

	async function fetchDecks() {
		if (!auth.user) return;
		try {
			const response = await apiFetch(`/decks?user_id=${auth.user.id}&limit=${pageSize}&offset=0`);
			decks = response.items || [];
			totalDecks = response.total || 0;
			currentPage = 1;
		} catch (err: any) {
			error = err.message || 'System error while retrieving decks.';
		} finally {
			isLoading = false;
		}
	}

	async function loadMoreDecks() {
		if (!auth.user || isLoadingMore || !hasMoreDecks) return;

		isLoadingMore = true;
		try {
			const nextPage = currentPage + 1;
			const offset = (nextPage - 1) * pageSize;
			const response = await apiFetch(
				`/decks?user_id=${auth.user.id}&limit=${pageSize}&offset=${offset}`
			);
			decks = [...decks, ...(response.items || [])];
			currentPage = nextPage;
		} catch (err: any) {
			error = err.message || 'Failed to load more decks.';
		} finally {
			isLoadingMore = false;
		}
	}

	onMount(() => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		fetchDecks();
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
				{totalDecks > 0
					? `${decks.length}${totalDecks > decks.length ? `/${totalDecks}` : ''} Decks`
					: 'Study Decks'}
			</p>
			<h1 class="font-display text-4xl font-bold tracking-tight md:text-5xl">
				Study <span class="text-primary">Decks</span>
			</h1>
			<p class="text-muted-foreground">
				Manage your collection of AI-generated study decks and flashcards.
			</p>
		</div>

		<Button onclick={() => goto('/dashboard')} class="gap-2">
			<Plus class="h-4 w-4" />
			Generate New Lecture
		</Button>
	</header>

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
		<div
			class="flex flex-col items-center justify-center space-y-6 rounded-xl border border-destructive/20 bg-destructive/10 py-20 text-center"
		>
			<p class="font-medium text-destructive">{error}</p>
			<Button onclick={fetchDecks} variant="outline" size="sm">Retry</Button>
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
				<h2 class="text-xl font-semibold">No Decks Found</h2>
				<p class="text-sm text-muted-foreground">
					Start by generating a lecture to create your first study deck.
				</p>
			</div>
			<Button onclick={() => goto('/dashboard')}>Create New Deck</Button>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each decks as deck, i}
				<button
					in:fly={{ y: 20, delay: i * 50 }}
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
								<h3 class="text-lg font-semibold transition-colors group-hover:text-primary">
									{deck.title}
								</h3>
								<p class="line-clamp-3 text-sm text-muted-foreground">
									{deck.description || 'No description provided.'}
								</p>
							</div>
						</div>

						<div class="mt-4 flex items-center gap-1 text-xs font-medium text-primary">
							<span>View</span>
							<ChevronRight class="h-4 w-4 transition-transform group-hover:translate-x-1" />
						</div>
					</div>
				</button>
			{/each}
		</div>

		{#if hasMoreDecks && !isLoading}
			<div class="flex justify-center pt-4">
				<Button onclick={loadMoreDecks} disabled={isLoadingMore} variant="outline" class="gap-2">
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
