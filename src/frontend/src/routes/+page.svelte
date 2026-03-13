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
	let providers = $state<Provider[]>([]);
	let isLoading = $state(true);
	let isGenerating = $state(false);
	let showGenerator = $state(false);

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
			// Using more robust endpoint paths
			const [lecturesData, providersData] = await Promise.all([
				apiFetch(`/lectures/?user_id=${user.id}`),
				apiFetch(`/llm/providers?user_id=${user.id}`)
			]);
			lectures = lecturesData || [];
			providers = providersData || [];
			if (providers.length > 0 && !settings.selectedProviderId) {
				settings.setProvider(providers[0].id);
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
</script>

<div class="container mx-auto max-w-7xl space-y-12 p-6 lg:p-12">

	<!-- Main Header -->
	<header class="relative space-y-6 pt-4" in:fade={{ duration: 1000 }}>
		<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
			<div class="max-w-3xl space-y-4">
				<div class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-cyan-400 uppercase">
					<LayoutDashboard class="h-4 w-4" />
					<span>Learning Overview</span>
				</div>
				<h1 class="font-unbounded text-4xl md:text-6xl font-black tracking-tighter text-white leading-none uppercase">
					Your <span class="bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 bg-clip-text text-transparent">Courses</span>
				</h1>
				<p class="font-sans text-lg text-slate-400 leading-relaxed max-w-2xl opacity-80">
					Manage your AI-generated lectures and continue your learning journey.
				</p>
			</div>
			
			<Button
				onclick={() => (showGenerator = !showGenerator)}
				variant={showGenerator ? "outline" : "default"}
				class="h-16 px-10 rounded-2xl font-black tracking-widest uppercase transition-all shadow-lg hover:-translate-y-1 flex items-center gap-3"
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
		<div class="absolute -top-24 -left-20 -z-10 h-64 w-64 rounded-full bg-indigo-500/10 blur-[100px]"></div>
	</header>

	{#if showGenerator}
		<section in:fly={{ y: 20, duration: 600 }} class="relative max-w-4xl mx-auto">
			<Card.Root class="overflow-hidden rounded-[2.5rem] border-white/10 bg-slate-900/40 backdrop-blur-3xl shadow-2xl ring-1 ring-white/10">
				<Card.Header class="p-10 border-b border-white/5 bg-white/2">
					<div class="flex items-center gap-4">
						<div class="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20">
							<Sparkles class="h-6 w-6 text-indigo-400" />
						</div>
						<div>
							<Card.Title class="font-syne text-3xl font-black text-white uppercase">Generate Lecture</Card.Title>
							<Card.Description class="font-serif text-lg text-slate-400 italic">Describe what you want to learn today.</Card.Description>
						</div>
					</div>
				</Card.Header>
				
				<Card.Content class="p-10 space-y-8">
					{#if error}
						<div class="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-bold flex items-center gap-3" in:fade>
							<div class="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse"></div>
							{error}
						</div>
					{/if}

					{#if providers.length === 0}
						<div class="p-10 rounded-3xl border border-dashed border-white/10 bg-white/2 text-center space-y-6">
							<Cpu class="h-12 w-12 text-slate-600 mx-auto" />
							<div class="space-y-2">
								<h3 class="text-xl font-bold text-white">No AI Models Detected</h3>
								<p class="text-slate-500 font-serif italic">You need to add at least one AI model provider to generate lectures.</p>
							</div>
							<Button onclick={() => goto('/providers')} variant="outline" class="rounded-xl border-indigo-500/50 text-indigo-400 hover:bg-indigo-500/10">
								Manage AI Models
							</Button>
						</div>
					{:else}
						<form onsubmit={handleGenerate} class="space-y-8">
							<div class="space-y-3">
								<Label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">Learning Topic</Label>
								<textarea 
									bind:value={prompt}
									required
									placeholder="e.g. Introduction to Quantum Computing, or History of the Roman Empire..."
									class="w-full min-h-[150px] p-6 rounded-2xl bg-slate-900 border border-border text-white font-sans text-lg focus:ring-2 focus:ring-primary outline-none transition-all resize-none shadow-xl"
								></textarea>
							</div>

							<div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-end">
								<div class="space-y-3">
									<Label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">AI Model Provider</Label>
									<div class="relative">
										<select 
											bind:value={settings.selectedProviderId}
											onchange={() => settings.setProvider(Number(settings.selectedProviderId))}
											class="w-full h-14 bg-slate-900 border border-border rounded-xl px-4 text-white appearance-none outline-none focus:ring-2 focus:ring-primary shadow-xl"
										>
											{#each providers as provider}
												<option value={provider.id} class="bg-slate-900 text-white">{provider.provider_name} — {provider.model_name}</option>
											{/each}
										</select>
										<ChevronRight class="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground rotate-90 pointer-events-none" />
									</div>
								</div>
								
								<Button 
									type="submit" 
									variant="default"
									disabled={isGenerating || !prompt}
									class="h-14 w-full font-black tracking-widest uppercase rounded-xl shadow-lg"
								>
									{#if isGenerating}
										<Loader2 class="h-5 w-5 animate-spin mr-2" />
										Generating...
									{:else}
										<Sparkles class="h-4 w-4 mr-2" />
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
				<div class="p-2 rounded-lg bg-indigo-500/10">
					<LibraryBig class="h-5 w-5 text-indigo-400" />
				</div>
				<h2 class="font-syne text-2xl font-black text-white uppercase tracking-tight">Active Courses</h2>
			</div>
			<span class="text-[10px] font-black text-slate-500 uppercase tracking-widest bg-white/5 px-4 py-2 rounded-full">
				{lectures.length} Total Lectures
			</span>
		</div>

		{#if isLoading}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {#each Array(6) as _}
                    <div class="space-y-4 rounded-[2rem] border border-white/5 bg-slate-950/40 p-8 h-[360px] flex flex-col justify-between">
                        <div class="space-y-6">
                            <div class="flex justify-between items-start">
                                <Skeleton class="h-14 w-14 rounded-2xl" />
                                <div class="space-y-2 text-right">
                                    <Skeleton class="h-3 w-16 ml-auto" />
                                    <Skeleton class="h-6 w-12 ml-auto" />
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
			<div class="py-32 text-center space-y-8 bg-slate-900/20 rounded-[3rem] border-2 border-dashed border-white/5" in:scale>
				<div class="relative w-24 h-24 mx-auto">
					<div class="absolute inset-0 bg-indigo-500/10 rounded-full blur-2xl animate-pulse"></div>
					<div class="relative bg-slate-950 rounded-full border border-white/10 p-6">
						<BookOpen class="h-12 w-12 text-slate-700" />
					</div>
				</div>
				<div class="max-w-sm mx-auto space-y-4">
					<h3 class="text-2xl font-bold text-white uppercase">Your Library is Empty</h3>
					<p class="text-slate-500 font-serif italic">Use the button above to generate your first AI-powered lecture.</p>
				</div>
				<Button 
					onclick={() => showGenerator = true}
					variant="outline" 
					class="rounded-xl border-indigo-500/50 text-indigo-400 hover:bg-indigo-500/10 px-8"
				>
					Start Learning
				</Button>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				{#each lectures as lecture, i (lecture.id)}
					<div in:fly={{ y: 20, delay: i * 100 }} class="group">
						<Card.Root 
							onclick={() => goto(`/lectures/${lecture.id}`)}
							class="h-full cursor-pointer rounded-[2rem] border-white/5 bg-slate-950/40 hover:bg-slate-900/60 hover:border-indigo-500/30 transition-all duration-500 overflow-hidden shadow-xl ring-1 ring-white/10"
						>
							<Card.Header class="p-8 pb-4">
								<div class="flex items-start justify-between mb-6">
									<div class="p-4 rounded-2xl bg-indigo-500/10 group-hover:scale-110 transition-transform">
										<BookOpen class="h-6 w-6 text-indigo-400" />
									</div>
									<div class="text-right">
										<span class="text-[9px] font-black text-slate-500 uppercase tracking-widest">Progress</span>
										<div class="font-syne text-xl font-black text-white">{Math.round(lecture.completion_percentage)}%</div>
									</div>
								</div>
								<div class="space-y-3">
									<Card.Title class="font-syne text-2xl font-black text-white leading-tight mt-2">{lecture.title}</Card.Title>
									<p class="text-slate-500 font-serif italic line-clamp-2 text-base leading-relaxed">
										{lecture.description || 'No description available for this course.'}
									</p>
								</div>
							</Card.Header>

							<Card.Content class="p-8 pt-4 space-y-6">
								<div class="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
									<div class="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-1000" style="width: {lecture.completion_percentage}%"></div>
								</div>

								<div class="grid grid-cols-2 gap-4">
									<div class="p-3 bg-white/2 rounded-xl border border-white/5">
										<span class="text-[8px] font-black text-slate-600 tracking-widest uppercase block mb-1">Created</span>
										<span class="text-xs font-bold text-slate-300">{formatDate(lecture.created_at)}</span>
									</div>
									<div class="p-3 bg-white/2 rounded-xl border border-white/5">
										<span class="text-[8px] font-black text-slate-600 tracking-widest uppercase block mb-1">Last seen</span>
										<span class="text-xs font-bold text-slate-300">{formatDate(lecture.last_accessed_at)}</span>
									</div>
								</div>
							</Card.Content>

							<Card.Footer class="p-6 bg-white/2 border-t border-white/5 flex items-center justify-between">
								<span class="text-[10px] font-black text-indigo-400 uppercase tracking-[0.2em]">Open Course</span>
								<ArrowRight class="h-4 w-4 text-slate-500 group-hover:translate-x-1 transition-transform" />
							</Card.Footer>
						</Card.Root>
					</div>
				{/each}
			</div>
		{/if}
	</section>
</div>

<style>
	:global(body) {
		background-color: #020617;
		font-family: var(--font-sans);
	}
	.font-unbounded {
		font-family: var(--font-display);
	}
	.font-sans {
		font-family: var(--font-sans);
	}
</style>
