<script lang="ts">
	import { onMount } from 'svelte';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { Button } from '$lib/components/ui/button';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import FilterBar from '$lib/components/FilterBar.svelte';
	import { BookOpen, Plus, Calendar, ChevronRight, Loader2, Sparkles, CheckCircle2, Circle, Clock } from '@lucide/svelte';
	import { goto } from '$app/navigation';

	interface Lecture {
		id: number;
		title: string;
		description: string | null;
		completion_percentage: number;
		created_at: string;
		last_accessed_at: string;
	}

	let lectures = $state<Lecture[]>([]);
	let isLoading = $state(true);
	let isLoadingMore = $state(false);
	let error = $state('');
	let currentPage = $state(1);
	let totalLectures = $state(0);
	let showGenerator = $state(false);
	let prompt = $state('');
	let providers = $state<any[]>([]);
	let selectedProviderId = $state<number | null>(null);
	let isGenerating = $state(false);
	let generationError = $state('');
	const pageSize = 12;

	// Filter state
	let searchQuery = $state('');
	let sortBy = $state('descending');
	let statusFilter = $state('all');
	let searchTimeout: number;

	let hasMoreLectures = $derived(currentPage * pageSize < totalLectures);

	async function fetchLectures(append = false) {
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

		// Add status filter (handled client-side for ranges)
		if (statusFilter !== 'all') {
			params.set('status', statusFilter);
		}

		try {
			if (!append) {
				isLoading = true;
				currentPage = 1;
			}
			const response = await apiFetch(`/lectures/?${params.toString()}`);

			let items = response.items || [];
			// Client-side filtering for status since API handles exact match only
			if (statusFilter === 'in_progress') {
				items = items.filter((l: Lecture) => l.completion_percentage > 0 && l.completion_percentage < 100);
			} else if (statusFilter === 'not_started') {
				items = items.filter((l: Lecture) => l.completion_percentage === 0);
			}

			if (append) {
				lectures = [...lectures, ...items];
				currentPage++;
			} else {
				lectures = items;
				totalLectures = response.total || 0;
			}
		} catch (err: any) {
			error = err.message || 'Failed to retrieve courses.';
		} finally {
			isLoading = false;
			isLoadingMore = false;
		}
	}

	async function fetchProviders() {
		if (!auth.user) return;
		try {
			const data = await apiFetch(`/llm/providers?user_id=${auth.user.id}`);
			providers = data || [];
			if (providers.length > 0 && !selectedProviderId) {
				selectedProviderId = providers[0].id;
			}
		} catch (err) {
			console.error('Failed to fetch providers:', err);
		}
	}

	function handleSearchChange(value: string) {
		clearTimeout(searchTimeout);
		searchTimeout = window.setTimeout(() => {
			fetchLectures();
		}, 300);
	}

	function handleSortChange(value: string) {
		sortBy = value;
		fetchLectures();
	}

	function handleStatusChange(value: string) {
		statusFilter = value;
		fetchLectures();
	}

	function handleClearFilters() {
		searchQuery = '';
		sortBy = 'descending';
		statusFilter = 'all';
		fetchLectures();
	}

	async function loadMoreLectures() {
		if (isLoadingMore || !hasMoreLectures) return;
		isLoadingMore = true;
		await fetchLectures(true);
	}

	async function handleGenerate(e: SubmitEvent) {
		e.preventDefault();
		const user = auth.user;
		if (!user?.id || !selectedProviderId || !prompt.trim()) return;

		isGenerating = true;
		generationError = '';

		try {
			const newLecture = await apiFetch('/llm/generate/lecture', {
				method: 'POST',
				body: JSON.stringify({
					prompt: prompt.trim(),
					provider_id: selectedProviderId,
					user_id: user.id
				})
			});
			goto(`/lectures/${newLecture.id}`);
		} catch (err: any) {
			generationError = err.message || 'Generation failed.';
		} finally {
			isGenerating = false;
		}
	}

	onMount(() => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		fetchLectures();
		fetchProviders();
	});

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function getStatusBadge(lecture: Lecture) {
		if (lecture.completion_percentage === 0) {
			return { label: 'Not Started', class: 'text-muted-foreground bg-muted' };
		} else if (lecture.completion_percentage === 100) {
			return { label: 'Completed', class: 'text-success bg-success/10 border-success/20' };
		} else {
			return { label: 'In Progress', class: 'text-warning bg-warning/10 border-warning/20' };
		}
	}
</script>

<svelte:head>
	<title>Courses — Excelsior</title>
</svelte:head>

<div class="container mx-auto max-w-7xl space-y-8 p-6 py-12 lg:p-12">
	<header class="flex flex-col justify-between gap-6 md:flex-row md:items-end" in:fade>
		<div class="space-y-2">
			<p class="text-xs font-medium tracking-wide text-primary uppercase">
				{#if totalLectures > 0}
					{lectures.length}{totalLectures > lectures.length ? `/${totalLectures}` : ''} Courses
				{:else}
					Study Courses
				{/if}
			</p>
			<h1 class="font-display text-4xl font-bold tracking-tight md:text-5xl">
				Your <span class="text-primary">Courses</span>
			</h1>
			<p class="text-muted-foreground">
				AI-generated curriculum structured for optimal learning.
			</p>
		</div>

		<Button onclick={() => (showGenerator = !showGenerator)} class="gap-2">
			{#if showGenerator}
				Cancel
			{:else}
				<Plus class="h-4 w-4" />
				New Course
			{/if}
		</Button>
	</header>

	{#if showGenerator}
		<div in:fly={{ y: 20, duration: 300 }} class="rounded-xl border border-border bg-card p-6">
			{#if providers.length === 0}
				<div class="flex flex-col items-center justify-center space-y-4 py-8 text-center">
					<p class="text-muted-foreground">No AI models configured.</p>
					<Button onclick={() => goto('/providers')} variant="outline" size="sm">
						Add AI Model
					</Button>
				</div>
			{:else}
				<form onsubmit={handleGenerate} class="space-y-4">
					{#if generationError}
						<p class="text-sm text-destructive">{generationError}</p>
					{/if}
					<div class="space-y-2">
						<label for="topic" class="text-sm font-medium">Topic</label>
						<textarea
							id="topic"
							bind:value={prompt}
							placeholder="Describe what you want to learn..."
							required
							class="min-h-[100px] w-full resize-none rounded-lg border border-input bg-background p-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
						></textarea>
					</div>
					<div class="flex items-end gap-4">
						<div class="flex-1 space-y-2">
							<label for="model" class="text-sm font-medium">AI Model</label>
							<select
								id="model"
								bind:value={selectedProviderId}
								class="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
							>
								{#each providers as p}
									<option value={p.id}>{p.provider_name} — {p.model_name}</option>
								{/each}
							</select>
						</div>
						<Button type="submit" disabled={isGenerating || !prompt.trim()} class="gap-2">
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
		</div>
	{/if}

	<!-- Filter Bar -->
	<FilterBar
		bind:searchValue={searchQuery}
		searchPlaceholder="Search courses..."
		onSearchChange={handleSearchChange}
		sortOptions={[
			{ value: 'descending', label: 'Recently Accessed' },
			{ value: 'ascending', label: 'Oldest First' }
		]}
		bind:sortValue={sortBy}
		onSortChange={handleSortChange}
		statusOptions={[
			{ value: 'all', label: 'All Status' },
			{ value: 'not_started', label: 'Not Started' },
			{ value: 'in_progress', label: 'In Progress' },
			{ value: 'completed', label: 'Completed' }
		]}
		bind:statusValue={statusFilter}
		onStatusChange={handleStatusChange}
		onClear={handleClearFilters}
	/>

	{#if isLoading}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each Array(6) as _}
				<div class="h-72 rounded-xl border border-border bg-muted/50 p-6">
					<div class="flex h-full flex-col justify-between">
						<div class="space-y-4">
							<Skeleton class="h-12 w-12 rounded-lg" />
							<div class="space-y-2">
								<Skeleton class="h-6 w-3/4" />
								<Skeleton class="h-4 w-full" />
								<Skeleton class="h-4 w-2/3" />
							</div>
						</div>
						<Skeleton class="h-1 w-full rounded-full" />
					</div>
				</div>
			{/each}
		</div>
	{:else if error}
		<div class="flex flex-col items-center justify-center space-y-6 rounded-xl border border-destructive/20 bg-destructive/10 py-20 text-center">
			<p class="font-medium text-destructive">{error}</p>
			<Button onclick={() => fetchLectures()} variant="outline" size="sm">Retry</Button>
		</div>
	{:else if lectures.length === 0}
		<div
			class="flex flex-col items-center justify-center space-y-6 rounded-2xl border border-dashed border-border bg-muted/30 py-20 text-center"
			in:scale
		>
			<div class="rounded-full bg-primary/10 p-4">
				<BookOpen class="h-10 w-10 text-primary" />
			</div>
			<div class="space-y-2">
				{#if searchQuery || statusFilter !== 'all'}
					<h2 class="text-xl font-semibold">No courses match your filters</h2>
					<p class="text-sm text-muted-foreground">
						Try adjusting your search or filter criteria.
					</p>
					<Button onclick={handleClearFilters} variant="outline" size="sm">Clear Filters</Button>
				{:else}
					<h2 class="text-xl font-semibold">No Courses Yet</h2>
					<p class="text-sm text-muted-foreground">
						Generate your first AI-powered course to start learning.
					</p>
					<Button onclick={() => (showGenerator = true)}>Create Your First Course</Button>
				{/if}
			</div>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each lectures as lecture, i (lecture.id)}
				{@const status = getStatusBadge(lecture)}
				<button
					in:fly={{ y: 20, delay: Math.min(i * 50, 300) }}
					class="group flex h-full cursor-pointer flex-col rounded-xl border border-border bg-card p-6 text-left transition-all hover:border-primary/30 hover:shadow-md"
					onclick={() => goto(`/lectures/${lecture.id}`)}
				>
					<div class="flex h-full flex-col justify-between">
						<div class="space-y-4">
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-3">
									<div class="rounded-lg bg-primary/10 p-2">
										<BookOpen class="h-5 w-5 text-primary" />
									</div>
									<span class="rounded-full border px-2 py-0.5 text-[10px] font-bold {status.class}">
										{#if lecture.completion_percentage === 0}
											Not Started
										{:else if lecture.completion_percentage === 100}
											Completed
										{:else}
											In Progress
										{/if}
									</span>
								</div>
								<span class="text-lg font-bold text-primary">
									{Math.round(lecture.completion_percentage)}%
								</span>
							</div>

							<div class="space-y-2">
								<h3 class="text-lg font-semibold transition-colors group-hover:text-primary line-clamp-1">
									{lecture.title}
								</h3>
								<p class="line-clamp-3 text-sm text-muted-foreground">
									{lecture.description || 'No description provided.'}
								</p>
							</div>
						</div>

						<div class="mt-4 space-y-3">
							<div class="h-1 w-full overflow-hidden rounded-full bg-secondary">
								<div
									class="h-full bg-primary transition-all"
									style="width: {lecture.completion_percentage}%"
								></div>
							</div>
							<div class="flex items-center justify-between text-xs text-muted-foreground">
								<span class="flex items-center gap-1">
									<Calendar class="h-3 w-3" />
									{formatDate(lecture.created_at)}
								</span>
								<span class="flex items-center gap-1 font-medium text-primary">
									Continue
									<ChevronRight class="h-3 w-3 transition-transform group-hover:translate-x-1" />
								</span>
							</div>
						</div>
					</div>
				</button>
			{/each}
		</div>

		{#if hasMoreLectures && !isLoading}
			<div class="flex justify-center pt-4">
				<Button onclick={loadMoreLectures} disabled={isLoadingMore} variant="outline" class="gap-2">
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
