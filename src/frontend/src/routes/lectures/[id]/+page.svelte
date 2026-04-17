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
		XCircle,
		Pencil,
		Trash2,
		Save,
		X
	} from '@lucide/svelte';
	import { fade, fly } from 'svelte/transition';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { Skeleton } from '$lib/components/ui/skeleton';

	interface Step {
		id: number;
		title: string;
		order_key: number;
		completed: boolean;
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
	}

	let lecture = $state<Lecture | null>(null);
	let sections = $state<Section[]>([]);
	let isLoading = $state(true);
	let isLoadingSections = $state(true);
	let error = $state('');
	let isEditing = $state(false);
	let editTitle = $state('');
	let editDescription = $state('');
	let isDeleting = $state(false);

	async function fetchLecture(id: string) {
		try {
			lecture = await apiFetch(`/lectures/${id}`);
		} catch (err: any) {
			error = err.message || 'Failed to load course details.';
		} finally {
			isLoading = false;
		}
	}

	async function fetchSections(lectureId: string) {
		try {
			const sectionData = await apiFetch(`/lectures/${lectureId}/sections`);
			const sectionList = Array.isArray(sectionData) ? sectionData : [];

			const sectionsWithSteps = await Promise.all(
				sectionList.map(async (section: Section) => {
					try {
						const steps = await apiFetch(`/lectures/${lectureId}/sections/${section.id}/steps`);
						return { ...section, steps: Array.isArray(steps) ? steps : [] };
					} catch {
						return { ...section, steps: [] };
					}
				})
			);
			sections = sectionsWithSteps;
		} catch (err: any) {
			console.error('Failed to load sections:', err);
		} finally {
			isLoadingSections = false;
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
			fetchSections(id);
		}
	});

	function handleStepClick(step: Step) {
		if (!step.id) {
			console.error('Step ID is missing:', step);
			return;
		}
		goto(`/lectures/${page.params.id}/step/${step.id}`);
	}

	function startEdit() {
		if (lecture) {
			editTitle = lecture.title;
			editDescription = lecture.description || '';
			isEditing = true;
		}
	}

	async function saveEdit() {
		if (!lecture) return;
		try {
			const updated = await apiFetch(`/lectures/${lecture.id}`, {
				method: 'PATCH',
				body: JSON.stringify({
					title: editTitle,
					description: editDescription
				})
			});
			lecture = { ...lecture, ...updated };
			isEditing = false;
		} catch (err: any) {
			error = err.message || 'Failed to update lecture.';
		}
	}

	function cancelEdit() {
		isEditing = false;
		editTitle = '';
		editDescription = '';
	}

	async function confirmDelete() {
		if (!lecture) return;
		isDeleting = true;
	}

	async function deleteLecture() {
		if (!lecture) return;
		try {
			await apiFetch(`/lectures/${lecture.id}`, { method: 'DELETE' });
			goto('/lectures');
		} catch (err: any) {
			error = err.message || 'Failed to delete lecture.';
			isDeleting = false;
		}
	}
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
				<div class="flex flex-wrap gap-4 border-y border-border py-8 pt-4">
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
		<div class="mx-auto max-w-2xl space-y-6 rounded-[2rem] border border-destructive/10 bg-destructive/5 p-12 text-center">
			<XCircle class="mx-auto h-16 w-16 text-destructive/50" />
			<h2 class="text-2xl font-bold uppercase">Something went wrong</h2>
			<p class="text-muted-foreground">{error}</p>
			<Button onclick={() => goto('/')} variant="outline" class="border-destructive/30 text-destructive hover:bg-destructive/10">
				Return Home
			</Button>
		</div>
	{:else if lecture}
		<header class="relative space-y-8 pt-4" in:fade={{ duration: 1000 }}>
			<div class="flex flex-col justify-between gap-8 md:flex-row md:items-end">
				<div class="max-w-3xl space-y-4">
					<div class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-primary uppercase">
						<Layers class="h-4 w-4" />
						<span>Course Content</span>
					</div>
					{#if isEditing}
						<input
							bind:value={editTitle}
							class="font-unbounded text-4xl leading-tight font-black tracking-tighter uppercase md:text-6xl bg-transparent border-b-2 border-primary focus:outline-none w-full text-foreground"
							placeholder="Lecture Title"
						/>
						<textarea
							bind:value={editDescription}
							class="font-sans text-lg leading-relaxed bg-muted/20 border border-border rounded-xl p-4 w-full focus:outline-none focus:border-primary text-muted-foreground"
							rows="2"
							placeholder="Description"
						></textarea>
					{:else}
						<h1 class="font-unbounded text-4xl leading-tight font-black tracking-tighter uppercase md:text-6xl text-foreground">
							{lecture.title}
						</h1>
						<p class="font-sans text-lg leading-relaxed text-muted-foreground opacity-80">
							{lecture.description || 'Step through this AI-generated curriculum at your own pace.'}
						</p>
					{/if}
				</div>

				<div class="flex flex-col items-end gap-4">
					<div class="flex items-center gap-2">
						{#if isEditing}
							<Button onclick={saveEdit} variant="default" class="rounded-xl">
								<Save class="h-4 w-4 mr-2" />
								Save
							</Button>
							<Button onclick={cancelEdit} variant="ghost" class="rounded-xl">
								<X class="h-4 w-4" />
							</Button>
						{:else}
							<Button onclick={startEdit} variant="outline" class="rounded-xl">
								<Pencil class="h-4 w-4 mr-2" />
								Edit
							</Button>
							<Button onclick={confirmDelete} variant="ghost" class="rounded-xl text-destructive hover:text-destructive">
								<Trash2 class="h-4 w-4" />
							</Button>
						{/if}
					</div>

					<div class="min-w-[200px] rounded-[2rem] border border-primary/20 bg-primary/10 p-6 text-center shadow-2xl backdrop-blur-3xl">
						<span class="mb-1 block text-[10px] font-black tracking-widest text-primary uppercase">Completion</span>
						<div class="font-display text-5xl font-black text-foreground">
							{Math.round(lecture.completion_percentage)}%
						</div>
						<div class="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-muted">
							<div class="h-full bg-primary transition-all duration-1000" style="width: {lecture.completion_percentage}%"></div>
						</div>
					</div>
				</div>
			</div>
		</header>

		<section class="space-y-16 pb-24">
			{#if isLoadingSections}
				{#each Array(3) as _}
					<div class="space-y-8">
						<Skeleton class="h-8 w-64" />
						<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
							<Skeleton class="h-24 rounded-2xl" />
							<Skeleton class="h-24 rounded-2xl" />
						</div>
					</div>
				{/each}
			{:else}
				{#each [...sections].sort((a, b) => a.order_key - b.order_key) as section, i}
					<div class="space-y-8" in:fly={{ y: 20, delay: i * 150 }}>
						<div class="group flex items-center gap-6">
							<div class="flex h-10 w-10 items-center justify-center rounded-2xl border border-border bg-muted font-display font-black text-primary shadow-xl transition-all group-hover:scale-110 group-hover:border-primary/30">
								{i + 1}
							</div>
							<h2 class="font-display text-2xl font-black tracking-tight text-foreground uppercase transition-colors group-hover:text-primary">
								{section.title}
							</h2>
							<div class="h-px flex-grow bg-border transition-all group-hover:bg-primary/20"></div>
						</div>

						<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
							{#each [...section.steps].sort((a, b) => a.order_key - b.order_key) as step}
								<button
									onclick={() => handleStepClick(step)}
									class="group flex items-center justify-between rounded-2xl border border-border bg-card/40 p-6 text-left shadow-lg transition-all hover:border-primary/30 hover:bg-primary/10"
								>
									<div class="flex items-center gap-4 overflow-hidden">
										<div class="rounded-xl p-3 {step.completed ? 'bg-success/10 text-success' : 'bg-muted text-muted-foreground'} transition-transform group-hover:scale-110">
											{#if step.completed}
												<CheckCircle2 class="h-5 w-5" />
											{:else}
												<Play class="h-5 w-5 fill-current" />
											{/if}
										</div>
										<div class="flex min-w-0 flex-col">
											<span class="truncate text-sm font-bold text-foreground transition-colors group-hover:text-primary">{step.title}</span>
											<span class="text-[10px] font-black tracking-widest text-muted-foreground uppercase">
												{step.completed ? 'Completed' : 'Draft Ready'}
											</span>
										</div>
									</div>
									<ChevronRight class="h-4 w-4 text-muted-foreground transition-all group-hover:translate-x-1 group-hover:text-primary" />
								</button>
							{/each}
						</div>
					</div>
				{/each}
			{/if}
		</section>

		{#if isDeleting}
			<div class="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
				<div class="mx-4 max-w-md rounded-2xl border border-destructive/20 bg-card p-8 shadow-2xl">
					<div class="space-y-4 text-center">
						<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
							<Trash2 class="h-8 w-8 text-destructive" />
						</div>
						<h3 class="font-display text-2xl font-black uppercase text-foreground">Delete Lecture?</h3>
						<p class="text-muted-foreground">This action cannot be undone. All sections and steps will be permanently removed.</p>
						<div class="flex justify-center gap-4 pt-4">
							<Button onclick={() => (isDeleting = false)} variant="outline" class="rounded-xl">
								Cancel
							</Button>
							<Button onclick={deleteLecture} variant="destructive" class="rounded-xl">
								Delete
							</Button>
						</div>
					</div>
				</div>
			</div>
		{/if}
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
