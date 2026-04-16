<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
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
		BookOpen,
		ArrowRight
	} from 'lucide-svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	interface Lecture {
		id: number;
		title: string;
		description?: string;
		completion_percentage: number;
		created_at: string;
		last_accessed_at: string;
	}

	interface Provider {
		id: number;
		provider_name: string;
		model_name: string;
	}

	let lectures = $state<Lecture[]>([]);
	let providers = $state<Provider[]>([]);
	let isLoading = $state(true);
	let isGenerating = $state(false);
	let showGenerator = $state(false);

	let prompt = $state('');
	let selectedProviderId = $state<number | null>(null);
	let generationError = $state('');

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
			const [lecturesData, providersData] = await Promise.all([
				apiFetch(`/lectures/?user_id=${user.id}`),
				apiFetch(`/llm/providers?user_id=${user.id}`)
			]);
			lectures = lecturesData.items || [];
			providers = providersData;
			if (providers.length > 0) {
				selectedProviderId = providers[0].id;
			}
		} catch (err) {
			console.error('Failed to fetch dashboard data:', err);
		} finally {
			isLoading = false;
		}
	}

	async function handleGenerate(e: SubmitEvent) {
		e.preventDefault();
		const user = auth.user;
		if (!user?.id || !selectedProviderId) return;

		isGenerating = true;
		generationError = '';

		try {
			const newLecture = await apiFetch('/llm/generate/lecture', {
				method: 'POST',
				body: JSON.stringify({
					prompt,
					provider_id: selectedProviderId,
					user_id: user.id
				})
			});
			goto(`/lectures/${newLecture.id}`);
		} catch (err: any) {
			generationError = err.message || 'Generation failed. Please try again.';
		} finally {
			isGenerating = false;
		}
	}

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<div class="container mx-auto max-w-7xl space-y-12 p-6 lg:p-12">
	<header class="space-y-6" in:fade={{ duration: 400 }}>
		<div class="flex flex-col justify-between gap-6 md:flex-row md:items-end">
			<div class="space-y-3">
				<div class="flex items-center gap-2">
					<div class="rounded-lg bg-primary/10 p-2">
						<BrainCircuit class="h-5 w-5 text-primary" />
					</div>
					<span class="text-sm font-medium text-muted-foreground">Dashboard</span>
				</div>
				<h1 class="text-3xl font-bold tracking-tight md:text-4xl">
					Learning <span class="text-primary">Center</span>
				</h1>
				<p class="text-muted-foreground">
					Welcome back! Continue your courses or create a new one.
				</p>
			</div>

			<Button
				onclick={() => (showGenerator = !showGenerator)}
				variant={showGenerator ? 'outline' : 'default'}
			>
				{#if showGenerator}
					<ChevronRight class="mr-2 h-4 w-4 rotate-90" />
					Cancel
				{:else}
					<Plus class="mr-2 h-4 w-4" />
					Generate Lecture
				{/if}
			</Button>
		</div>
	</header>

	{#if showGenerator}
		<section in:fly={{ y: 20, duration: 400 }}>
			<Card.Root class="overflow-hidden rounded-xl border-border">
				<Card.Header class="border-b border-border bg-muted/50">
					<div class="flex items-center gap-4">
						<div class="rounded-lg bg-primary/10 p-2">
							<Sparkles class="h-5 w-5 text-primary" />
						</div>
						<div>
							<Card.Title>Create New Lecture</Card.Title>
							<Card.Description>Describe what topic you want to learn about.</Card.Description>
						</div>
					</div>
				</Card.Header>

				<Card.Content class="space-y-6 p-6">
					{#if generationError}
						<div
							class="flex items-center gap-3 rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive"
						>
							{generationError}
						</div>
					{/if}

					{#if providers.length === 0}
						<div class="space-y-4 rounded-lg border border-amber-500/20 bg-amber-500/10 p-6 text-amber-600 dark:text-amber-400">
							<p class="font-medium">No AI models configured.</p>
							<Button onclick={() => goto('/providers')} variant="outline" size="sm">
								Add AI Model
							</Button>
						</div>
					{:else}
						<form onsubmit={handleGenerate} class="space-y-6">
							<div class="space-y-2">
								<Label class="text-sm font-medium">Learning Topic</Label>
								<textarea
									bind:value={prompt}
									placeholder="Describe the lecture topic..."
									required
									class="min-h-[120px] w-full resize-none rounded-lg border border-input bg-background p-4 text-sm transition-colors focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
								></textarea>
							</div>

							<div class="flex items-end gap-4">
								<div class="flex-1 space-y-2">
									<Label class="text-sm font-medium">AI Model</Label>
									<select
										bind:value={selectedProviderId}
										class="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
									>
										{#each providers as provider}
											<option value={provider.id}
												>{provider.provider_name} — {provider.model_name}</option
											>
										{/each}
									</select>
								</div>

								<Button type="submit" disabled={isGenerating || !prompt} class="gap-2">
									{#if isGenerating}
										<Loader2 class="h-4 w-4 animate-spin" />
										Creating...
									{:else}
										<Sparkles class="h-4 w-4" />
										Generate
									{/if}
								</Button>
							</div>
						</form>
					{/if}
				</Card.Content>
			</Card.Root>
		</section>
	{/if}

	<section class="space-y-6">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="h-8 w-1 rounded-full bg-primary"></div>
				<h2 class="text-xl font-semibold">Your Courses</h2>
			</div>
			<span class="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
				{lectures.length} Course{lectures.length === 1 ? '' : 's'}
			</span>
		</div>

		{#if isLoading}
			<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each Array(6) as _}
					<div class="h-72 rounded-xl border border-border bg-muted/50 p-6"></div>
				{/each}
			</div>
		{:else if lectures.length === 0}
			<div
				class="flex flex-col items-center justify-center space-y-4 rounded-xl border border-dashed border-border bg-muted/30 py-16 text-center"
				in:scale
			>
				<div class="rounded-full bg-muted p-4">
					<BookOpen class="h-8 w-8 text-muted-foreground" />
				</div>
				<div class="space-y-1">
					<h3 class="font-semibold">No Courses Yet</h3>
					<p class="text-sm text-muted-foreground">Create your first course to get started.</p>
				</div>
				<Button onclick={() => (showGenerator = true)} variant="outline" size="sm">
					Create Your First Course
				</Button>
			</div>
		{:else}
			<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each lectures as lecture, i (lecture.id)}
					<div in:fly={{ y: 20, delay: i * 50 }}>
						<button
							onclick={() => goto(`/lectures/${lecture.id}`)}
							class="w-full text-left"
						>
						<Card.Root
							class="transition-all hover:border-primary/30 hover:shadow-md cursor-pointer"
						>
							<Card.Header class="p-6 pb-4">
								<div class="mb-4 flex items-start justify-between">
									<div class="rounded-lg bg-primary/10 p-3">
										<BookOpen class="h-5 w-5 text-primary" />
									</div>
									<div class="text-right">
										<span class="block text-xs text-muted-foreground">Progress</span>
										<span class="text-lg font-semibold text-primary"
											>{Math.round(lecture.completion_percentage)}%</span
										>
									</div>
								</div>
								<Card.Title class="text-lg font-semibold leading-tight"
									>{lecture.title}</Card.Title
								>
								<Card.Description class="mt-2 line-clamp-2 text-muted-foreground">
									{lecture.description || 'No description provided.'}
								</Card.Description>
							</Card.Header>

							<Card.Content class="space-y-4 p-6 pt-0">
								<div class="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
									<div
										class="h-full bg-primary transition-all"
										style="width: {lecture.completion_percentage}%"
									></div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div class="rounded-lg border border-border bg-muted/50 p-3">
										<span class="block text-[10px] uppercase text-muted-foreground">Created</span>
										<span class="text-xs font-medium">{formatDate(lecture.created_at)}</span>
									</div>
									<div class="rounded-lg border border-border bg-muted/50 p-3">
										<span class="block text-[10px] uppercase text-muted-foreground">Last accessed</span>
										<span class="text-xs font-medium">{formatDate(lecture.last_accessed_at)}</span>
									</div>
								</div>
							</Card.Content>

							<Card.Footer class="flex items-center justify-between border-t border-border bg-muted/30 p-4">
								<span class="text-xs font-medium uppercase tracking-wide text-primary"
									>Continue Learning</span
								>
								<ArrowRight
									class="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1"
								/>
							</Card.Footer>
						</Card.Root>
						</button>
					</div>
				{/each}
			</div>
		{/if}
	</section>
</div>
