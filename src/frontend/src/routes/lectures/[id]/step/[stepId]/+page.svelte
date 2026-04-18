<script lang="ts">
	import { apiFetch, API_BASE_URL } from '$lib/api';
	
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
	import { fade, fly, slide, scale } from 'svelte/transition';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import Flashcard from '$lib/components/Flashcard.svelte';
	import MarkdownRenderer from '$lib/components/MarkdownRenderer.svelte';
	import ChatSession from '$lib/components/ChatSession.svelte';
	import { MessageCircle } from '@lucide/svelte';

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
		completed: boolean;
		cards?: FlashcardData[];
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
	let isCompleting = $state(false);
	let isPageReady = $state(false);
	let error = $state('');
	let isSidebarOpen = $state(false);
	let isChatSidebarOpen = $state(false);
	let lectureChatId = $state<number | null>(null);

	let stepId = $derived(page.params.stepId);
	let lectureId = $derived(page.params.id);
	let bottomElement = $state<HTMLElement | null>(null);

	async function fetchData(currentStepId: string | undefined) {
		if (!currentStepId) return;
		try {
			const [stepData, lectureData, providersData] = await Promise.all([
				apiFetch(`/lectures/steps/${currentStepId}`),
				apiFetch(`/lectures/${lectureId}`),
				apiFetch(`/llm/providers?user_id=${auth.user?.id}`)
			]);

			const cardsData = await apiFetch(`/lectures/steps/${currentStepId}/cards`);
			step = { ...stepData, cards: Array.isArray(cardsData) ? cardsData : [] };

			if (lectureData) {
				const sectionsData = await apiFetch(`/lectures/${lectureId}/sections`);
				const sectionsWithSteps = await Promise.all(
					(Array.isArray(sectionsData) ? sectionsData : []).map(async (section: Section) => {
						try {
							const steps = await apiFetch(`/lectures/${lectureId}/sections/${section.id}/steps`);
							return { ...section, steps: Array.isArray(steps) ? steps : [] };
						} catch {
							return { ...section, steps: [] };
						}
					})
				);
				lecture = {
					...lectureData,
					sections: sectionsWithSteps
				};
			}

			providers = providersData || [];

			if (providers.length > 0 && !settings.selectedProviderId) {
				settings.setProvider(providers[0].id);
			}

			if (step && !step.content && !isGenerating && settings.selectedProviderId) {
				handleGenerate();
			}
		} catch (err: any) {
			error = err.message || 'Failed to initialize the learning session.';
		} finally {
			isLoading = false;
			setTimeout(() => {
				isPageReady = true;
			}, 100);
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
				{ method: 'POST' }
			);

			step = updatedStep;
		} catch (err: any) {
			error = err.message || 'The AI failed to generate content. Please try again.';
		} finally {
			isGenerating = false;
		}
	}

	async function toggleComplete() {
		if (!step || isCompleting) return;
		isCompleting = true;
		try {
			const updated = await apiFetch(`/lectures/steps/${stepId}/complete`, {
				method: 'POST'
			});
			step.completed = updated.completed;
		} catch (err) {
			console.error('Failed to update progress:', err);
		} finally {
			isCompleting = false;
		}
	}

	$effect(() => {
		if (!stepId || isLoading || !isPageReady) return;
		
		if (bottomElement && step && !step.completed && !isCompleting) {
			let hasTriggered = false;
			const observer = new IntersectionObserver(
				(entries) => {
					entries.forEach((entry) => {
						if (entry.isIntersecting && !hasTriggered && !isCompleting && !step?.completed) {
							hasTriggered = true;
							toggleComplete();
						}
					});
				},
				{ threshold: 1.0 }
			);
			observer.observe(bottomElement);
			return () => {
				hasTriggered = true;
				observer.disconnect();
			};
		}
	});

	async function updateCardMastery(cardId: number, isCorrect: boolean, selectedAns: number) {
		try {
			await apiFetch(`/lectures/cards/${cardId}`, {
				method: 'PATCH',
				body: JSON.stringify({
					user_selected_ans: selectedAns,
					is_correct: isCorrect
				})
			});

			if (step && step.cards) {
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

	function getAllSteps() {
		if (!lecture || !lecture.sections || !Array.isArray(lecture.sections)) {
			return [];
		}
		try {
			return [...lecture.sections]
				.sort((a, b) => a.order_key - b.order_key)
				.flatMap((s) => [...(s.steps || [])].sort((a, b) => a.order_key - b.order_key));
		} catch {
			return [];
		}
	}

	let allSteps = $derived(getAllSteps());

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
</script>

<div class="flex h-screen overflow-hidden bg-background text-foreground">
	<!-- Adaptive Sidebar -->
	<aside class="fixed inset-y-0 left-0 z-50 w-80 transform border-r border-border bg-card transition-transform duration-500 {isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} shadow-2xl lg:relative lg:translate-x-0">
		<div class="flex flex-col gap-6 border-b border-border p-8">
			<a href="/" class="flex items-center gap-3">
				<div class="rounded-xl bg-primary p-2">
					<BrainCircuit class="h-5 w-5 text-primary-foreground" />
				</div>
				<div class="flex flex-col">
					<span class="font-unbounded text-lg font-black tracking-tighter uppercase text-foreground">EXCELSIOR</span>
				</div>
			</a>

			<Button
				variant="outline"
				onclick={() => goto(`/lectures/${lectureId}`)}
				class="flex h-12 w-full items-center justify-center gap-2 rounded-xl font-black tracking-widest uppercase"
			>
				<ArrowLeft class="h-4 w-4" />
				Lecture Outline
			</Button>

			<div class="space-y-3 border-t border-border pt-4">
				<div class="flex items-center gap-2 text-[8px] font-black tracking-widest text-muted-foreground uppercase">
					<Cpu class="h-3 w-3 text-primary" />
					Master Model Selection
				</div>
				<div class="relative">
					<select
						bind:value={settings.selectedProviderId}
						onchange={() => settings.setProvider(Number(settings.selectedProviderId))}
						class="h-10 w-full cursor-pointer appearance-none rounded-lg border border-border bg-secondary px-3 text-[10px] font-bold shadow-xl transition-all outline-none focus:ring-1 focus:ring-primary text-foreground"
					>
						{#if providers.length === 0}
							<option value={null} class="bg-card">No models available</option>
						{/if}
						{#each providers as p}
							<option value={p.id} class="bg-card">{p.provider_name} — {p.model_name}</option>
						{/each}
					</select>
					<ChevronRight class="pointer-events-none absolute top-1/2 right-3 h-3 w-3 -translate-y-1/2 rotate-90 text-muted-foreground" />
				</div>
			</div>
		</div>

		<div class="custom-scrollbar flex-1 overflow-y-auto overflow-x-hidden p-6 pb-20">
			{#if lecture && lecture.sections}
				<div class="space-y-10">
					{#each [...lecture.sections].sort((a, b) => a.order_key - b.order_key) as section}
						<div class="space-y-4">
							<div class="flex items-center gap-2 text-[10px] font-black tracking-widest text-muted-foreground uppercase">
								<ListChecks class="h-3 w-3 text-primary" />
								{section.title}
							</div>
							<div class="space-y-2">
								{#each [...(section.steps || [])].sort((a, b) => a.order_key - b.order_key) as s}
									<button
										onclick={() => navigateTo(s.id)}
										class="w-full rounded-xl border p-3 text-left text-xs font-bold transition-all flex items-center gap-3 {s.id === Number(stepId)
											? 'border-primary/30 bg-primary/10 text-foreground'
											: 'border-transparent text-muted-foreground hover:bg-muted hover:text-foreground'}"
									>
										<div class="h-1.5 w-1.5 rounded-full {s.id === Number(stepId) ? 'animate-pulse bg-primary' : s.completed ? 'bg-success' : 'bg-muted'}"></div>
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
		<div class="flex items-center justify-between border-b border-border bg-card p-4 lg:hidden">
			<button onclick={() => (isSidebarOpen = !isSidebarOpen)} class="p-2 text-muted-foreground hover:text-foreground">
				{#if isSidebarOpen}
					<X class="h-6 w-6" />
				{:else}
					<Menu class="h-6 w-6" />
				{/if}
			</button>
			<span class="max-w-[200px] truncate text-xs font-black tracking-widest text-primary uppercase">{step?.title || 'Learning'}</span>
			<div class="h-10 w-10"></div>
		</div>

		{#if isLoading}
			<div class="flex h-full flex-grow flex-col items-center justify-center space-y-8 bg-background/20 backdrop-blur-xl">
				<div class="relative h-24 w-24">
					<div class="absolute inset-0 animate-pulse rounded-full border-4 border-primary/10"></div>
					<div class="absolute inset-0 animate-spin rounded-full border-t-4 border-primary"></div>
					<BookOpen class="absolute inset-0 m-auto h-8 w-8 animate-pulse text-primary" />
				</div>
				<p class="font-sans text-lg text-muted-foreground">Preparing your study materials...</p>
			</div>
		{:else if error}
			<div class="flex flex-grow flex-col items-center justify-center space-y-8 p-12 text-center">
				<div class="relative">
					<div class="absolute inset-0 animate-pulse rounded-full bg-destructive/20 blur-3xl"></div>
					<div class="relative rounded-full border border-destructive/20 bg-destructive/10 p-8">
						<AlertTriangle class="h-16 w-16 text-destructive" />
					</div>
				</div>
				<div class="max-w-2xl space-y-4">
					<h2 class="font-unbounded text-3xl font-black tracking-tighter uppercase">Connection Lost</h2>
					<p class="font-sans text-xl leading-relaxed text-muted-foreground">{error}</p>
				</div>
				<div class="flex flex-wrap items-center justify-center gap-4">
					<Button onclick={() => stepId && fetchData(stepId)} variant="outline" class="h-14 rounded-2xl px-8 font-black tracking-widest uppercase">
						<RotateCcw class="mr-2 h-4 w-4" />
						Retry Connection
					</Button>
					<Button onclick={handleGenerate} variant="default" class="h-14 rounded-2xl px-10 font-black tracking-widest uppercase">
						<Sparkles class="mr-2 h-4 w-4" />
						Regenerate Content
					</Button>
				</div>
			</div>
		{:else if step}
			<!-- Progress Bar -->
			<div class="absolute top-0 left-0 z-20 h-1 w-full bg-muted">
				<div class="h-full bg-primary transition-all duration-1000" style="width: {((currentStepIndex + 1) / allSteps.length) * 100}%"></div>
			</div>

			<div class="custom-scrollbar flex-grow overflow-x-hidden overflow-y-auto">
				<div class="mx-auto max-w-4xl space-y-12 px-6 py-16 lg:py-24">
					<header class="space-y-6" in:fade>
						<div class="flex items-center gap-4 text-[10px] font-black tracking-[0.4em] text-primary uppercase">
							<Sparkles class="h-4 w-4" />
							<span>Step {currentStepIndex + 1} of {allSteps.length}</span>
						</div>
						<h1 class="font-unbounded text-4xl leading-tight font-black tracking-tighter uppercase md:text-6xl text-foreground">
							{step.title}
						</h1>

						<div class="flex items-center gap-6 border-y border-border py-6 font-sans text-sm text-muted-foreground">
							<div class="flex items-center gap-2">
								<Clock class="h-4 w-4" />
								<span>Approx. 10 min read</span>
							</div>
						</div>
					</header>

					<article class="prose-excelsior max-w-none" in:fade={{ delay: 200, duration: 800 }}>
						{#if isGenerating}
							<div class="flex flex-col items-center justify-center space-y-6 rounded-3xl border border-dashed border-border bg-muted/20 p-20">
								<Loader2 class="h-12 w-12 animate-spin text-primary" />
								<div class="space-y-2 text-center">
									<p class="font-unbounded text-xl font-black uppercase">AI is crafting your lesson...</p>
									<p class="font-sans text-muted-foreground opacity-60">This usually takes about 10-20 seconds.</p>
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
							<div class="space-y-6 rounded-3xl border border-warning/10 bg-warning/5 p-20 text-center">
								<p class="font-sans text-xl text-warning">This step is currently empty.</p>
								<Button onclick={handleGenerate} variant="default" class="rounded-xl px-8 font-black">Generate Content</Button>
							</div>
						{:else}
							<MarkdownRenderer content={step.content || ''} />

							{#if step.cards && step.cards.length > 0}
								<div class="mt-20 space-y-8" in:fade={{ delay: 600 }}>
									<div class="mb-8 flex items-center gap-4">
										<div class="h-px flex-grow bg-border"></div>
										<span class="text-[10px] font-black tracking-[0.4em] text-muted-foreground uppercase">Unit Review</span>
										<div class="h-px flex-grow bg-border"></div>
									</div>
									{#each step.cards as card}
										<Flashcard
											{...card}
											onAnswered={(isCorrect, selectedIdx) => updateCardMastery(card.id, isCorrect, selectedIdx)}
										/>
									{/each}
								</div>
							{/if}

							<div class="mt-16 flex items-center justify-center border-t border-border pt-10">
								<Button
									onclick={handleGenerate}
									variant="ghost"
									class="group flex items-center gap-3 rounded-2xl px-6 py-4 text-[10px] font-black tracking-[0.3em] text-muted-foreground uppercase transition-all hover:bg-primary/10 hover:text-primary"
								>
									<RotateCcw class="h-4 w-4 transition-transform group-hover:rotate-[-45deg]" />
									Regenerate Step Content
								</Button>
							</div>
						{/if}
					</article>

					<div class="flex flex-col items-center justify-between gap-8 border-t border-border pt-20 md:flex-row" in:fade={{ delay: 400 }}>
						<Button
							onclick={toggleComplete}
							disabled={isCompleting}
							variant={step.completed ? 'outline' : 'default'}
							class="flex h-16 items-center gap-3 rounded-2xl px-10 text-sm font-black tracking-widest uppercase transition-all {step.completed ? 'border-success/30 bg-success/10 text-success' : 'shadow-xl hover:-translate-y-1'}"
						>
							{#if isCompleting}
								<Loader2 class="h-5 w-5 animate-spin" />
								Completing...
							{:else if step.completed}
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
									disabled={isCompleting || isGenerating}
									class="flex h-14 items-center gap-2 rounded-xl border border-border px-6 text-muted-foreground hover:bg-muted hover:text-foreground disabled:opacity-50"
								>
									<ChevronLeft class="h-4 w-4" />
									Previous
								</Button>
							{/if}

							{#if nextStep}
								<Button onclick={() => navigateTo(nextStep.id)} disabled={isCompleting || isGenerating} variant="default" class="flex h-14 items-center gap-2 rounded-xl px-8 font-black tracking-widest uppercase disabled:opacity-50">
									Next Step
									<ChevronRight class="h-4 w-4" />
								</Button>
							{:else}
								<div class="flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/10 px-6 py-4 text-xs font-black tracking-widest text-primary uppercase">
									<Sparkles class="h-4 w-4" />
									Course Complete
								</div>
							{/if}
						</div>
					</div>
					<div bind:this={bottomElement} class="h-4"></div>
				</div>
			</div>
		{/if}
	</main>

	<!-- AI Chat Sidebar Toggle Button -->
	{#if !isChatSidebarOpen}
		<button
			onclick={() => (isChatSidebarOpen = true)}
			class="fixed right-6 bottom-6 z-40 flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition-all hover:-translate-y-1 hover:shadow-xl md:right-10 md:bottom-10"
			in:scale={{ duration: 400 }}
		>
			<MessageCircle class="h-6 w-6" />
		</button>
	{/if}

	<!-- AI Chat Right Sidebar -->
	<aside class="fixed inset-y-0 right-0 z-50 flex w-80 transform flex-col border-l border-border bg-card shadow-2xl transition-transform duration-500 lg:w-96 {isChatSidebarOpen ? 'translate-x-0' : 'translate-x-full'}">
		<div class="flex items-center justify-between border-b border-border bg-card/60 p-4 backdrop-blur-2xl">
			<div class="flex items-center gap-3">
				<div class="rounded-xl border border-primary/20 bg-primary/10 p-2">
					<BrainCircuit class="h-4 w-4 text-primary" />
				</div>
				<span class="font-display text-xs font-black tracking-widest uppercase text-foreground">AI Assistant</span>
			</div>
			<button onclick={() => (isChatSidebarOpen = false)} class="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
				<X class="h-5 w-5" />
			</button>
		</div>

		{#if step && providers.length > 0}
			<ChatSession
				bind:chatId={lectureChatId}
				lectureId={Number(lectureId)}
				lectureContext={step.content}
				{providers}
			/>
		{:else if providers.length === 0}
			<div class="flex flex-1 items-center justify-center p-6 text-center text-sm font-bold text-muted-foreground">
				No AI models configured. Please add one in AI settings to chat.
			</div>
		{:else}
			<div class="flex flex-1 items-center justify-center">
				<Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
			</div>
		{/if}
	</aside>
</div>

<style>
	:global(.prose h1, .prose h2, .prose h3) {
		font-family: var(--font-display);
		letter-spacing: -0.05em;
		text-transform: uppercase;
		font-weight: 800;
	}

	.custom-scrollbar::-webkit-scrollbar {
		width: 4px;
	}
	.custom-scrollbar::-webkit-scrollbar-track {
		background: transparent;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: var(--border);
		border-radius: 10px;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb:hover {
		background: var(--muted);
	}

.font-unbounded {
		font-family: var(--font-display);
	}
	.font-sans {
		font-family: var(--font-sans);
	}
 </style>
