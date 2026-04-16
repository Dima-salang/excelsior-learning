<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { settings } from '$lib/stores/settings.svelte';
	import {
		Sparkles,
		Plus,
		Loader2,
		ChevronRight,
		BookOpen,
		LayoutDashboard,
		ArrowRight,
		Cpu,
		LibraryBig,
		ChevronDown
	} from 'lucide-svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { Skeleton } from '$lib/components/ui/skeleton';

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
	let decks = $state<any[]>([]);
	let providers = $state<Provider[]>([]);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let isGenerating = $state(false);
	let showGenerator = $state(false);
	let currentPage = $state(1);
	let totalLectures = $state(0);
	const pageSize = 12;
	let hasMoreLectures = $derived(currentPage * pageSize < totalLectures);

	let prompt = $state('');
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
			const [lecturesData, providersData, decksData] = await Promise.all([
				apiFetch(`/lectures/?user_id=${user.id}&limit=${pageSize}&offset=0`),
				apiFetch(`/llm/providers?user_id=${user.id}`),
				apiFetch(`/decks?user_id=${user.id}&limit=${pageSize}&offset=0`)
			]);
			lectures = lecturesData.items || [];
			totalLectures = lecturesData.total || 0;
			currentPage = 1;
			providers = providersData || [];
			decks = decksData.items || [];
			if (providers.length > 0 && !settings.selectedProviderId) {
				settings.setProvider(providers[0].id);
			}
		} catch (err) {
			console.error('Failed to fetch dashboard data:', err);
		} finally {
			isLoading = false;
		}
	}

	async function loadMoreLectures() {
		const user = auth.user;
		if (!user?.id || isLoadingMore || !hasMoreLectures) return;

		isLoadingMore = true;
		try {
			const nextPage = currentPage + 1;
			const offset = (nextPage - 1) * pageSize;
			const lecturesData = await apiFetch(
				`/lectures/?user_id=${user.id}&limit=${pageSize}&offset=${offset}`
			);
			lectures = [...lectures, ...(lecturesData.items || [])];
			currentPage = nextPage;
		} catch (err) {
			console.error('Failed to load more lectures:', err);
		} finally {
			isLoadingMore = false;
		}
	}

	async function handleGenerate(e: SubmitEvent) {
		e.preventDefault();
		const user = auth.user;
		if (!user?.id || !settings.selectedProviderId) return;

		isGenerating = true;
		error = '';

		try {
			const newLecture = await apiFetch('/llm/generate/lecture', {
				method: 'POST',
				body: JSON.stringify({
					prompt,
					provider_id: settings.selectedProviderId,
					user_id: user.id
				})
			});
			goto(`/lectures/${newLecture.id}`);
		} catch (err: any) {
			error = err.message || 'Failed to generate lecture. Please check your AI model settings.';
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
	<header class="relative space-y-6 pt-4" in:fade={{ duration: 1000 }}>
		<div class="flex flex-col justify-between gap-8 md:flex-row md:items-end">
			<div class="max-w-3xl space-y-4">
				<div
					class="flex items-center gap-2 text-[10px] font-bold tracking-[0.2em] text-primary uppercase"
				>
					<LayoutDashboard class="h-4 w-4" />
					<span>Your Courses</span>
				</div>
				<h1 class="font-display text-4xl font-bold tracking-tight md:text-6xl">
					Your <span class="text-primary">Learning</span>
				</h1>
				<p class="text-muted-foreground">
					Continue your courses or create a new one to start learning.
				</p>
			</div>

			<Button
				onclick={() => (showGenerator = !showGenerator)}
				variant={showGenerator ? 'outline' : 'default'}
				class="flex h-12 items-center gap-2 px-6 font-semibold transition-all hover:-translate-y-1"
			>
				{#if showGenerator}
					<Plus class="h-4 w-4 rotate-45 transition-transform" />
					Cancel
				{:else}
					<Plus class="h-4 w-4" />
					New Lecture
				{/if}
			</Button>
		</div>
	</header>

	{#if showGenerator}
		<section in:fly={{ y: 20, duration: 600 }} class="relative mx-auto max-w-4xl">
			<Card.Root class="overflow-hidden rounded-xl border-border bg-card">
				<Card.Header class="border-b border-border bg-muted/50 p-6">
					<div class="flex items-center gap-4">
						<div class="rounded-lg bg-primary/10 p-2">
							<Sparkles class="h-5 w-5 text-primary" />
						</div>
						<div>
							<Card.Title class="text-xl font-semibold">Create Course</Card.Title>
							<Card.Description class="text-muted-foreground"
								>Describe what you want to learn about.</Card.Description
							>
						</div>
					</div>
				</Card.Header>

				<Card.Content class="space-y-6 p-6">
					{#if error}
						<div
							class="flex items-center gap-3 rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive"
							in:fade
						>
							{error}
						</div>
					{/if}

					{#if providers.length === 0}
						<div
							class="space-y-4 rounded-lg border border-dashed border-border bg-muted/50 p-8 text-center"
						>
							<Cpu class="mx-auto h-10 w-10 text-muted-foreground" />
							<div class="space-y-2">
								<h3 class="font-semibold">No AI Models Detected</h3>
								<p class="text-sm text-muted-foreground">
									You need to add at least one AI model provider to generate lectures.
								</p>
							</div>
							<Button onclick={() => goto('/providers')} variant="outline" size="sm">
								Manage AI Models
							</Button>
						</div>
					{:else}
						<form onsubmit={handleGenerate} class="space-y-6">
							<div class="space-y-2">
								<Label class="text-xs font-medium tracking-wide text-muted-foreground uppercase"
									>Learning Topic</Label
								>
								<textarea
									bind:value={prompt}
									required
									placeholder="e.g. Introduction to Quantum Computing..."
									class="min-h-[120px] w-full resize-none rounded-lg border border-input bg-background p-4 text-sm transition-colors focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none"
								></textarea>
							</div>

							<div class="flex items-end gap-4">
								<div class="flex-1 space-y-2">
									<Label class="text-xs font-medium tracking-wide text-muted-foreground uppercase"
										>AI Model</Label
									>
									<div class="relative">
										<select
											bind:value={settings.selectedProviderId}
											onchange={() => settings.setProvider(Number(settings.selectedProviderId))}
											class="h-10 w-full appearance-none rounded-lg border border-input bg-background px-3 pr-8 text-sm focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none"
										>
											{#each providers as provider}
												<option value={provider.id}
													>{provider.provider_name} — {provider.model_name}</option
												>
											{/each}
										</select>
										<ChevronRight
											class="pointer-events-none absolute top-1/2 right-3 h-4 w-4 -translate-y-1/2 rotate-90 text-muted-foreground"
										/>
									</div>
								</div>

								<Button type="submit" disabled={isGenerating || !prompt} class="h-10 gap-2">
									{#if isGenerating}
										<Loader2 class="h-4 w-4 animate-spin" />
										Generating...
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
				<div class="rounded-lg bg-primary/10 p-2">
					<LibraryBig class="h-5 w-5 text-primary" />
				</div>
				<h2 class="text-xl font-semibold">Active Courses</h2>
			</div>
			<span class="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
				{lectures.length}{totalLectures > lectures.length ? `/${totalLectures}` : ''} Course
			</span>
		</div>

		{#if isLoading}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each Array(6) as _}
					<div
						class="flex h-[280px] flex-col justify-between rounded-xl border border-border bg-muted/50 p-6"
					>
						<div class="space-y-4">
							<div class="flex items-start justify-between">
								<Skeleton class="h-12 w-12 rounded-lg" />
								<Skeleton class="h-6 w-16" />
							</div>
							<div class="space-y-2">
								<Skeleton class="h-6 w-3/4" />
								<Skeleton class="h-4 w-full" />
								<Skeleton class="h-4 w-2/3" />
							</div>
						</div>
						<div class="space-y-3">
							<Skeleton class="h-2 w-full rounded-full" />
							<div class="flex gap-2">
								<Skeleton class="h-8 flex-1 rounded-lg" />
								<Skeleton class="h-8 flex-1 rounded-lg" />
							</div>
						</div>
					</div>
				{/each}
			</div>
		{:else if lectures.length === 0}
			<div
				class="flex flex-col items-center justify-center space-y-6 rounded-2xl border border-dashed border-border bg-muted/30 py-20 text-center"
				in:scale
			>
				<div class="rounded-full bg-muted p-4">
					<BookOpen class="h-10 w-10 text-muted-foreground" />
				</div>
				<div class="space-y-2">
					<h3 class="text-xl font-semibold">Your Library is Empty</h3>
					<p class="text-sm text-muted-foreground">
						Use the button above to generate your first AI-powered lecture.
					</p>
				</div>
				<Button onclick={() => (showGenerator = true)} variant="outline" size="sm">
					Start Learning
				</Button>
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each lectures as lecture, i (lecture.id)}
					<div in:fly={{ y: 20, delay: i * 50 }} class="group">
						<Card.Root
							onclick={() => goto(`/lectures/${lecture.id}`)}
							class="h-full cursor-pointer transition-all hover:border-primary/30 hover:shadow-md"
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
								<Card.Title class="text-lg leading-tight font-semibold">{lecture.title}</Card.Title>
								<Card.Description class="mt-2 line-clamp-2 text-muted-foreground">
									{lecture.description || 'No description available.'}
								</Card.Description>
							</Card.Header>

							<Card.Content class="space-y-4 p-6 pt-0">
								<div class="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
									<div
										class="h-full bg-primary transition-all duration-1000"
										style="width: {lecture.completion_percentage}%"
									></div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div class="rounded-lg border border-border bg-muted/30 p-2">
										<span class="block text-[10px] text-muted-foreground uppercase">Created</span>
										<span class="text-xs font-medium">{formatDate(lecture.created_at)}</span>
									</div>
									<div class="rounded-lg border border-border bg-muted/30 p-2">
										<span class="block text-[10px] text-muted-foreground uppercase">Last seen</span>
										<span class="text-xs font-medium">{formatDate(lecture.last_accessed_at)}</span>
									</div>
								</div>
							</Card.Content>

							<Card.Footer
								class="flex items-center justify-between border-t border-border bg-muted/30 p-4"
							>
								<span class="text-xs font-medium tracking-wide text-primary uppercase"
									>Open Course</span
								>
								<ArrowRight
									class="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1"
								/>
							</Card.Footer>
						</Card.Root>
					</div>
				{/each}
			</div>

			{#if hasMoreLectures && !isLoading}
				<div class="flex justify-center pt-4">
					<Button
						onclick={loadMoreLectures}
						disabled={isLoadingMore}
						variant="outline"
						class="gap-2"
					>
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
	</section>
</div>
