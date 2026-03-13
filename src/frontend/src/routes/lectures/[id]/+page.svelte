<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import {
		BrainCircuit,
		Loader2,
		Play,
		CheckCircle2,
		ChevronRight,
		BookOpen,
		Clock,
		Target,
		ArrowLeft,
		Layers,
		Sparkles,
		XCircle
	} from '@lucide/svelte';
	import { fade, fly } from 'svelte/transition';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';

	interface Step {
		id: number;
		title: string;
		order_key: number;
		is_completed: boolean;
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
		description: string;
		completion_percentage: number;
		sections: Section[];
	}

	let lecture = $state<Lecture | null>(null);
	let isLoading = $state(true);
	let error = $state('');

	async function fetchLecture(id: string) {
		try {
			lecture = await apiFetch(`/lectures/${id}`);
		} catch (err: any) {
			error = err.message || 'Failed to load course details.';
		} finally {
			isLoading = false;
		}
	}

	$effect(() => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		const id = page.params.id;
		if (id && isLoading) {
			fetchLecture(id);
		}
	});

	function handleStepClick(step: Step) {
		if (!step.id) {
			console.error('Step ID is missing:', step);
			return;
		}
		goto(`/lectures/${page.params.id}/step/${step.id}`);
	}
	import { Skeleton } from '$lib/components/ui/skeleton';
</script>

<div class="container mx-auto max-w-5xl space-y-12 p-6 lg:p-12">
	{#if isLoading}
		<div class="space-y-16 py-4">
			<div class="space-y-6">
				<div class="flex flex-col justify-between gap-8 md:flex-row md:items-end">
					<div class="w-full max-w-2xl space-y-4">
						<Skeleton class="h-4 w-32" />
						<Skeleton class="h-16 w-full" />
						<Skeleton class="h-6 w-3/4" />
					</div>
				</div>
				<div class="flex flex-wrap gap-4 border-y border-white/5 py-8 pt-4">
					<Skeleton class="h-14 w-32 rounded-xl" />
					<Skeleton class="h-14 w-32 rounded-xl" />
					<Skeleton class="h-14 w-32 rounded-xl" />
				</div>
			</div>
			<div class="space-y-10">
				{#each Array(3) as _}
					<div class="space-y-6">
						<div class="flex items-center gap-4">
							<Skeleton class="h-6 w-48" />
							<Skeleton class="h-px grow" />
						</div>
						<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
							<Skeleton class="h-40 rounded-[2rem]" />
							<Skeleton class="h-40 rounded-[2rem]" />
						</div>
					</div>
				{/each}
			</div>
		</div>
	{:else if error}
		<div
			class="mx-auto max-w-2xl space-y-6 rounded-[2rem] border border-red-500/10 bg-red-500/5 p-12 text-center"
		>
			<XCircle class="mx-auto h-16 w-16 text-red-500/50" />
			<h2 class="text-2xl font-bold text-white uppercase">Something went wrong</h2>
			<p class="font-serif text-slate-400 italic">{error}</p>
			<Button
				onclick={() => goto('/')}
				variant="outline"
				class="border-red-500/30 text-red-400 hover:bg-red-500/10">Return Home</Button
			>
		</div>
	{:else if lecture}
		<header class="relative space-y-8 pt-4" in:fade={{ duration: 1000 }}>
			<div class="flex flex-col justify-between gap-8 md:flex-row md:items-end">
				<div class="max-w-3xl space-y-4">
					<div
						class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-indigo-400 uppercase"
					>
						<Layers class="h-4 w-4" />
						<span>Lecture Outline</span>
					</div>
					<h1
						class="font-unbounded text-4xl leading-tight font-black tracking-tighter text-white uppercase md:text-6xl"
					>
						{lecture.title}
					</h1>
					<p class="font-sans text-lg leading-relaxed text-slate-400 opacity-80">
						{lecture.description || 'Step through this AI-generated curriculum at your own pace.'}
					</p>
				</div>

				<div
					class="min-w-[200px] rounded-[2rem] border border-primary/20 bg-primary/10 p-6 text-center shadow-2xl backdrop-blur-3xl"
				>
					<span class="mb-1 block text-[10px] font-black tracking-widest text-primary uppercase"
						>Completion</span
					>
					<div class="font-display text-5xl font-black text-foreground">
						{Math.round(lecture.completion_percentage)}%
					</div>
					<div class="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
						<div
							class="h-full bg-indigo-500 transition-all duration-1000"
							style="width: {lecture.completion_percentage}%"
						></div>
					</div>
				</div>
			</div>

			<!-- Decor -->
			<div
				class="absolute -top-12 -right-12 -z-10 h-64 w-64 rounded-full bg-indigo-500/5 blur-[100px]"
			></div>
		</header>

		<section class="space-y-16 pb-24">
			{#each [...lecture.sections].sort((a, b) => a.order_key - b.order_key) as section, i}
				<div class="space-y-8" in:fly={{ y: 20, delay: i * 150 }}>
					<div class="group flex items-center gap-6">
						<div
							class="flex h-10 w-10 items-center justify-center rounded-2xl border border-border bg-muted font-display font-black text-primary shadow-xl transition-all group-hover:scale-110 group-hover:border-primary/30"
						>
							{i + 1}
						</div>
						<h2
							class="font-display text-2xl font-black tracking-tight text-foreground uppercase transition-colors group-hover:text-primary"
						>
							{section.title}
						</h2>
						<div class="h-px flex-grow bg-border transition-all group-hover:bg-primary/20"></div>
					</div>

					<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
						{#each [...section.steps].sort((a, b) => a.order_key - b.order_key) as step}
							<button
								onclick={() => handleStepClick(step)}
								class="group flex items-center justify-between rounded-2xl border border-border bg-card/40 p-6 text-left shadow-lg ring-1 ring-white/5 transition-all hover:border-primary/30 hover:bg-primary/10"
							>
								<div class="flex items-center gap-4 overflow-hidden">
									<div
										class="rounded-xl p-3 {step.is_completed
											? 'bg-emerald-500/10 text-emerald-400'
											: 'bg-muted text-muted-foreground'} transition-transform group-hover:scale-110"
									>
										{#if step.is_completed}
											<CheckCircle2 class="h-5 w-5" />
										{:else}
											<Play class="h-5 w-5 fill-current" />
										{/if}
									</div>
									<div class="flex min-w-0 flex-col">
										<span
											class="truncate text-sm font-bold text-foreground transition-colors group-hover:text-primary"
											>{step.title}</span
										>
										<span
											class="text-[10px] font-black tracking-widest text-muted-foreground uppercase"
										>
											{step.is_completed ? 'Completed' : 'Draft Ready'}
										</span>
									</div>
								</div>
								<ChevronRight
									class="h-4 w-4 text-muted-foreground transition-all group-hover:translate-x-1 group-hover:text-primary"
								/>
							</button>
						{/each}
					</div>
				</div>
			{/each}
		</section>
	{/if}
</div>

<style>
	.font-unbounded {
		font-family: var(--font-display);
	}
	.font-sans {
		font-family: var(--font-sans);
	}
</style>
