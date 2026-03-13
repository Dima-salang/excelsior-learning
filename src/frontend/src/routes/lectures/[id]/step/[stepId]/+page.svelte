<script lang="ts">
	import { apiFetch, API_BASE_URL } from '$lib/api';
	const API_URL = API_BASE_URL || 'http://localhost:8000';
	import { Button } from '$lib/components/ui/button';
	import { auth } from '$lib/stores/auth.svelte';
	import {
		Loader2,
		BrainCircuit,
		CheckCircle2,
		ChevronLeft,
		ChevronRight,
		ArrowLeft,
		BookOpen,
		Sparkles,
		Clock,
		ExternalLink,
		ListChecks,
		Menu,
		X,
		XCircle,
		Cpu,
		RotateCcw,
		AlertTriangle
	} from '@lucide/svelte';
	import { settings } from '$lib/stores/settings.svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { marked } from 'marked';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import Flashcard from '$lib/components/Flashcard.svelte';

	interface FlashcardData {
		id: number;
		type: string;
		front: string;
		options?: string[];
		options_ans?: number;
		user_selected_ans?: number;
		explanation?: string;
		is_correct?: boolean;
	}

	interface Step {
		id: number;
		title: string;
		order_key: number;
		content?: string;
		is_completed: boolean;
		lecture_section_id: number;
		cards: FlashcardData[];
	}

	interface Section {
		id: number;
		title: string;
		order_key: number;
		steps: Step[];
	}

	interface Lecture {
		id: number;
		title: string;
		sections: Section[];
	}

	interface Provider {
		id: number;
		provider_name: string;
		model_name: string;
	}

	let step = $state<Step | null>(null);
	let lecture = $state<Lecture | null>(null);
	let providers = $state<Provider[]>([]);
	let isLoading = $state(true);
	let isGenerating = $state(false);
	let error = $state('');
	let isSidebarOpen = $state(false);

	let stepId = $derived(page.params.stepId);
	let lectureId = $derived(page.params.id);

	async function fetchData(currentStepId: string | undefined) {
		if (!currentStepId) return;
		try {
			const [stepData, lectureData, providersData] = await Promise.all([
				apiFetch(`/lectures/steps/${currentStepId}`),
				apiFetch(`/lectures/${lectureId}`),
				apiFetch(`/llm/providers?user_id=${auth.user?.id}`)
			]);
			step = stepData;
			lecture = lectureData;
			providers = providersData;

			// Initialize global setting if not set
			if (providers.length > 0 && !settings.selectedProviderId) {
				settings.setProvider(providers[0].id);
			}

			// Auto-generate if content is missing
			if (step && !step.content && !isGenerating && settings.selectedProviderId) {
				handleGenerate();
			}
		} catch (err: any) {
			error = err.message || 'Failed to initialize the learning session.';
		} finally {
			isLoading = false;
		}
	}

	$effect(() => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		if (stepId === 'undefined') {
			if (lectureId) goto(`/lectures/${lectureId}`);
			else goto('/dashboard');
			return;
		}
		if (auth.token && auth.user && stepId) {
			isLoading = true;
			fetchData(stepId);
		}
	});

	async function handleGenerate() {
		if (providers.length === 0) {
			error = 'No AI models configured. Please add one in AI Model settings.';
			return;
		}

		try {
			isGenerating = true;
			const providerId = settings.selectedProviderId || providers[0]?.id;
			if (!providerId) {
				error = 'Please select an AI model provider.';
				return;
			}

			if (stepId === 'undefined') {
				error = 'Invalid step session. Please return to the lecture outline.';
				return;
			}

			const updatedStep = await apiFetch(
				`/lectures/${lectureId}/steps/${stepId}/generate?provider_id=${providerId}`,
				{
					method: 'POST'
				}
			);

			step = updatedStep;
		} catch (err: any) {
			error = err.message || 'The AI failed to generate content. Please try again.';
		} finally {
			isGenerating = false;
		}
	}

	async function toggleComplete() {
		if (!step) return;
		try {
			const updated = await apiFetch(`/lectures/steps/${stepId}/complete`, {
				method: 'POST'
			});
			step.is_completed = updated.is_completed;
			// Refresh lecture progress
			lecture = await apiFetch(`/lectures/${lectureId}`);
		} catch (err) {
			console.error('Failed to update progress:', err);
		}
	}

	async function updateCardMastery(cardId: number, isCorrect: boolean, selectedAns: number) {
		try {
			await apiFetch(`/lectures/cards/${cardId}`, {
				method: 'PATCH',
				body: JSON.stringify({
					user_selected_ans: selectedAns,
					is_correct: isCorrect
				})
			});

			// Update local state
			if (step) {
				const card = step.cards.find((c) => c.id === cardId);
				if (card) {
					card.is_correct = isCorrect;
					card.user_selected_ans = selectedAns;
				}
			}
		} catch (err) {
			console.error('Failed to update card:', err);
		}
	}

	// Navigation Helpers
	let allSteps = $derived(
		[...(lecture?.sections || [])]
			.sort((a, b) => a.order_key - b.order_key)
			.flatMap((s) => [...s.steps].sort((a, b) => a.order_key - b.order_key))
	);

	let currentStepIndex = $derived(allSteps.findIndex((s) => s.id === Number(stepId)));
	let nextStep = $derived(allSteps[currentStepIndex + 1]);
	let prevStep = $derived(allSteps[currentStepIndex - 1]);

	function navigateTo(targetId: number | undefined) {
		if (!targetId || targetId.toString() === 'undefined') {
			console.error('Refusing to navigate to undefined step');
			return;
		}
		if (Number(stepId) === targetId) return;
		isSidebarOpen = false;
		goto(`/lectures/${lectureId}/step/${targetId}`);
	}

	let renderedContent = $derived(step?.content ? marked(step.content) : '');
</script>

<div class="flex h-screen overflow-hidden bg-[#020617] text-slate-100">
	<!-- Adaptive Sidebar -->
	<aside
		class="fixed inset-y-0 left-0 z-50 w-80 transform border-r border-white/5 bg-slate-950 transition-transform duration-500 {isSidebarOpen
			? 'translate-x-0'
			: '-translate-x-full'} shadow-2xl lg:relative lg:translate-x-0"
	>
		<div class="flex flex-col gap-6 border-b border-white/5 p-8">
			<a href="/" class="flex items-center gap-3">
				<div class="rounded-xl bg-indigo-600 p-2">
					<BrainCircuit class="h-5 w-5 text-white" />
				</div>
				<div class="flex flex-col">
					<span class="font-unbounded text-lg font-black tracking-tighter text-white uppercase"
						>EXCELSIOR</span
					>
				</div>
			</a>

			<Button
				variant="outline"
				onclick={() => goto(`/lectures/${lectureId}`)}
				class="flex h-12 w-full items-center justify-center gap-2 rounded-xl border-white/10 text-xs font-black tracking-widest uppercase hover:bg-white/5"
			>
				<ArrowLeft class="h-4 w-4" />
				Lecture Outline
			</Button>

			<!-- Global Model Selector -->
			<div class="space-y-3 border-t border-white/5 pt-4">
				<div
					class="flex items-center gap-2 text-[8px] font-black tracking-widest text-slate-600 uppercase"
				>
					<Cpu class="h-3 w-3 text-indigo-400" />
					Master Model Selection
				</div>
				<div class="relative">
					<select
						bind:value={settings.selectedProviderId}
						onchange={() => settings.setProvider(Number(settings.selectedProviderId))}
						class="h-10 w-full cursor-pointer appearance-none rounded-lg border border-border bg-slate-900 px-3 text-[10px] font-bold text-white shadow-xl transition-all outline-none focus:ring-1 focus:ring-primary"
					>
						{#if providers.length === 0}
							<option value={null} class="bg-slate-900 text-white">No models available</option>
						{/if}
						{#each providers as p}
							<option value={p.id} class="bg-slate-900 text-white"
								>{p.provider_name} — {p.model_name}</option
							>
						{/each}
					</select>
					<ChevronRight
						class="pointer-events-none absolute top-1/2 right-3 h-3 w-3 -translate-y-1/2 rotate-90 text-slate-600"
					/>
				</div>
			</div>
		</div>

		<div class="custom-scrollbar h-[calc(100vh-160px)] overflow-y-auto p-6">
			{#if lecture}
				<div class="space-y-10">
					{#each [...lecture.sections].sort((a, b) => a.order_key - b.order_key) as section}
						<div class="space-y-4">
							<div
								class="flex items-center gap-2 text-[10px] font-black tracking-widest text-slate-500 uppercase"
							>
								<ListChecks class="h-3 w-3 text-indigo-400" />
								{section.title}
							</div>
							<div class="space-y-2">
								{#each [...section.steps].sort((a, b) => a.order_key - b.order_key) as s}
									<button
										onclick={() => navigateTo(s.id)}
										class="w-full rounded-xl border p-3 text-left text-xs font-bold transition-all {s.id ===
										Number(stepId)
											? 'border-indigo-500/30 bg-indigo-600/10 text-white'
											: 'border-transparent text-slate-500 hover:bg-white/5 hover:text-white'} flex items-center gap-3"
									>
										<div
											class="h-1.5 w-1.5 rounded-full {s.id === Number(stepId)
												? 'animate-pulse bg-indigo-400'
												: s.is_completed
													? 'bg-emerald-500'
													: 'bg-slate-800'}"
										></div>
										<span class="truncate">{s.title}</span>
									</button>
								{/each}
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="space-y-10">
					{#each Array(3) as _}
						<div class="space-y-4">
							<Skeleton class="h-3 w-32" />
							<div class="space-y-2">
								<Skeleton class="h-10 w-full rounded-xl" />
								<Skeleton class="h-10 w-full rounded-xl" />
								<Skeleton class="h-10 w-full rounded-xl" />
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</aside>

	<!-- Main Content Canvas -->
	<main class="relative flex flex-grow flex-col overflow-hidden">
		<!-- Mobile Header -->
		<div
			class="flex items-center justify-between border-b border-white/5 bg-slate-950 p-4 lg:hidden"
		>
			<button
				onclick={() => (isSidebarOpen = !isSidebarOpen)}
				class="p-2 text-slate-400 hover:text-white"
			>
				{#if isSidebarOpen}
					<X class="h-6 w-6" />
				{:else}
					<Menu class="h-6 w-6" />
				{/if}
			</button>
			<span
				class="max-w-[200px] truncate text-xs font-black tracking-widest text-indigo-400 uppercase"
				>{step?.title || 'Learning'}</span
			>
			<div class="h-10 w-10"></div>
		</div>

		{#if isLoading}
			<div
				class="flex h-full flex-grow flex-col items-center justify-center space-y-8 bg-slate-950/20 backdrop-blur-xl"
			>
				<div class="relative h-24 w-24">
					<div
						class="absolute inset-0 animate-pulse rounded-full border-4 border-indigo-500/10"
					></div>
					<div
						class="absolute inset-0 animate-spin rounded-full border-t-4 border-indigo-500"
					></div>
					<BookOpen class="absolute inset-0 m-auto h-8 w-8 animate-pulse text-indigo-400" />
				</div>
				<p class="font-serif text-lg text-slate-500 italic">Acquiring learning materials...</p>
			</div>
		{:else if error}
			<div class="flex flex-grow flex-col items-center justify-center space-y-8 p-12 text-center">
				<div class="relative">
					<div class="absolute inset-0 animate-pulse rounded-full bg-red-500/20 blur-3xl"></div>
					<div class="relative rounded-full border border-red-500/20 bg-red-500/10 p-8">
						<AlertTriangle class="h-16 w-16 text-red-500" />
					</div>
				</div>
				<div class="max-w-2xl space-y-4">
					<h2 class="font-unbounded text-3xl font-black tracking-tighter text-white uppercase">
						Neural Signal Lost
					</h2>
					<p class="font-serif text-xl leading-relaxed text-slate-400 italic">{error}</p>
				</div>
				<div class="flex flex-wrap items-center justify-center gap-4">
					<Button
						onclick={() => stepId && fetchData(stepId)}
						variant="outline"
						class="h-14 rounded-2xl border-white/10 px-8 font-black tracking-widest uppercase hover:bg-white/5"
					>
						<RotateCcw class="mr-2 h-4 w-4" />
						Retry Connection
					</Button>
					<Button
						onclick={handleGenerate}
						variant="default"
						class="h-14 rounded-2xl bg-indigo-600 px-10 font-black tracking-widest uppercase shadow-[0_0_30px_rgba(79,70,229,0.4)]"
					>
						<Sparkles class="mr-2 h-4 w-4" />
						Regenerate Content
					</Button>
				</div>
			</div>
		{:else if step}
			<!-- Progress Bar -->
			<div class="absolute top-0 left-0 z-20 h-1 w-full bg-white/5">
				<div
					class="h-full bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 transition-all duration-1000"
					style="width: {((currentStepIndex + 1) / allSteps.length) * 100}%"
				></div>
			</div>

			<div class="custom-scrollbar flex-grow overflow-x-hidden overflow-y-auto">
				<div class="mx-auto max-w-4xl space-y-12 px-6 py-16 lg:py-24">
					<header class="space-y-6" in:fade>
						<div
							class="flex items-center gap-4 text-[10px] font-black tracking-[0.4em] text-indigo-400 uppercase"
						>
							<Sparkles class="h-4 w-4" />
							<span>Step {currentStepIndex + 1} of {allSteps.length}</span>
						</div>
						<h1
							class="font-unbounded text-4xl leading-tight font-black tracking-tighter text-white uppercase md:text-6xl"
						>
							{step.title}
						</h1>

						<div
							class="flex items-center gap-6 border-y border-white/5 py-6 font-serif text-sm text-slate-500 italic"
						>
							<div class="flex items-center gap-2">
								<Clock class="h-4 w-4" />
								<span>Approx. 10 min read</span>
							</div>
						</div>
					</header>

					<article class="prose-excelsior max-w-none" in:fade={{ delay: 200, duration: 800 }}>
						{#if isGenerating}
							<div
								class="flex flex-col items-center justify-center space-y-6 rounded-3xl border border-dashed border-white/10 bg-white/2 p-20"
							>
								<Loader2 class="h-12 w-12 animate-spin text-indigo-500" />
								<div class="space-y-2 text-center">
									<p class="font-unbounded text-xl font-black text-white uppercase">
										AI is crafting your lesson...
									</p>
									<p class="font-sans text-slate-500 italic opacity-60">
										This usually takes about 10-20 seconds.
									</p>
								</div>
							</div>
						{:else if !step}
							<div class="space-y-8 py-10">
								<Skeleton class="h-6 w-full" />
								<Skeleton class="h-6 w-full" />
								<Skeleton class="h-6 w-5/6" />
								<Skeleton class="h-6 w-2/3" />
								<div class="space-y-4 pt-8">
									<Skeleton class="h-6 w-full" />
									<Skeleton class="h-6 w-3/4" />
								</div>
							</div>
						{:else if !step.content}
							<div
								class="space-y-6 rounded-3xl border border-amber-500/10 bg-amber-500/5 p-20 text-center"
							>
								<p class="font-serif text-xl text-amber-400 italic">
									This step is currently empty.
								</p>
								<Button
									onclick={handleGenerate}
									variant="default"
									class="rounded-xl px-8 font-black">Generate Content</Button
								>
							</div>
						{:else}
							{@html renderedContent}

							{#if step.cards && step.cards.length > 0}
								<div class="mt-20 space-y-8" in:fade={{ delay: 600 }}>
									<div class="mb-8 flex items-center gap-4">
										<div class="h-px flex-grow bg-white/5"></div>
										<span class="text-[10px] font-black tracking-[0.4em] text-slate-500 uppercase"
											>Knowledge Checkpoint</span
										>
										<div class="h-px flex-grow bg-white/5"></div>
									</div>
									{#each step.cards as card}
										<Flashcard
											{...card}
											onAnswered={(isCorrect, selectedIdx) =>
												updateCardMastery(card.id, isCorrect, selectedIdx)}
										/>
									{/each}
								</div>
							{/if}

							<!-- Regenerate Action -->
							<div class="mt-16 flex items-center justify-center border-t border-white/5 pt-10">
								<Button
									onclick={handleGenerate}
									variant="ghost"
									class="group flex items-center gap-3 rounded-2xl px-6 py-4 text-[10px] font-black tracking-[0.3em] text-slate-500 uppercase transition-all hover:bg-indigo-500/10 hover:text-indigo-400"
								>
									<RotateCcw class="h-4 w-4 transition-transform group-hover:rotate-[-45deg]" />
									Regenerate Step Content
								</Button>
							</div>
						{/if}
					</article>

					<div
						class="flex flex-col items-center justify-between gap-8 border-t border-white/5 pt-20 md:flex-row"
						in:fade={{ delay: 400 }}
					>
						<Button
							onclick={toggleComplete}
							variant={step.is_completed ? 'outline' : 'default'}
							class="flex h-16 items-center gap-3 rounded-2xl px-10 text-sm font-black tracking-widest uppercase transition-all {step.is_completed
								? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
								: 'shadow-xl hover:-translate-y-1'}"
						>
							{#if step.is_completed}
								<CheckCircle2 class="h-5 w-5" />
								Step Completed
							{:else}
								Mark as Completed
							{/if}
						</Button>

						<div class="flex items-center gap-4">
							{#if prevStep}
								<Button
									variant="ghost"
									onclick={() => navigateTo(prevStep.id)}
									class="flex h-14 items-center gap-2 rounded-xl border border-white/5 px-6 text-slate-500 hover:bg-white/5 hover:text-white"
								>
									<ChevronLeft class="h-4 w-4" />
									Previous
								</Button>
							{/if}

							{#if nextStep}
								<Button
									onclick={() => navigateTo(nextStep.id)}
									variant="default"
									class="flex h-14 items-center gap-2 rounded-xl px-8 font-black tracking-widest uppercase"
								>
									Next Step
									<ChevronRight class="h-4 w-4" />
								</Button>
							{:else}
								<div
									class="flex items-center gap-2 rounded-xl border border-indigo-500/20 bg-indigo-500/10 px-6 py-4 text-xs font-black tracking-widest text-indigo-400 uppercase"
								>
									<Sparkles class="h-4 w-4" />
									Course Complete
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
		{/if}
	</main>
</div>

<style>
	:global(.prose h1, .prose h2, .prose h3) {
		font-family: 'Syne', sans-serif;
		letter-spacing: -0.05em;
		text-transform: uppercase;
		font-weight: 800;
	}

	:global(.prose code) {
		color: #818cf8;
		background: rgba(129, 140, 248, 0.1);
		padding: 0.2rem 0.4rem;
		border-radius: 4px;
	}

	.custom-scrollbar::-webkit-scrollbar {
		width: 4px;
	}
	.custom-scrollbar::-webkit-scrollbar-track {
		background: transparent;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 10px;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb:hover {
		background: rgba(255, 255, 255, 0.1);
	}

	.font-unbounded {
		font-family: var(--font-display);
	}
	.font-sans {
		font-family: var(--font-sans);
	}

	/* Custom Prose Styling for Better Readability */
	:global(.prose-excelsior) {
		--tw-prose-invert-body: #94a3b8;
		--tw-prose-invert-headings: #f8fafc;
		--tw-prose-invert-links: #818cf8;
		--tw-prose-invert-bold: #f8fafc;
		--tw-prose-invert-counters: #6366f1;
		--tw-prose-invert-bullets: #334155;
		--tw-prose-invert-hr: #1e293b;
		--tw-prose-invert-quotes: #e2e8f0;
		--tw-prose-invert-quote-borders: #6366f1;
		--tw-prose-invert-captions: #64748b;
		--tw-prose-invert-code: #818cf8;
		--tw-prose-invert-pre-code: #e2e8f0;
		--tw-prose-invert-pre-bg: #0f172a;
		--tw-prose-invert-th-borders: #334155;
		--tw-prose-invert-td-borders: #1e293b;
	}

	:global(.prose-excelsior h1, .prose-excelsior h2, .prose-excelsior h3) {
		font-family: var(--font-display);
		letter-spacing: -0.05em;
		text-transform: uppercase;
		font-weight: 800;
		margin-top: 2.5em;
		margin-bottom: 1em;
		line-height: 1.1;
	}

	:global(.prose-excelsior p) {
		font-family: var(--font-serif);
		font-size: 1.125rem;
		line-height: 1.8;
		margin-top: 1.5em;
		margin-bottom: 1.5em;
		color: #94a3b8;
	}

	:global(.prose-excelsior strong) {
		color: #f8fafc;
		font-weight: 700;
	}

	:global(.prose-excelsior blockquote) {
		border-left-width: 4px;
		background: rgba(99, 102, 241, 0.05);
		padding: 1.5rem 2rem;
		border-radius: 1rem;
		font-size: 1.1em;
		border-color: #6366f1;
		margin: 2rem 0;
		font-style: italic;
	}

	:global(.prose-excelsior code) {
		background: rgba(129, 140, 248, 0.1);
		padding: 0.25rem 0.5rem;
		border-radius: 0.5rem;
		font-size: 0.9em;
		color: #818cf8;
	}

	:global(.prose-excelsior ul, .prose-excelsior ol) {
		margin-top: 1.5em;
		margin-bottom: 1.5em;
		padding-left: 1.5em;
	}

	:global(.prose-excelsior li) {
		margin-top: 0.75em;
		margin-bottom: 0.75em;
		font-family: var(--font-serif);
		font-size: 1.125rem;
		line-height: 1.7;
	}
</style>
