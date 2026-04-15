<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import {
		Plus,
		Trash2,
		Settings2,
		ExternalLink,
		Cpu,
		KeyRound,
		Globe,
		BrainCircuit,
		Loader2,
		ShieldCheck,
		Zap,
		ChevronRight,
		Info,
		CheckCircle2,
		XCircle,
		Terminal,
		Copy,
		Search
	} from '@lucide/svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { goto } from '$app/navigation';

	interface Provider {
		id: number;
		provider_name: string;
		model_name: string;
		base_url?: string | null;
		additional_params?: string | null;
		created_at: string;
		updated_at: string;
	}

	let providers = $state<Provider[]>([]);
	let isLoading = $state(true);
	let isAddingProvider = $state(false);
	let editingProviderId = $state<number | null>(null);

	let form = $state({
		provider_name: '',
		model_name: '',
		api_key: '',
		base_url: '',
		additional_params: ''
	});

	let isSubmitting = $state(false);
	let error = $state('');
	let successMessage = $state('');
	let availableModels = $state<{ name: string; display_name: string }[]>([]);
	let isFetchingModels = $state(false);
	let modelSearchQuery = $state('');
	let isModelDropdownOpen = $state(false);

	// Close dropdown when clicking outside
	import { onMount } from 'svelte';
	let dropdownRef = $state<HTMLElement | null>(null);
	onMount(() => {
		const handleClickOutside = (e: MouseEvent) => {
			if (dropdownRef && !dropdownRef.contains(e.target as Node)) {
				isModelDropdownOpen = false;
				if (form.model_name && !filteredModels.find((m) => m.name === form.model_name)) {
					// retain if it was manually typed but not in list
				}
			}
		};
		document.addEventListener('mousedown', handleClickOutside);
		return () => document.removeEventListener('mousedown', handleClickOutside);
	});

	let filteredModels = $derived(
		availableModels.filter(
			(m) =>
				m.name.toLowerCase().includes(modelSearchQuery.toLowerCase()) ||
				m.display_name.toLowerCase().includes(modelSearchQuery.toLowerCase())
		)
	);

	let lastProvider = $state('');
	$effect(() => {
		const currentProvider = form.provider_name.toLowerCase();
		if (currentProvider !== lastProvider) {
			if (currentProvider) {
				fetchAvailableModels(currentProvider);
			} else {
				availableModels = [];
			}
			lastProvider = currentProvider;
		}
	});

	$effect(() => {
		if (!auth.token) {
			goto('/login');
			return;
		}
		if (auth.user && isLoading) {
			fetchProviders();
		}
	});

	async function fetchProviders() {
		const user = auth.user;
		if (!user?.id) return;
		try {
			providers = await apiFetch(`/llm/providers?user_id=${user.id}`);
		} catch (err) {
			console.error('Failed to fetch providers:', err);
		} finally {
			isLoading = false;
		}
	}

	function resetForm() {
		form = {
			provider_name: '',
			model_name: '',
			api_key: '',
			base_url: '',
			additional_params: ''
		};
		error = '';
		editingProviderId = null;
	}

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		const user = auth.user;
		if (!user?.id) return;

		isSubmitting = true;
		error = '';

		try {
			const payload = { ...form, user_id: user.id };
			if (editingProviderId) {
				const updated = await apiFetch(`/llm/providers/${editingProviderId}`, {
					method: 'PATCH',
					body: JSON.stringify(payload)
				});
				providers = providers.map((p) => (p.id === editingProviderId ? updated : p));
				successMessage = 'Update successful.';
			} else {
				const newProvider = await apiFetch('/llm/providers', {
					method: 'POST',
					body: JSON.stringify(payload)
				});
				providers = [newProvider, ...providers];
				successMessage = 'AI Model added.';
			}
			isAddingProvider = false;
			resetForm();
			setTimeout(() => (successMessage = ''), 3000);
		} catch (err: any) {
			error = err.message || 'Failed to load AI models.';
		} finally {
			isSubmitting = false;
		}
	}

	async function deleteProvider(id: number) {
		if (!confirm('Are you sure you want to remove this AI model?')) return;
		try {
			await apiFetch(`/llm/providers/${id}`, { method: 'DELETE' });
			providers = providers.filter((p) => p.id !== id);
		} catch (err) {
			console.error('Failed to remove provider:', err);
		}
	}

	async function copyApiKey(id: number) {
		try {
			const { api_key } = await apiFetch(`/llm/providers/${id}/key`);
			await navigator.clipboard.writeText(api_key);
			successMessage = 'API key copied to your clipboard.';
			setTimeout(() => (successMessage = ''), 3000);
		} catch (err: any) {
			error = 'Failed to retrieve the API key.';
		}
	}

	function startEdit(provider: Provider) {
		form = {
			provider_name: provider.provider_name,
			model_name: provider.model_name,
			api_key: '',
			base_url: provider.base_url || '',
			additional_params: provider.additional_params || ''
		};
		editingProviderId = provider.id;
		isAddingProvider = true;
	}

	function applyPreset(type: 'openai' | 'anthropic' | 'gemini' | 'openrouter') {
		const presets = {
			openai: { provider: 'OpenAI', model: 'gpt-4o', baseUrl: 'https://api.openai.com/v1' },
			anthropic: { provider: 'Anthropic', model: 'claude-3-5-sonnet-latest', baseUrl: '' },
			gemini: { provider: 'Gemini', model: 'gemini-1.5-pro', baseUrl: '' },
			openrouter: {
				provider: 'OpenRouter',
				model: 'google/gemini-2.0-flash-001',
				baseUrl: 'https://openrouter.ai/api/v1'
			}
		};
		const p = presets[type];
		form.provider_name = p.provider;
		form.model_name = p.model;
		form.base_url = p.baseUrl || '';

		if (type) {
			fetchAvailableModels(type);
		} else {
			availableModels = [];
		}
	}

	async function fetchAvailableModels(provider: string) {
		isFetchingModels = true;
		try {
			availableModels = await apiFetch(`/llm/models`);
		} catch (err) {
			console.error('Failed to fetch models:', err);
		} finally {
			isFetchingModels = false;
		}
	}
	import { Skeleton } from '$lib/components/ui/skeleton';
</script>

<div class="container mx-auto max-w-7xl space-y-12 p-6 lg:p-12">
	<!-- Header -->
	<header class="flex flex-col justify-between gap-8 pt-4 md:flex-row md:items-end">
		<div class="max-w-2xl space-y-4">
			<div
				class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-primary uppercase"
			>
				<Settings2 class="h-4 w-4" />
				<span>AI Configuration</span>
			</div>
			<h1
				class="font-display text-4xl leading-none font-black tracking-tighter text-white uppercase md:text-6xl"
			>
				AI <span class="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent"
					>Models</span
				>
			</h1>
			<p class="max-w-2xl font-sans text-lg leading-relaxed text-muted-foreground opacity-80">
				Configure the AI systems that power your learning experience. Add your API keys to get
				started.
			</p>
		</div>

		<Button
			onclick={() => {
				isAddingProvider = !isAddingProvider;
				if (!isAddingProvider) resetForm();
			}}
			variant={isAddingProvider ? 'outline' : 'default'}
			class="flex h-16 items-center gap-3 rounded-2xl px-10 font-black tracking-widest uppercase shadow-lg transition-all"
		>
			{#if isAddingProvider}
				<ChevronRight class="h-5 w-5 rotate-90 transition-transform" />
				Back to List
			{:else}
				<Plus class="h-5 w-5" />
				Add AI Model
			{/if}
		</Button>
	</header>

	{#if successMessage}
		<div
			transition:fade
			class="fixed top-24 left-1/2 z-50 mx-auto flex max-w-md -translate-x-1/2 items-center gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm font-bold text-emerald-400 shadow-2xl backdrop-blur-xl"
		>
			<CheckCircle2 class="h-4 w-4" />
			{successMessage}
		</div>
	{/if}

	{#if isAddingProvider}
		<section in:fly={{ y: 20, duration: 600 }} class="relative mx-auto max-w-3xl">
			<div class="absolute inset-0 -z-10 rounded-full bg-indigo-500/5 blur-[100px]"></div>
			<Card.Root
				class="overflow-hidden rounded-[2.5rem] border-white/10 bg-slate-900/40 shadow-2xl ring-1 ring-white/10 backdrop-blur-3xl"
			>
				<Card.Header class="border-b border-white/5 bg-white/2 p-10">
					<div class="flex items-center gap-4">
						<div class="rounded-2xl border border-indigo-500/20 bg-indigo-500/10 p-3">
							<Cpu class="h-6 w-6 text-indigo-400" />
						</div>
						<div>
							<Card.Title class="font-display text-3xl font-black text-white uppercase"
								>{editingProviderId ? 'Edit Model' : 'New AI Model'}</Card.Title
							>
							<Card.Description class="font-sans text-lg text-muted-foreground opacity-70"
								>Connect your preferred AI provider.</Card.Description
							>
						</div>
					</div>
				</Card.Header>

				<Card.Content class="space-y-10 p-10">
					{#if error}
						<div
							class="flex items-center gap-3 rounded-xl border border-red-500/20 bg-red-500/10 p-4 font-bold text-red-400"
						>
							<XCircle class="h-5 w-5" />
							{error}
						</div>
					{/if}

					{#if !editingProviderId}
						<div class="space-y-3">
							<Label class="ml-1 text-[10px] font-black tracking-widest text-slate-500 uppercase"
								>Speed Presets</Label
							>
							<div class="flex flex-wrap gap-3">
								{#each ['openai', 'anthropic', 'gemini', 'openrouter'] as preset}
									<button
										type="button"
										onclick={() => applyPreset(preset as any)}
										class="flex items-center gap-2 rounded-full border border-border bg-slate-900 px-5 py-2 text-xs font-bold text-white transition-all hover:border-primary/50 hover:bg-muted"
									>
										<Zap class="h-3 w-3 text-primary" />
										{preset.charAt(0).toUpperCase() + preset.slice(1)}
									</button>
								{/each}
							</div>
						</div>
					{/if}

					<form onsubmit={handleSubmit} class="space-y-8">
						<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
							<div class="space-y-3">
								<Label
									class="ml-1 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
									>AI Provider</Label
								>
								<Input
									bind:value={form.provider_name}
									placeholder="e.g. OpenAI"
									required
									class="h-14 rounded-xl border-border bg-background px-6 text-white"
								/>
							</div>
							<div class="space-y-3">
								<Label
									class="ml-1 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
									>Model Name</Label
								>
								{#if availableModels.length > 0}
									<div class="relative space-y-2" bind:this={dropdownRef}>
										<div class="relative w-full">
											<Search
												class="absolute top-1/2 left-4 h-4 w-4 -translate-y-1/2 text-muted-foreground transition-colors {isModelDropdownOpen
													? 'text-primary'
													: ''}"
											/>
											<Input
												value={isModelDropdownOpen
													? modelSearchQuery
													: availableModels.find((m) => m.name === form.model_name)?.display_name ||
														form.model_name}
												oninput={(e) => {
													modelSearchQuery = e.currentTarget.value;
													form.model_name = e.currentTarget.value;
													isModelDropdownOpen = true;
												}}
												onfocus={() => {
													isModelDropdownOpen = true;
													modelSearchQuery = form.model_name;
												}}
												placeholder="Search or enter model name..."
												class="h-14 w-full rounded-xl border-white/10 bg-white/5 pl-12 text-white shadow-sm ring-1 ring-white/5 transition-all focus:border-primary/50 focus:bg-slate-900/80 focus:ring-2 focus:ring-primary/50"
											/>
											{#if isModelDropdownOpen}
												<button
													type="button"
													class="absolute top-1/2 right-4 -translate-y-1/2"
													onclick={() => {
														isModelDropdownOpen = false;
													}}
												>
													<ChevronRight
														class="h-4 w-4 rotate-[-90deg] text-muted-foreground transition-all hover:text-white"
													/>
												</button>
											{:else}
												<div class="pointer-events-none absolute top-1/2 right-4 -translate-y-1/2">
													<ChevronRight class="h-4 w-4 rotate-90 text-muted-foreground" />
												</div>
											{/if}
										</div>

										{#if isModelDropdownOpen}
											<div
												transition:fly={{ y: -10, duration: 200 }}
												class="absolute z-50 mt-2 w-full overflow-hidden rounded-xl border border-white/10 bg-slate-950/90 shadow-2xl ring-1 ring-black/5 backdrop-blur-2xl"
											>
												<div
													class="scrollbar-thin scrollbar-track-transparent scrollbar-thumb-white/10 max-h-64 overflow-y-auto p-2"
												>
													{#if filteredModels.length === 0}
														<div class="p-6 text-center">
															<Terminal class="mx-auto mb-2 h-6 w-6 text-slate-600" />
															<p class="text-sm font-medium text-slate-400">No models found</p>
															<p class="text-xs text-slate-500">Press enter to use custom model</p>
														</div>
													{:else}
														<div class="grid gap-1">
															{#each filteredModels as model}
																<button
																	type="button"
																	onclick={() => {
																		form.model_name = model.name;
																		modelSearchQuery = '';
																		isModelDropdownOpen = false;
																	}}
																	class="flex w-full flex-col items-start gap-1 rounded-lg px-4 py-3 text-left transition-all hover:bg-white/10 {form.model_name ===
																	model.name
																		? 'bg-primary/20 ring-1 ring-primary/50'
																		: ''}"
																>
																	<div class="flex w-full items-center justify-between">
																		<span class="leading-none font-bold text-white"
																			>{model.display_name}</span
																		>
																		{#if form.model_name === model.name}
																			<CheckCircle2 class="h-3 w-3 text-primary" />
																		{/if}
																	</div>
																	<span class="font-mono text-[10px] text-slate-500"
																		>{model.name}</span
																	>
																</button>
															{/each}
														</div>
													{/if}
												</div>
												<div class="border-t border-white/5 bg-black/40 px-4 py-2">
													<p class="text-[10px] font-medium text-slate-500">
														Showing {filteredModels.length} of {availableModels.length} models
													</p>
												</div>
											</div>
										{/if}
									</div>
								{:else}
									<div class="relative">
										<Input
											bind:value={form.model_name}
											placeholder="e.g. gpt-4o"
											required
											class="h-14 rounded-xl border-border bg-background px-6 text-white"
										/>
										{#if isFetchingModels}
											<div class="absolute top-0 right-4 flex h-full items-center">
												<Loader2 class="h-4 w-4 animate-spin text-primary" />
											</div>
										{/if}
									</div>
								{/if}
							</div>
						</div>

						<div class="space-y-3">
							<Label
								class="ml-1 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
								>API Key</Label
							>
							<Input
								type="password"
								bind:value={form.api_key}
								placeholder={editingProviderId ? '••••••••' : 'sk-...'}
								required={!editingProviderId}
								class="h-14 rounded-xl border-border bg-background px-6 text-white"
							/>
						</div>

						<div class="space-y-3">
							<Label
								class="ml-1 text-[10px] font-black tracking-widest text-muted-foreground uppercase"
								>Base URL (Optional)</Label
							>
							<Input
								bind:value={form.base_url}
								placeholder="https://api.openai.com/v1"
								class="h-14 rounded-xl border-border bg-background px-6 text-white"
							/>
						</div>

						<div class="flex gap-4 pt-4">
							<Button
								variant="ghost"
								type="button"
								onclick={() => {
									isAddingProvider = false;
									resetForm();
								}}
								class="h-14 flex-1 rounded-xl font-bold">Cancel</Button
							>
							<Button
								type="submit"
								variant="default"
								disabled={isSubmitting}
								class="h-14 flex-1 rounded-xl font-black"
							>
								{#if isSubmitting}
									<Loader2 class="mr-2 h-4 w-4 animate-spin" />
									Saving...
								{:else}
									{editingProviderId ? 'Update Model' : 'Save Model'}
								{/if}
							</Button>
						</div>
					</form>
				</Card.Content>
			</Card.Root>
		</section>
	{:else}
		<section class="space-y-8">
			<div class="flex items-center justify-between border-b border-white/5 pb-4">
				<h2
					class="font-syne flex items-center gap-3 text-2xl font-black tracking-tight text-white uppercase"
				>
					<Globe class="h-6 w-6 text-indigo-400" />
					Active Models
				</h2>
				<span
					class="rounded-full bg-white/5 px-4 py-2 text-[10px] font-black tracking-widest text-slate-500 uppercase"
				>
					{providers.length} Registered
				</span>
			</div>

			{#if isLoading}
				<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
					{#each Array(3) as _}
						<div
							class="flex h-[320px] flex-col justify-between space-y-8 rounded-[2rem] border border-white/5 bg-slate-950/40 p-8"
						>
							<div class="space-y-6">
								<div class="flex items-start justify-between">
									<Skeleton class="h-14 w-14 rounded-2xl" />
									<div class="flex gap-2">
										<Skeleton class="h-8 w-8 rounded-lg" />
										<Skeleton class="h-8 w-8 rounded-lg" />
									</div>
								</div>
								<div class="space-y-3">
									<Skeleton class="h-8 w-1/2" />
									<Skeleton class="h-3 w-1/3" />
								</div>
							</div>
							<div class="space-y-4">
								<Skeleton class="h-10 w-full rounded-xl" />
								<Skeleton class="h-10 w-full rounded-xl" />
							</div>
						</div>
					{/each}
				</div>
			{:else if providers.length === 0}
				<div
					class="space-y-8 rounded-[3rem] border-2 border-dashed border-white/5 bg-slate-900/20 py-32 text-center"
					in:scale
				>
					<div
						class="mx-auto flex h-24 w-24 items-center justify-center rounded-full border border-white/10 bg-slate-950"
					>
						<Terminal class="h-10 w-10 text-slate-700" />
					</div>
					<div class="mx-auto max-w-sm space-y-3">
						<h3 class="text-2xl font-bold text-white uppercase">No AI Models Ready</h3>
						<p class="font-serif text-slate-500 italic">
							Add an AI provider to start generating study materials.
						</p>
					</div>
					<Button
						onclick={() => (isAddingProvider = true)}
						variant="outline"
						class="rounded-xl border-indigo-500/50 px-8 text-indigo-400">Add First Model</Button
					>
				</div>
			{:else}
				<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
					{#each providers as provider, i (provider.id)}
						<div in:fly={{ y: 20, delay: i * 100 }}>
							<Card.Root
								class="group relative flex h-full flex-col overflow-hidden rounded-[2rem] border-white/5 bg-slate-950/40 shadow-xl ring-1 ring-white/10 transition-all duration-500 hover:bg-slate-900/60 hover:ring-indigo-500/30"
							>
								<Card.Header class="p-8 pb-4">
									<div class="mb-6 flex items-start justify-between">
										<div
											class="rounded-xl bg-indigo-500/10 p-4 transition-transform group-hover:scale-110"
										>
											<Cpu class="h-6 w-6 text-indigo-400" />
										</div>
										<div class="flex items-center gap-1">
											<Button
												variant="ghost"
												size="icon"
												onclick={() => copyApiKey(provider.id)}
												class="rounded-lg text-slate-600 hover:text-indigo-400"
												title="Copy API Key"><Copy class="h-4 w-4" /></Button
											>
											<Button
												variant="ghost"
												size="icon"
												onclick={() => startEdit(provider)}
												class="rounded-lg text-slate-600 hover:text-white"
												><Settings2 class="h-4 w-4" /></Button
											>
											<Button
												variant="ghost"
												size="icon"
												onclick={() => deleteProvider(provider.id)}
												class="rounded-lg text-slate-600 hover:text-red-400"
												><Trash2 class="h-4 w-4" /></Button
											>
										</div>
									</div>
									<div class="space-y-1">
										<Card.Title class="font-syne text-2xl font-black text-white"
											>{provider.provider_name}</Card.Title
										>
										<div class="flex items-center gap-2">
											<div class="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500"></div>
											<span class="text-[10px] font-black tracking-widest text-slate-500 uppercase"
												>{provider.model_name}</span
											>
										</div>
									</div>
								</Card.Header>

								<Card.Content class="flex-grow p-8 pt-4">
									<div class="space-y-4">
										<div
											class="flex items-center gap-3 truncate rounded-xl bg-white/2 p-3 text-xs font-medium text-slate-400"
										>
											<Globe class="h-3 w-3 text-slate-600" />
											{provider.base_url || 'Default API Endpoint'}
										</div>
										<div
											class="flex items-center gap-3 rounded-xl bg-white/2 p-3 text-xs font-medium text-slate-400"
										>
											<ShieldCheck class="h-3 w-3 text-emerald-500/50" />
											API Key Encrypted
										</div>
									</div>
								</Card.Content>
							</Card.Root>
						</div>
					{/each}
				</div>
			{/if}
		</section>
	{/if}
</div>

<style>
	.font-display {
		font-family: var(--font-display);
	}
	.font-sans {
		font-family: var(--font-sans);
	}
</style>
