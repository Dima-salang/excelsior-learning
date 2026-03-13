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
		ArrowRight
	} from '@lucide/svelte';
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

	// Generator Form
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
			lectures = lecturesData;
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

			// Redirect to the newly created lecture
			goto(`/lectures/${newLecture.id}`);
		} catch (err: any) {
			generationError = err.message || 'Generation failed. The neural matrix is unstable.';
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

<div class="container mx-auto max-w-7xl space-y-16 p-6 lg:p-12">
	<!-- Navbar Logic (Simplified for now) -->
	<nav class="flex items-center justify-between py-4" in:fade>
		<div class="flex items-center gap-8">
			<a href="/dashboard" class="flex items-center gap-3">
				<div class="rounded-xl bg-indigo-600 p-2">
					<BrainCircuit class="h-6 w-6 text-white" />
				</div>
				<span class="font-syne text-2xl font-black tracking-tighter text-white">EXCELSIOR</span>
			</a>
			<div
				class="hidden items-center gap-6 text-sm font-bold tracking-widest text-slate-500 uppercase md:flex"
			>
				<a href="/dashboard" class="text-indigo-400">Dashboard</a>
				<a href="/providers" class="transition-colors hover:text-white">Providers</a>
				<a href="/library" class="transition-colors hover:text-white">Library</a>
			</div>
		</div>
		<div class="flex items-center gap-4">
			<div class="flex flex-col items-end">
				<span class="text-xs font-black text-white">{auth.user?.username || 'Scholar'}</span>
				<span class="text-[10px] text-slate-500 lowercase">{auth.user?.email || 'unverified'}</span>
			</div>
			<div class="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400 p-[1px]">
				<div class="flex h-full w-full items-center justify-center rounded-full bg-slate-950">
					<span class="text-xs font-bold text-white uppercase"
						>{auth.user?.username?.[0] || 'S'}</span
					>
				</div>
			</div>
		</div>
	</nav>

	<!-- Header -->
	<header
		class="relative flex flex-col items-end justify-between gap-8 pt-8 md:flex-row"
		in:fade={{ duration: 1200 }}
	>
		<div class="max-w-2xl space-y-4">
			<div
				class="ml-1 flex items-center gap-3 text-[10px] font-bold tracking-[0.3em] text-cyan-400 uppercase"
			>
				<LayoutDashboard class="h-4 w-4" />
				<span>Central Intelligence Hub</span>
			</div>
			<h1
				class="font-syne text-6xl leading-none font-black tracking-tighter text-white select-none md:text-8xl"
			>
				Academy <span
					class="bg-gradient-to-br from-indigo-500 via-cyan-400 to-emerald-400 bg-clip-text text-transparent"
					>Nexus</span
				>
			</h1>
			<p class="font-serif text-xl leading-relaxed text-slate-500 italic">
				Welcome back, scholar. Your cognitive blueprints are synchronized. Continue your ascent or
				initialize a new path of discovery.
			</p>
		</div>

		<Button
			onclick={() => (showGenerator = !showGenerator)}
			class="group flex h-16 items-center gap-3 rounded-3xl bg-indigo-600 px-10 font-black tracking-widest text-white uppercase shadow-[0_20px_40px_rgba(79,70,229,0.3)] transition-all hover:-translate-y-2 hover:bg-indigo-500 active:scale-95"
		>
			{#if showGenerator}
				<ChevronRight class="group-rotate-90 h-5 w-5 transition-transform" />
				Close Conduit
			{:else}
				<Plus class="h-5 w-5" />
				Generate Lecture
			{/if}
		</Button>

		<!-- Decorative Background Accent -->
		<div
			class="absolute -top-24 -left-24 -z-10 h-96 w-96 rounded-full bg-indigo-500/10 blur-[120px]"
		></div>
	</header>

	{#if showGenerator}
		<section in:fly={{ y: 40, duration: 800 }} class="relative mx-auto w-full max-w-4xl">
			<div class="absolute inset-0 -z-10 rounded-full bg-indigo-500/5 blur-[120px]"></div>

			<Card.Root
				class="overflow-hidden rounded-[3rem] border-white/10 bg-slate-950/80 shadow-[0_0_80px_rgba(0,0,0,0.5)] ring-1 ring-white/15 backdrop-blur-3xl"
			>
				<Card.Header class="border-b border-white/5 p-12 pb-6">
					<div class="mb-2 flex items-center gap-4">
						<div class="rounded-2xl border border-indigo-500/20 bg-indigo-500/10 p-3">
							<Sparkles class="h-6 w-6 text-indigo-400" />
						</div>
						<div>
							<Card.Title class="font-syne text-3xl font-black text-white"
								>Neural Manifestation</Card.Title
							>
							<Card.Description class="font-serif text-lg text-slate-400 italic">
								Articulate your prompt. The synthetic nodes will craft your curriculum.
							</Card.Description>
						</div>
					</div>
				</Card.Header>

				<Card.Content class="space-y-10 p-12">
					{#if generationError}
						<div
							class="flex items-center gap-4 rounded-2xl border border-red-500/20 bg-red-500/10 p-6 text-sm font-bold text-red-400"
							transition:fade
						>
							<div class="h-2 w-2 animate-pulse rounded-full bg-red-500"></div>
							{generationError}
						</div>
					{/if}

					{#if providers.length === 0}
						<div
							class="space-y-4 rounded-[2rem] border border-amber-500/20 bg-amber-500/5 p-8 text-amber-400/80"
						>
							<p class="font-serif text-lg italic">
								No intelligence nodes detected. You must establish a neural link before generation.
							</p>
							<Button
								variant="outline"
								onclick={() => goto('/providers')}
								class="border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
							>
								Configure Providers
							</Button>
						</div>
					{:else}
						<form onsubmit={handleGenerate} class="space-y-10">
							<div class="space-y-4">
								<Label
									class="ml-1 flex items-center gap-2 text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase"
								>
									<Target class="h-3 w-3" /> Cognitive Objective
								</Label>
								<textarea
									bind:value={prompt}
									placeholder="Describe the lecture topic in detail (e.g. 'Advanced Quantum Mechanics and the Wave-Particle Duality')..."
									required
									class="min-h-[160px] w-full resize-none rounded-3xl border border-white/5 bg-slate-900/50 p-8 font-serif text-xl text-white italic transition-all outline-none placeholder:text-slate-600 focus:bg-slate-900 focus:ring-2 focus:ring-indigo-500"
								></textarea>
							</div>

							<div class="grid grid-cols-1 items-end gap-10 md:grid-cols-2">
								<div class="space-y-4">
									<Label
										class="ml-1 flex items-center gap-2 text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase"
									>
										<Zap class="h-3 w-3" /> Intelligence Source
									</Label>
									<select
										bind:value={selectedProviderId}
										class="h-16 w-full appearance-none rounded-2xl border border-white/5 bg-slate-900/50 px-6 text-lg text-white transition-all outline-none focus:ring-2 focus:ring-indigo-500"
									>
										{#each providers as provider}
											<option value={provider.id}
												>{provider.provider_name} — {provider.model_name}</option
											>
										{/each}
									</select>
								</div>

								<Button
									type="submit"
									disabled={isGenerating || !prompt}
									class="flex h-16 items-center justify-center gap-3 rounded-2xl bg-white text-lg font-black text-slate-950 shadow-[0_0_40px_rgba(255,255,255,0.15)] transition-all hover:bg-slate-200"
								>
									{#if isGenerating}
										<Loader2 class="h-6 w-6 animate-spin" />
										Manifesting Knowledge...
									{:else}
										<Sparkles class="h-5 w-5" />
										Initialize Generation
									{/if}
								</Button>
							</div>
						</form>
					{/if}
				</Card.Content>
			</Card.Root>
		</section>
	{/if}

	<!-- Lectures Section -->
	<section class="space-y-12">
		<div class="relative flex items-center justify-between border-b border-white/5 pb-8">
			<div class="flex items-center gap-4">
				<div
					class="h-12 w-1.5 overflow-hidden rounded-full bg-gradient-to-b from-indigo-500 to-transparent"
				>
					<div class="h-full w-full animate-pulse bg-cyan-400"></div>
				</div>
				<div>
					<h2 class="font-syne text-3xl font-black tracking-tight text-white uppercase">
						Active Curriculums
					</h2>
					<p class="font-serif text-base text-slate-500 italic">
						Your personalized path to mastery.
					</p>
				</div>
			</div>
			<div
				class="rounded-full border border-white/10 bg-white/5 px-6 py-2 text-[10px] font-black tracking-[0.3em] text-indigo-400 uppercase backdrop-blur-md"
			>
				{lectures.length} Total Path{lectures.length === 1 ? '' : 's'}
			</div>
		</div>

		{#if isLoading}
			<div class="flex flex-col items-center justify-center space-y-8 py-40">
				<div class="relative h-24 w-24">
					<div
						class="absolute inset-0 scale-150 animate-pulse rounded-full border-[3px] border-indigo-500/10"
					></div>
					<div
						class="absolute inset-0 animate-[spin_1.5s_linear_infinite] rounded-full border-t-[3px] border-indigo-500"
					></div>
					<BrainCircuit class="absolute inset-0 m-auto h-8 w-8 animate-pulse text-indigo-400" />
				</div>
				<div class="space-y-2 text-center">
					<p class="font-syne text-xl font-black tracking-widest text-white uppercase">
						Synchronizing Nexus
					</p>
					<p class="font-serif text-slate-500 italic">
						Retrieving cognitive blueprints from secure storage...
					</p>
				</div>
			</div>
		{:else if lectures.length === 0}
			<div
				in:scale={{ duration: 1000, opacity: 0, start: 0.9 }}
				class="group flex flex-col items-center justify-center space-y-10 rounded-[4rem] border-2 border-dashed border-white/5 bg-slate-900/20 py-40 backdrop-blur-sm"
			>
				<div class="relative">
					<div
						class="absolute inset-0 rounded-full bg-indigo-500/20 blur-[60px] transition-all group-hover:blur-[80px]"
					></div>
					<div
						class="relative rounded-full border border-white/10 bg-slate-950 p-10 shadow-2xl transition-transform duration-700 group-hover:scale-110"
					>
						<BookOpen
							class="h-16 w-16 text-slate-700 transition-colors group-hover:text-indigo-400"
						/>
					</div>
				</div>
				<div class="max-w-sm space-y-4 px-6 text-center">
					<h3 class="font-syne text-3xl font-black tracking-tight text-white uppercase">
						The Library is Silent
					</h3>
					<p class="font-serif text-lg leading-relaxed text-slate-500 italic">
						No active curriculums found. Use the power of synthesis to create your first lecture.
					</p>
				</div>
				<Button
					variant="outline"
					onclick={() => (showGenerator = true)}
					class="h-14 rounded-2xl border-indigo-500/50 px-10 font-black tracking-widest text-indigo-400 uppercase transition-all hover:scale-105 hover:bg-indigo-500/10 active:scale-95"
				>
					Initialize Discovery
				</Button>
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-10 md:grid-cols-2 xl:grid-cols-3">
				{#each lectures as lecture, i (lecture.id)}
					<div in:fly={{ y: 30, delay: i * 150, duration: 1000 }} class="group h-full">
						<Card.Root
							onclick={() => goto(`/lectures/${lecture.id}`)}
							class="group relative flex h-full cursor-pointer flex-col overflow-hidden rounded-[3rem] border-white/5 bg-slate-950/40 shadow-2xl ring-1 ring-white/10 backdrop-blur-md transition-all duration-700 hover:bg-slate-950/70 hover:ring-indigo-500/40"
						>
							<!-- Floating Glow -->
							<div
								class="absolute top-0 right-0 -z-10 h-48 w-48 rounded-full bg-indigo-500/5 blur-[80px] transition-all duration-1000 group-hover:bg-indigo-500/15"
							></div>
							<div
								class="absolute -bottom-10 -left-10 -z-10 h-32 w-32 rounded-full bg-cyan-500/5 blur-[60px] transition-all duration-1000 group-hover:bg-cyan-500/15"
							></div>

							<Card.Header class="flex-grow-0 p-10 pb-6">
								<div class="mb-8 flex items-start justify-between">
									<div
										class="rounded-[1.5rem] border border-white/10 bg-gradient-to-br from-indigo-500/10 to-cyan-500/10 p-5 shadow-xl transition-all duration-700 group-hover:scale-110 group-hover:rotate-6"
									>
										<BookOpen class="h-8 w-8 text-indigo-400" />
									</div>
									<div class="flex flex-col items-end gap-1">
										<span class="text-[10px] font-black tracking-widest text-slate-500 uppercase"
											>Mastery</span
										>
										<span class="font-syne text-2xl font-black text-white"
											>{Math.round(lecture.completion_percentage)}%</span
										>
									</div>
								</div>

								<div class="space-y-4">
									<Card.Title
										class="font-syne text-3xl leading-tight font-black text-white transition-all group-hover:bg-gradient-to-r group-hover:from-indigo-400 group-hover:to-cyan-400 group-hover:bg-clip-text group-hover:text-transparent"
									>
										{lecture.title}
									</Card.Title>
									<p class="line-clamp-2 font-serif text-lg leading-relaxed text-slate-400 italic">
										{lecture.description || 'No description provided for this path of study.'}
									</p>
								</div>
							</Card.Header>

							<Card.Content class="flex-grow p-10 pt-0">
								<div class="space-y-8">
									<!-- Progress Bar -->
									<div class="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
										<div
											class="h-full bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 transition-all duration-1000 ease-out"
											style="width: {lecture.completion_percentage}%"
										></div>
									</div>

									<div class="grid grid-cols-2 gap-4">
										<div class="space-y-1 rounded-2xl border border-white/5 bg-white/5 p-4">
											<div
												class="flex items-center gap-2 text-[10px] font-black tracking-widest text-slate-500 uppercase"
											>
												<Calendar class="h-3 w-3" /> Manifested
											</div>
											<div class="text-xs font-bold text-slate-300">
												{formatDate(lecture.created_at)}
											</div>
										</div>
										<div class="space-y-1 rounded-2xl border border-white/5 bg-white/5 p-4">
											<div
												class="flex items-center gap-2 text-[10px] font-black tracking-widest text-slate-500 uppercase"
											>
												<Clock class="h-3 w-3" /> Last Access
											</div>
											<div class="text-xs font-bold text-slate-300">
												{formatDate(lecture.last_accessed_at)}
											</div>
										</div>
									</div>
								</div>
							</Card.Content>

							<Card.Footer class="border-t border-white/5 bg-white/[0.02] p-8">
								<div class="group/btn flex w-full items-center justify-between">
									<span class="text-[10px] font-black tracking-[0.3em] text-indigo-400 uppercase"
										>Resynchronize Path</span
									>
									<div
										class="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 transition-all group-hover/btn:bg-white group-hover/btn:text-slate-950"
									>
										<ArrowRight
											class="h-5 w-5 transition-transform group-hover/btn:translate-x-1"
										/>
									</div>
								</div>
							</Card.Footer>
						</Card.Root>
					</div>
				{/each}
			</div>
		{/if}
	</section>
</div>

<style>
	:global(.container) {
		max-width: 1400px;
	}
	.font-syne {
		font-family: 'Syne', sans-serif;
	}
</style>
