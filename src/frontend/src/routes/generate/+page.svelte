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
	let selectedDeckId = $state<string>('new'); // 'new' or deck id as string
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
					class="flex items-center gap-3 text-[10px] font-black tracking-[0.4em] text-indigo-400 uppercase"
				>
					<Sparkles class="h-4 w-4" />
					<span>Synthesis Engine</span>
				</div>
				<h1
					class="font-unbounded text-5xl leading-tight font-black tracking-tighter text-white uppercase md:text-7xl"
				>
					Generate <span
						class="bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 bg-clip-text text-transparent"
						>Flashcards</span
					>
				</h1>
				<p class="max-w-2xl font-sans text-xl leading-relaxed text-muted-foreground italic">
					Transform any topic or concept into high-fidelity study modules. Select your model,
					calibrate the difficulty, and manifest your knowledge.
				</p>
			</div>

			<!-- Decorative Background Glow -->
			<div
				class="absolute -top-24 -left-24 -z-10 h-96 w-96 rounded-full bg-indigo-500/10 blur-[120px]"
			></div>
		</header>

		{#if isLoading}
			<div class="flex flex-col items-center justify-center space-y-8 py-32">
				<div class="relative h-20 w-20">
					<div
						class="absolute inset-0 animate-pulse rounded-full border-4 border-indigo-500/10"
					></div>
					<div
						class="absolute inset-0 animate-spin rounded-full border-t-4 border-indigo-500"
					></div>
					<BrainCircuit class="absolute inset-0 m-auto h-8 w-8 animate-pulse text-indigo-400" />
				</div>
				<p class="font-sans tracking-widest text-muted-foreground uppercase italic">
					Aligning Neural Matrices...
				</p>
			</div>
		{:else}
			<div in:fly={{ y: 40, duration: 800 }}>
				<Card.Root
					class="overflow-hidden rounded-[3rem] border-white/10 bg-slate-950/40 shadow-2xl ring-1 ring-white/10 backdrop-blur-3xl"
				>
					<form onsubmit={handleGenerate}>
						<Card.Content class="space-y-12 p-10 md:p-16">
							{#if error}
								<div
									class="flex items-center gap-4 rounded-2xl border border-red-500/20 bg-red-500/10 p-6 text-sm font-bold text-red-400"
									transition:fade
								>
									<Activity class="h-5 w-5 animate-pulse" />
									{error}
								</div>
							{/if}

							<!-- Topic/Prompt Input -->
							<div class="space-y-6">
								<Label
									class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-slate-500 uppercase"
								>
									<Target class="h-4 w-4 text-indigo-400" /> Topic of Manifestation
								</Label>
								<textarea
									bind:value={prompt}
									required
									placeholder="e.g. 'Photosynthesis in deep-sea organisms' or 'The rise and fall of the Roman Empire'..."
									class="min-h-[200px] w-full resize-none rounded-[2.5rem] border border-white/5 bg-slate-900/40 p-10 font-sans text-2xl text-white italic transition-all outline-none placeholder:text-slate-700 focus:bg-slate-900/60 focus:ring-2 focus:ring-indigo-500"
								></textarea>
							</div>

							<div class="grid grid-cols-1 gap-12 lg:grid-cols-2">
								<!-- Model Selection -->
								<div class="space-y-6">
									<Label
										class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-slate-500 uppercase"
									>
										<Zap class="h-4 w-4 text-cyan-400" /> Intelligence Provider
									</Label>
									<div class="relative">
										<select
											bind:value={selectedProviderId}
											required
											class="h-16 w-full appearance-none rounded-2xl border border-white/5 bg-slate-900/40 px-8 text-lg text-white transition-all outline-none focus:ring-2 focus:ring-indigo-500"
										>
											{#each providers as provider}
												<option value={provider.id} class="bg-slate-950">
													{provider.provider_name} — {provider.model_name}
												</option>
											{/each}
										</select>
										<div class="pointer-events-none absolute top-1/2 right-6 -translate-y-1/2">
											<ChevronRight class="h-5 w-5 rotate-90 text-slate-500" />
										</div>
									</div>
								</div>

								<!-- Target Deck -->
								<div class="space-y-6">
									<Label
										class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-slate-500 uppercase"
									>
										<Layers class="h-4 w-4 text-emerald-400" /> Target Deck
									</Label>
									<div class="relative">
										<select
											bind:value={selectedDeckId}
											class="h-16 w-full appearance-none rounded-2xl border border-white/5 bg-slate-900/40 px-8 text-lg text-white transition-all outline-none focus:ring-2 focus:ring-indigo-500"
										>
											<option value="new" class="bg-slate-950 font-bold text-indigo-400">
												+ Create New Deck
											</option>
											<optgroup label="Existing Decks" class="bg-slate-950">
												{#each decks as deck}
													<option value={deck.id.toString()} class="bg-slate-950">
														{deck.title}
													</option>
												{/each}
											</optgroup>
										</select>
										<div class="pointer-events-none absolute top-1/2 right-6 -translate-y-1/2">
											<ChevronRight class="h-5 w-5 rotate-90 text-slate-500" />
										</div>
									</div>
								</div>

								<!-- Flashcards Count -->
								<div class="space-y-6">
									<Label
										class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-slate-500 uppercase"
									>
										<Infinity class="h-4 w-4 text-amber-400" /> Card Quantity
									</Label>
									<div class="flex items-center gap-6">
										<input
											type="range"
											min="5"
											max="30"
											step="5"
											bind:value={numFlashcards}
											class="h-2 flex-grow cursor-pointer appearance-none rounded-full bg-white/5 accent-indigo-500"
										/>
										<div
											class="font-unbounded min-w-[80px] rounded-xl border border-white/5 bg-white/5 p-4 text-center text-2xl font-black text-white"
										>
											{numFlashcards}
										</div>
									</div>
								</div>

								<!-- Difficulty -->
								<div class="space-y-6">
									<Label
										class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-slate-500 uppercase"
									>
										<Trophy class="h-4 w-4 text-red-400" /> Difficulty Calibration
									</Label>
									<div class="grid grid-cols-3 gap-3">
										{#each ['easy', 'normal', 'hard'] as level}
											<button
												type="button"
												onclick={() => (difficulty = level as any)}
												class="h-16 rounded-2xl border text-[10px] font-black tracking-widest uppercase transition-all
                                                {difficulty === level
													? 'border-indigo-500/50 bg-indigo-500/20 text-white shadow-[0_0_20px_rgba(79,70,229,0.2)]'
													: 'border-white/5 bg-white/5 text-slate-500 hover:bg-white/10 hover:text-slate-300'}"
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
									class="relative h-20 w-full overflow-hidden rounded-[2rem] bg-indigo-600 text-xl font-black tracking-[0.2em] text-white uppercase shadow-[0_20px_50px_rgba(79,70,229,0.4)] transition-all hover:scale-[1.02] hover:bg-indigo-500 active:scale-[0.98]"
								>
									{#if isGenerating}
										<div class="flex items-center gap-4">
											<Loader2 class="h-8 w-8 animate-spin" />
											<span>Synthesizing Nodes...</span>
										</div>
									{:else}
										<div class="flex items-center gap-4">
											<Sparkles class="h-6 w-6" />
											<span>Initialize Synthesis</span>
										</div>
									{/if}
								</Button>
								{#if providers.length === 0}
									<p class="mt-4 text-center text-xs font-bold text-amber-500/60 uppercase">
										No Intelligence Provider setup. <a href="/providers" class="underline"
											>Configure here</a
										>
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
		background: rgba(255, 255, 255, 0.05);
		border-radius: 10px;
	}
</style>
