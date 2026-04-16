<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import {
		Layers,
		Plus,
		BrainCircuit,
		Calendar,
		ChevronRight,
		Loader2,
		ChevronDown
	} from '@lucide/svelte';
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

<div class="min-h-screen bg-transparent px-6 pt-32 pb-20">
	<div class="mx-auto max-w-7xl space-y-16">
		<header class="flex flex-col justify-between gap-8 md:flex-row md:items-end" in:fade>
			<div class="space-y-4">
				<div
					class="flex items-center gap-3 text-[10px] font-black tracking-[0.4em] text-indigo-400 uppercase"
				>
					<Layers class="h-4 w-4" />
					<span
						>{totalDecks > 0
							? `${decks.length}${totalDecks > decks.length ? `/${totalDecks}` : ''} Decks`
							: 'Study Decks'}</span
					>
				</div>
				<h1
					class="font-unbounded text-5xl leading-none font-black tracking-tighter text-foreground uppercase md:text-7xl"
				>
					Study<span class="text-primary">Decks</span>
				</h1>
				<p class="max-w-xl font-sans text-lg text-muted-foreground italic">
					Manage your collection of AI-generated study decks and flashcards.
				</p>
			</div>

			<Button
				onclick={() => goto('/dashboard')}
				class="h-14 rounded-2xl bg-primary px-8 font-black tracking-widest uppercase shadow-[0_0_30px_rgba(79,70,229,0.4)] transition-all hover:-translate-y-1"
			>
				<Plus class="mr-2 h-5 w-5" />
				Generate New Lecture
			</Button>
		</header>

		{#if isLoading}
			<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
				{#each Array(6) as _}
					<div class="h-64 animate-pulse rounded-3xl border border-border bg-muted"></div>
				{/each}
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center space-y-6 py-20 text-center">
				<div class="rounded-full border border-red-500/20 bg-red-500/10 p-6">
					<BrainCircuit class="h-12 w-12 text-red-500" />
				</div>
				<h2 class="font-unbounded text-2xl font-black text-white uppercase italic">{error}</h2>
				<Button onclick={fetchDecks} variant="outline" class="rounded-xl border-white/10"
					>Retry Connection</Button
				>
			</div>
		{:else if decks.length === 0}
			<div
				class="flex flex-col items-center justify-center space-y-10 rounded-[4rem] border border-dashed border-border bg-muted/60 py-32 text-center"
				in:scale
			>
				<div class="relative">
					<div class="absolute inset-0 animate-ping rounded-full bg-primary/20"></div>
					<div class="relative rounded-full border border-primary/20 bg-primary/10 p-8">
						<Layers class="h-16 w-16 text-primary" />
					</div>
				</div>
				<div class="space-y-4">
					<h2 class="font-unbounded text-3xl font-black tracking-tighter text-foreground uppercase">
						No Decks Found
					</h2>
					<p class="mx-auto max-w-md font-sans text-xl text-muted-foreground italic">
						Start by generating a lecture to create your first study deck.
					</p>
				</div>
				<Button
					onclick={() => goto('/dashboard')}
					class="h-16 rounded-2xl bg-indigo-600 px-10 font-black tracking-widest uppercase shadow-2xl"
				>
					Create New Deck
				</Button>
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
				{#each decks as deck, i}
					<button
						in:fly={{ y: 20, delay: i * 50 }}
						class="group relative flex h-full cursor-pointer flex-col overflow-hidden rounded-[2.5rem] border border-border bg-card/40 p-8 text-left backdrop-blur-xl transition-all duration-500 hover:border-primary/30 hover:bg-muted/60 hover:shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
						onclick={() => goto(`/decks/${deck.id}`)}
					>
						<!-- Decorative Glow -->
						<div
							class="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-primary/10 opacity-0 blur-[80px] transition-opacity duration-700 group-hover:opacity-100"
						></div>

						<div class="relative z-10 flex h-full w-full flex-col space-y-6">
							<div class="flex items-center justify-between">
								<div class="rounded-2xl border border-primary/20 bg-primary/10 p-3">
									<Layers class="h-6 w-6 text-primary" />
								</div>
								<div
									class="flex items-center gap-2 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
								>
									<Calendar class="h-3 w-3" />
									{formatDate(deck.created_at)}
								</div>
							</div>

							<div class="flex-grow space-y-2">
								<h3
									class="font-unbounded text-2xl font-black tracking-tighter text-white uppercase transition-colors group-hover:text-primary"
								>
									{deck.title}
								</h3>
								<p class="line-clamp-3 font-sans leading-relaxed text-muted-foreground italic">
									{deck.description || 'No description provided.'}
								</p>
							</div>

							<div class="flex w-full items-center justify-between border-t border-border pt-6">
								<div
									class="flex items-center gap-1 text-[10px] font-black tracking-widest text-primary uppercase transition-transform group-hover:translate-x-1"
								>
									View
									<ChevronRight class="h-4 w-4" />
								</div>
							</div>
						</div>
					</button>
				{/each}
			</div>

			{#if hasMoreDecks && !isLoading}
				<div class="mt-12 flex justify-center">
					<Button
						onclick={loadMoreDecks}
						disabled={isLoadingMore}
						variant="outline"
						class="group flex h-14 items-center gap-3 rounded-2xl border-border px-10 font-black tracking-widest uppercase transition-all hover:bg-primary/5 disabled:opacity-50"
					>
						{#if isLoadingMore}
							<Loader2 class="h-5 w-5 animate-spin" />
							Loading...
						{:else}
							<ChevronDown class="h-5 w-5 transition-transform group-hover:translate-y-1" />
							Load More Decks
						{/if}
					</Button>
				</div>
			{/if}
		{/if}
	</div>
</div>

<style>
	.font-unbounded {
		font-family: var(--font-display);
	}
</style>
