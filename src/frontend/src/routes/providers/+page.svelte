<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import {
		Plus,
		Trash2,
		Settings2,
		Cpu,
		Globe,
		Loader2,
		ShieldCheck,
		Zap,
		ChevronRight,
		CheckCircle2,
		XCircle,
		Search
	} from 'lucide-svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

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

	let dropdownRef = $state<HTMLElement | null>(null);
	onMount(() => {
		const handleClickOutside = (e: MouseEvent) => {
			if (dropdownRef && !dropdownRef.contains(e.target as Node)) {
				isModelDropdownOpen = false;
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
		form = { provider_name: '', model_name: '', api_key: '', base_url: '', additional_params: '' };
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
		fetchAvailableModels(type);
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
</script>

<div class="container mx-auto max-w-6xl space-y-8 p-6 py-12">
	<header class="flex flex-col justify-between gap-6 md:flex-row md:items-end">
		<div class="space-y-2">
			<div class="flex items-center gap-2">
				<div class="rounded-lg bg-primary/10 p-2">
					<Settings2 class="h-5 w-5 text-primary" />
				</div>
				<span class="text-sm font-medium text-muted-foreground">AI Configuration</span>
			</div>
			<h1 class="text-3xl font-bold tracking-tight md:text-4xl">
				AI <span class="text-primary">Models</span>
			</h1>
			<p class="text-muted-foreground">
				Configure the AI systems that power your learning experience.
			</p>
		</div>

		<Button
			onclick={() => {
				isAddingProvider = !isAddingProvider;
				if (!isAddingProvider) resetForm();
			}}
			variant={isAddingProvider ? 'outline' : 'default'}
		>
			{#if isAddingProvider}
				<ChevronRight class="mr-2 h-4 w-4 rotate-90" />
				Back to List
			{:else}
				<Plus class="mr-2 h-4 w-4" />
				Add AI Model
			{/if}
		</Button>
	</header>

	{#if successMessage}
		<div
			transition:fade
			class="fixed top-24 left-1/2 z-50 mx-auto flex max-w-sm -translate-x-1/2 items-center gap-2 rounded-lg border border-green-500/20 bg-green-500/10 p-4 text-sm text-green-600 dark:text-green-400"
		>
			<CheckCircle2 class="h-4 w-4" />
			{successMessage}
		</div>
	{/if}

	{#if isAddingProvider}
		<section in:fly={{ y: 20, duration: 400 }}>
			<Card.Root class="overflow-hidden rounded-xl border-border">
				<Card.Header class="border-b border-border bg-muted/50">
					<div class="flex items-center gap-4">
						<div class="rounded-lg bg-primary/10 p-2">
							<Cpu class="h-5 w-5 text-primary" />
						</div>
						<div>
							<Card.Title>{editingProviderId ? 'Edit Model' : 'New AI Model'}</Card.Title>
							<Card.Description>Connect your preferred AI provider.</Card.Description>
						</div>
					</div>
				</Card.Header>

				<Card.Content class="space-y-6 p-6">
					{#if error}
						<div
							class="flex items-center gap-3 rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive"
						>
							<XCircle class="h-4 w-4" />
							{error}
						</div>
					{/if}

					{#if !editingProviderId}
						<div class="space-y-3">
							<Label class="text-sm font-medium">Quick Presets</Label>
							<div class="flex flex-wrap gap-2">
								{#each ['openai', 'anthropic', 'gemini', 'openrouter'] as preset}
									<button
										type="button"
										onclick={() => applyPreset(preset as any)}
										class="flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:border-primary/50 hover:bg-muted"
									>
										<Zap class="h-3 w-3 text-primary" />
										{preset.charAt(0).toUpperCase() + preset.slice(1)}
									</button>
								{/each}
							</div>
						</div>
					{/if}

					<form onsubmit={handleSubmit} class="space-y-5">
						<div class="grid gap-5 md:grid-cols-2">
							<div class="space-y-2">
								<Label for="provider_name" class="text-sm font-medium">AI Provider</Label>
								<Input
									id="provider_name"
									bind:value={form.provider_name}
									placeholder="e.g. OpenAI"
									required
								/>
							</div>
							<div class="space-y-2">
								<Label for="model_name" class="text-sm font-medium">Model Name</Label>
								<Input
									id="model_name"
									bind:value={form.model_name}
									placeholder="e.g. gpt-4o"
									required
								/>
							</div>
						</div>

						<div class="space-y-2">
							<Label for="api_key" class="text-sm font-medium">API Key</Label>
							<Input
								id="api_key"
								type="password"
								bind:value={form.api_key}
								placeholder={editingProviderId ? 'Leave blank to keep current' : 'sk-...'}
								required={!editingProviderId}
							/>
						</div>

						<div class="space-y-2">
							<Label for="base_url" class="text-sm font-medium">Base URL (Optional)</Label>
							<Input
								id="base_url"
								bind:value={form.base_url}
								placeholder="https://api.openai.com/v1"
							/>
						</div>

						<div class="flex gap-4">
							<Button
								type="button"
								variant="outline"
								onclick={() => {
									isAddingProvider = false;
									resetForm();
								}}
								class="flex-1"
							>
								Cancel
							</Button>
							<Button type="submit" disabled={isSubmitting} class="flex-1">
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
		<section class="space-y-6">
			<div class="flex items-center justify-between">
				<h2 class="flex items-center gap-2 text-lg font-semibold">
					<Globe class="h-5 w-5 text-primary" />
					Active Models
				</h2>
				<span class="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
					{providers.length} Registered
				</span>
			</div>

			{#if isLoading}
				<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
					{#each Array(3) as _}
						<div class="rounded-xl border border-border bg-card p-6">
							<div class="space-y-4">
								<div class="flex items-start justify-between">
									<Skeleton class="h-12 w-12 rounded-lg" />
									<div class="flex gap-2">
										<Skeleton class="h-8 w-8 rounded-lg" />
										<Skeleton class="h-8 w-8 rounded-lg" />
									</div>
								</div>
								<div class="space-y-2">
									<Skeleton class="h-6 w-1/2" />
									<Skeleton class="h-4 w-1/3" />
								</div>
							</div>
						</div>
					{/each}
				</div>
			{:else if providers.length === 0}
				<div
					class="flex flex-col items-center justify-center space-y-4 rounded-xl border border-dashed border-border bg-muted/30 py-16 text-center"
					in:scale
				>
					<div class="rounded-full bg-muted p-4">
						<Cpu class="h-8 w-8 text-muted-foreground" />
					</div>
					<div class="space-y-1">
						<h3 class="font-semibold">No AI Models Ready</h3>
						<p class="text-sm text-muted-foreground">Add an AI provider to get started.</p>
					</div>
					<Button onclick={() => (isAddingProvider = true)} variant="outline" size="sm">
						Add First Model
					</Button>
				</div>
			{:else}
				<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
					{#each providers as provider, i (provider.id)}
						<div in:fly={{ y: 10, delay: i * 50 }}>
							<Card.Root class="flex h-full flex-col transition-all hover:border-primary/30">
								<Card.Header class="p-6 pb-4">
									<div class="flex items-start justify-between">
										<div class="rounded-lg bg-primary/10 p-3">
											<Cpu class="h-5 w-5 text-primary" />
										</div>
										<div class="flex gap-1">
											<Button
												variant="ghost"
												size="icon"
												onclick={() => copyApiKey(provider.id)}
												title="Copy API Key"
											>
												<Globe class="h-4 w-4" />
											</Button>
											<Button variant="ghost" size="icon" onclick={() => startEdit(provider)}>
												<Settings2 class="h-4 w-4" />
											</Button>
											<Button
												variant="ghost"
												size="icon"
												onclick={() => deleteProvider(provider.id)}
												class="text-destructive hover:text-destructive"
											>
												<Trash2 class="h-4 w-4" />
											</Button>
										</div>
									</div>
									<Card.Title class="mt-4 text-lg">{provider.provider_name}</Card.Title>
									<div class="mt-1 flex items-center gap-2">
										<div class="h-2 w-2 animate-pulse rounded-full bg-green-500"></div>
										<span class="text-xs font-medium text-muted-foreground"
											>{provider.model_name}</span
										>
									</div>
								</Card.Header>

								<Card.Content class="flex-grow p-6 pt-0">
									<div class="space-y-3">
										<div
											class="flex items-center gap-2 rounded-lg border border-border bg-muted/50 p-3 text-xs"
										>
											<Globe class="h-3 w-3 text-muted-foreground" />
											<span class="truncate text-muted-foreground">
												{provider.base_url || 'Default API Endpoint'}
											</span>
										</div>
										<div
											class="flex items-center gap-2 rounded-lg border border-border bg-muted/50 p-3 text-xs"
										>
											<ShieldCheck class="h-3 w-3 text-green-500" />
											<span class="text-muted-foreground">API Key Encrypted</span>
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
