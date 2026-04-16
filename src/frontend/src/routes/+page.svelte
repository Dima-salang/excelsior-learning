<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { settings } from '$lib/stores/settings.svelte';
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
		Cpu,
		LibraryBig,
		Settings
	} from '@lucide/svelte';
	import { fade, fly, scale } from 'svelte/transition';
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

	// Generator Form
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
	import { Skeleton } from '$lib/components/ui/skeleton';
	import { ChevronDown, Loader2 as LoadingIcon } from 'lucide-svelte';

	interface PaginatedResponse<T> {
		items: T[];
		total: number;
		page: number;
		size: number;
	}
</script>

<div class="container mx-auto max-w-7xl space-y-12 p-6 lg:p-12">
	<!-- Main Header -->
	<header class="relative space-y-6 pt-4" in:fade={{ duration: 1000 }}>
		<div class="flex flex-col justify-between gap-8 md:flex-row md:items-end">
			<div class="max-w-3xl space-y-4">
				<div
					class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-cyan-400 uppercase"
				>
					<LayoutDashboard class="h-4 w-4" />
					<span>Your Courses</span>
				</div>
				<h1
					class="font-unbounded text-4xl leading-none font-black tracking-tighter text-white uppercase md:text-6xl"
				>
					Your <span
						class="bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 bg-clip-text text-transparent"
						>Learning</span
					>
				</h1>
				<p class="max-w-2xl font-sans text-lg leading-relaxed text-slate-400 opacity-80">
					Continue your courses or create a new one to start learning.
				</p>
			</div>

			<Button
				onclick={() => (showGenerator = !showGenerator)}
				variant={showGenerator ? 'outline' : 'default'}
				class="flex h-16 items-center gap-3 rounded-2xl px-10 font-black tracking-widest uppercase shadow-lg transition-all hover:-translate-y-1"
			>
				{#if showGenerator}
					<Plus class="h-5 w-5 rotate-45 transition-transform" />
					Cancel
				{:else}
					<Plus class="h-5 w-5" />
					New Lecture
				{/if}
			</Button>
		</div>

		<!-- Background Blur Decor -->
		<div
			class="absolute -top-24 -left-20 -z-10 h-64 w-64 rounded-full bg-indigo-500/10 blur-[100px]"
		></div>
	</header>

	{#if showGenerator}
		<section in:fly={{ y: 20, duration: 600 }} class="relative mx-auto max-w-4xl">
			<Card.Root
				class="overflow-hidden rounded-[2.5rem] border-white/10 bg-slate-900/40 shadow-2xl ring-1 ring-white/10 backdrop-blur-3xl"
			>
				<Card.Header class="border-b border-white/5 bg-white/2 p-10">
					<div class="flex items-center gap-4">
						<div class="rounded-2xl border border-indigo-500/20 bg-indigo-500/10 p-3">
							<Sparkles class="h-6 w-6 text-indigo-400" />
						</div>
						<div>
							<Card.Title class="font-syne text-3xl font-black text-white uppercase"
								>Create Course</Card.Title
							>
							<Card.Description class="font-serif text-lg text-slate-400 italic"
								>Describe what you want to learn about.</Card.Description
							>
						</div>
					</div>
				</Card.Header>

				<Card.Content class="space-y-8 p-10">
					{#if error}
						<div
							class="flex items-center gap-3 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm font-bold text-red-400"
							in:fade
						>
							<div class="h-1.5 w-1.5 animate-pulse rounded-full bg-red-500"></div>
							{error}
						</div>
					{/if}

					{#if providers.length === 0}
						<div
							class="space-y-6 rounded-3xl border border-dashed border-white/10 bg-white/2 p-10 text-center"
						>
							<Cpu class="mx-auto h-12 w-12 text-slate-600" />
							<div class="space-y-2">
								<h3 class="text-xl font-bold text-white">No AI Models Detected</h3>
								<p class="font-serif text-slate-500 italic">
									You need to add at least one AI model provider to generate lectures.
								</p>
							</div>
							<Button
								onclick={() => goto('/providers')}
								variant="outline"
								class="rounded-xl border-indigo-500/50 text-indigo-400 hover:bg-indigo-500/10"
							>
								Manage AI Models
							</Button>
						</div>
					{:else}
						<form onsubmit={handleGenerate} class="space-y-8">
							<div class="space-y-3">
								<Label
									class="ml-1 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
									>Learning Topic</Label
								>
								<textarea
									bind:value={prompt}
									required
									placeholder="e.g. Introduction to Quantum Computing, or History of the Roman Empire..."
									class="min-h-[150px] w-full resize-none rounded-2xl border border-border bg-slate-900 p-6 font-sans text-lg text-white shadow-xl transition-all outline-none focus:ring-2 focus:ring-primary"
								></textarea>
							</div>

							<div class="grid grid-cols-1 items-end gap-8 md:grid-cols-2">
								<div class="space-y-3">
									<Label
										class="ml-1 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
										>AI Model</Label
									>
									<div class="relative">
										<select
											bind:value={settings.selectedProviderId}
											onchange={() => settings.setProvider(Number(settings.selectedProviderId))}
											class="h-14 w-full appearance-none rounded-xl border border-border bg-slate-900 px-4 text-white shadow-xl outline-none focus:ring-2 focus:ring-primary"
										>
											{#each providers as provider}
												<option value={provider.id} class="bg-slate-900 text-white"
													>{provider.provider_name} — {provider.model_name}</option
												>
											{/each}
										</select>
										<ChevronRight
											class="pointer-events-none absolute top-1/2 right-4 h-4 w-4 -translate-y-1/2 rotate-90 text-muted-foreground"
										/>
									</div>
								</div>

								<Button
									type="submit"
									variant="default"
									disabled={isGenerating || !prompt}
									class="h-14 w-full rounded-xl font-black tracking-widest uppercase shadow-lg"
								>
									{#if isGenerating}
										<Loader2 class="mr-2 h-5 w-5 animate-spin" />
										Generating...
									{:else}
										<Sparkles class="mr-2 h-4 w-4" />
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

	<!-- Course List Section -->
	<section class="space-y-8">
		<div class="flex items-center justify-between border-b border-white/5 pb-4">
			<div class="flex items-center gap-3">
				<div class="rounded-lg bg-indigo-500/10 p-2">
					<LibraryBig class="h-5 w-5 text-indigo-400" />
				</div>
				<h2 class="font-syne text-2xl font-black tracking-tight text-white uppercase">
					Active Courses
				</h2>
			</div>
			<span
				class="rounded-full bg-white/5 px-4 py-2 text-[10px] font-black tracking-widest text-slate-500 uppercase"
			>
				{lectures.length}{totalLectures > lectures.length ? `/${totalLectures}` : ''} Course{lectures.length ===
				1
					? ''
					: 's'}
			</span>
		</div>

		{#if isLoading}
			<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
				{#each Array(6) as _}
					<div
						class="flex h-[360px] flex-col justify-between space-y-4 rounded-[2rem] border border-white/5 bg-slate-950/40 p-8"
					>
						<div class="space-y-6">
							<div class="flex items-start justify-between">
								<Skeleton class="h-14 w-14 rounded-2xl" />
								<div class="space-y-2 text-right">
									<Skeleton class="ml-auto h-3 w-16" />
									<Skeleton class="ml-auto h-6 w-12" />
								</div>
							</div>
							<div class="space-y-3">
								<Skeleton class="h-8 w-3/4" />
								<Skeleton class="h-4 w-full" />
								<Skeleton class="h-4 w-2/3" />
							</div>
						</div>
						<div class="space-y-4">
							<Skeleton class="h-1.5 w-full rounded-full" />
							<div class="grid grid-cols-2 gap-4 pt-2">
								<Skeleton class="h-10 rounded-xl" />
								<Skeleton class="h-10 rounded-xl" />
							</div>
						</div>
					</div>
				{/each}
			</div>
		{:else if lectures.length === 0}
			<div
				class="space-y-8 rounded-[3rem] border-2 border-dashed border-white/5 bg-slate-900/20 py-32 text-center"
				in:scale
			>
				<div class="relative mx-auto h-24 w-24">
					<div class="absolute inset-0 animate-pulse rounded-full bg-indigo-500/10 blur-2xl"></div>
					<div class="relative rounded-full border border-white/10 bg-slate-950 p-6">
						<BookOpen class="h-12 w-12 text-slate-700" />
					</div>
				</div>
				<div class="mx-auto max-w-sm space-y-4">
					<h3 class="text-2xl font-bold text-white uppercase">Your Library is Empty</h3>
					<p class="font-serif text-slate-500 italic">
						Use the button above to generate your first AI-powered lecture.
					</p>
				</div>
				<Button
					onclick={() => (showGenerator = true)}
					variant="outline"
					class="rounded-xl border-indigo-500/50 px-8 text-indigo-400 hover:bg-indigo-500/10"
				>
					Start Learning
				</Button>
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
				{#each lectures as lecture, i (lecture.id)}
					<div in:fly={{ y: 20, delay: i * 100 }} class="group">
						<Card.Root
							onclick={() => goto(`/lectures/${lecture.id}`)}
							class="h-full cursor-pointer overflow-hidden rounded-[2rem] border-border bg-card/40 shadow-xl ring-1 ring-border/20 transition-all duration-500 hover:border-primary/30 hover:bg-muted/60"
						>
							<Card.Header class="p-8 pb-4">
								<div class="mb-6 flex items-start justify-between">
									<div
										class="rounded-2xl bg-indigo-500/10 p-4 transition-transform group-hover:scale-110"
									>
										<BookOpen class="h-6 w-6 text-indigo-400" />
									</div>
									<div class="text-right">
										<span class="text-[9px] font-black tracking-widest text-slate-500 uppercase"
											>Progress</span
										>
										<div class="font-syne text-xl font-black text-white">
											{Math.round(lecture.completion_percentage)}%
										</div>
									</div>
								</div>
								<div class="space-y-3">
									<Card.Title class="font-syne mt-2 text-2xl leading-tight font-black text-white"
										>{lecture.title}</Card.Title
									>
									<p
										class="line-clamp-2 font-serif text-base leading-relaxed text-slate-500 italic"
									>
										{lecture.description || 'No description available for this course.'}
									</p>
								</div>
							</Card.Header>

							<Card.Content class="space-y-6 p-8 pt-4">
								<div class="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
									<div
										class="h-full bg-primary transition-all duration-1000"
										style="width: {lecture.completion_percentage}%"
									></div>
								</div>

								<div class="grid grid-cols-2 gap-4">
									<div class="rounded-xl border border-border bg-muted/30 p-3">
										<span
											class="mb-1 block text-[8px] font-black tracking-widest text-muted-foreground uppercase"
											>Created</span
										>
										<span class="text-xs font-bold text-foreground/70"
											>{formatDate(lecture.created_at)}</span
										>
									</div>
									<div class="rounded-xl border border-border bg-muted/30 p-3">
										<span
											class="mb-1 block text-[8px] font-black tracking-widest text-muted-foreground uppercase"
											>Last seen</span
										>
										<span class="text-xs font-bold text-foreground/70"
											>{formatDate(lecture.last_accessed_at)}</span
										>
									</div>
								</div>
							</Card.Content>

							<Card.Footer
								class="flex items-center justify-between border-t border-border bg-muted/30 p-6"
							>
								<span class="text-[10px] font-black tracking-[0.2em] text-primary uppercase"
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
				<div class="mt-12 flex justify-center">
					<Button
						onclick={loadMoreLectures}
						disabled={isLoadingMore}
						variant="outline"
						class="group flex h-14 items-center gap-3 rounded-2xl border-border px-10 font-black tracking-widest uppercase transition-all hover:bg-primary/5 disabled:opacity-50"
					>
						{#if isLoadingMore}
							<LoadingIcon class="h-5 w-5 animate-spin" />
							Loading...
						{:else}
							<ChevronDown class="h-5 w-5 transition-transform group-hover:translate-y-1" />
							Load More Courses
						{/if}
					</Button>
				</div>
			{/if}
		{/if}
	</section>
</div>

<style>
	.font-unbounded {
		font-family: var(--font-display);
	}
	.font-sans {
		font-family: var(--font-sans);
	}
</style>
