<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import {
		Sparkles,
		Plus,
		BrainCircuit,
		Loader2,
		ChevronRight,
		Calendar,
		Clock,
		Target,
		Zap,
		BookOpen,
		LayoutDashboard,
		ArrowRight,
		Layers,
		Trophy,
		Activity,
		Settings2,
		Infinity
	} from '@lucide/svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface Deck {
		id: number;
		title: string;
		description: string | null;
	}

	interface Provider {
		id: number;
		provider_name: string;
		model_name: string;
	}

	let decks = $state<Deck[]>([]);
	let providers = $state<Provider[]>([]);
	let isLoading = $state(true);
	let isGenerating = $state(false);

	// Form State
	let prompt = $state('');
	let selectedProviderId = $state<number | null>(null);
	let selectedDeckId = $state<string>('new');
	let numFlashcards = $state(10);
	let difficulty = $state<'easy' | 'normal' | 'hard'>('normal');
	let error = $state('');

	onMount(async () => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		await fetchData();
	});

	async function fetchData() {
		if (!auth.user) return;
		try {
			const [decksData, providersData] = await Promise.all([
				apiFetch(`/decks?user_id=${auth.user.id}`),
				apiFetch(`/llm/providers?user_id=${auth.user.id}`)
			]);
			decks = decksData;
			providers = providersData;

			if (providers.length > 0) {
				selectedProviderId = providers[0].id;
			}
		} catch (err: any) {
			error = err.message || 'Failed to initialize generation matrix.';
		} finally {
			isLoading = false;
		}
	}

	async function handleGenerate(e: SubmitEvent) {
		e.preventDefault();
		if (!auth.user || !selectedProviderId) return;

		isGenerating = true;
		error = '';

		try {
			const body = {
				prompt,
				provider_id: selectedProviderId,
				user_id: auth.user.id,
				num_flashcards: numFlashcards,
				difficulty
			};

			let result;
			if (selectedDeckId === 'new') {
				result = await apiFetch('/llm/generate/cards', {
					method: 'POST',
					body: JSON.stringify(body)
				});
				goto(`/decks/${result}`);
			} else {
				result = await apiFetch(`/llm/generate/${selectedDeckId}/cards`, {
					method: 'POST',
					body: JSON.stringify(body)
				});
				goto(`/decks/${result}`);
			}
		} catch (err: any) {
			error = err.message || 'The neural matrix failed to stabilize. Please try again.';
		} finally {
			isGenerating = false;
		}
	}
</script>

<svelte:head>
	<title>Generate Flashcards — Excelsior</title>
</svelte:head>

<div class="min-h-screen bg-transparent px-6 pt-32 pb-20">
	<div class="mx-auto max-w-5xl space-y-12">
		<!-- Header Section -->
		<header class="relative space-y-6" in:fade={{ duration: 1000 }}>
			<div class="space-y-4">
				<div
					class="flex items-center gap-3 text-[10px] font-black tracking-[0.4em] text-primary uppercase"
				>
					<Sparkles class="h-4 w-4" />
					<span>Flashcard Generator</span>
				</div>
				<h1
					class="font-unbounded text-5xl leading-tight font-black tracking-tighter uppercase md:text-7xl text-foreground"
				>
					Generate <span class="text-primary">Flashcards</span>
				</h1>
				<p class="max-w-2xl font-sans text-xl leading-relaxed text-muted-foreground">
					Create study flashcards from any topic. Select your AI model, choose difficulty, and
					generate cards to test your knowledge.
				</p>
			</div>
		</header>

		{#if isLoading}
			<div class="flex flex-col items-center justify-center space-y-8 py-32">
				<div class="relative h-20 w-20">
					<div class="absolute inset-0 animate-pulse rounded-full border-4 border-primary/10"></div>
					<div class="absolute inset-0 animate-spin rounded-full border-t-4 border-primary"></div>
					<BrainCircuit class="absolute inset-0 m-auto h-8 w-8 animate-pulse text-primary" />
				</div>
				<p class="font-sans tracking-widest text-muted-foreground uppercase">
					Preparing generator...
				</p>
			</div>
		{:else}
			<div in:fly={{ y: 40, duration: 800 }}>
				<Card.Root class="overflow-hidden rounded-[3rem] border-border bg-card/40 shadow-2xl backdrop-blur-3xl">
					<form onsubmit={handleGenerate}>
						<Card.Content class="space-y-12 p-10 md:p-16">
							{#if error}
								<div
									class="flex items-center gap-4 rounded-2xl border border-destructive/20 bg-destructive/10 p-6 text-sm font-bold text-destructive"
									transition:fade
								>
									<Activity class="h-5 w-5 animate-pulse" />
									{error}
								</div>
							{/if}

							<!-- Topic/Prompt Input -->
							<div class="space-y-6">
								<Label class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-muted-foreground uppercase">
									<Target class="h-4 w-4 text-primary" /> Topic
								</Label>
								<textarea
									bind:value={prompt}
									required
									placeholder="e.g. 'Photosynthesis' or 'World War II timeline'..."
									class="min-h-[200px] w-full resize-none rounded-[2.5rem] border border-border bg-input px-10 py-8 font-sans text-2xl transition-all outline-none placeholder:text-muted-foreground/50 focus:bg-input focus:ring-2 focus:ring-primary"
								></textarea>
							</div>

							<div class="grid grid-cols-1 gap-12 lg:grid-cols-2">
								<!-- Model Selection -->
								<div class="space-y-6">
									<Label class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-muted-foreground uppercase">
										<Zap class="h-4 w-4 text-info" /> AI Model
									</Label>
									<div class="relative">
										<select
											bind:value={selectedProviderId}
											required
											class="h-16 w-full appearance-none rounded-2xl border border-border bg-input px-8 text-lg outline-none focus:ring-2 focus:ring-primary text-foreground"
										>
											{#each providers as provider}
												<option value={provider.id} class="bg-card">
													{provider.provider_name} — {provider.model_name}
												</option>
											{/each}
										</select>
										<div class="pointer-events-none absolute top-1/2 right-6 -translate-y-1/2">
											<ChevronRight class="h-5 w-5 rotate-90 text-muted-foreground" />
										</div>
									</div>
								</div>

								<!-- Target Deck -->
								<div class="space-y-6">
									<Label class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-muted-foreground uppercase">
										<Layers class="h-4 w-4 text-success" /> Target Deck
									</Label>
									<div class="relative">
										<select
											bind:value={selectedDeckId}
											class="h-16 w-full appearance-none rounded-2xl border border-border bg-input px-8 text-lg outline-none focus:ring-2 focus:ring-primary text-foreground"
										>
											<option value="new" class="bg-card font-bold text-primary">
												+ Create New Deck
											</option>
											<optgroup label="Existing Decks" class="bg-card">
												{#each decks as deck}
													<option value={deck.id.toString()} class="bg-card">
														{deck.title}
													</option>
												{/each}
											</optgroup>
										</select>
										<div class="pointer-events-none absolute top-1/2 right-6 -translate-y-1/2">
											<ChevronRight class="h-5 w-5 rotate-90 text-muted-foreground" />
										</div>
									</div>
								</div>

								<!-- Flashcards Count -->
								<div class="space-y-6">
									<Label class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-muted-foreground uppercase">
										<Infinity class="h-4 w-4 text-warning" /> Number of Cards
									</Label>
									<div class="flex items-center gap-6">
										<input
											type="range"
											min="5"
											max="30"
											step="5"
											bind:value={numFlashcards}
											class="h-2 flex-grow cursor-pointer appearance-none rounded-full bg-muted accent-primary"
										/>
										<div class="font-unbounded min-w-[80px] rounded-xl border border-border bg-muted p-4 text-center text-2xl font-black text-foreground">
											{numFlashcards}
										</div>
									</div>
								</div>

								<!-- Difficulty -->
								<div class="space-y-6">
									<Label class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-muted-foreground uppercase">
										<Trophy class="h-4 w-4 text-destructive" /> Difficulty
									</Label>
									<div class="grid grid-cols-3 gap-3">
										{#each ['easy', 'normal', 'hard'] as level}
											<button
												type="button"
												onclick={() => (difficulty = level as any)}
												class="h-16 rounded-2xl border text-[10px] font-black tracking-widest uppercase transition-all
                                                {difficulty === level
													? 'border-primary/50 bg-primary/20 text-foreground shadow-[0_0_20px_rgba(var(--color-primary),0.2)]'
													: 'border-border bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground'}"
											>
												{level}
											</button>
										{/each}
									</div>
								</div>
							</div>

							<div class="pt-8">
								<Button
									type="submit"
									disabled={isGenerating || providers.length === 0}
									class="relative h-20 w-full overflow-hidden rounded-[2rem] text-xl font-black tracking-[0.2em] uppercase transition-all hover:scale-[1.02] active:scale-[0.98]"
								>
									{#if isGenerating}
										<div class="flex items-center gap-4">
											<Loader2 class="h-8 w-8 animate-spin" />
											<span>Creating Flashcards...</span>
										</div>
									{:else}
										<div class="flex items-center gap-4">
											<Sparkles class="h-6 w-6" />
											<span>Generate Flashcards</span>
										</div>
									{/if}
								</Button>
								{#if providers.length === 0}
									<p class="mt-4 text-center text-xs font-bold text-warning uppercase">
										No Intelligence Provider setup. <a href="/providers" class="underline">Configure here</a>
									</p>
								{/if}
							</div>
						</Card.Content>
					</form>
				</Card.Root>
			</div>
		{/if}
	</div>
</div>

<style>
	.font-unbounded {
		font-family: var(--font-display);
	}

	textarea::-webkit-scrollbar {
		width: 4px;
	}
	textarea::-webkit-scrollbar-track {
		background: transparent;
	}
	textarea::-webkit-scrollbar-thumb {
		background: var(--border);
		border-radius: 10px;
	}
</style>
