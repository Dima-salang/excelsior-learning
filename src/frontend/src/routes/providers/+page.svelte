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
		Terminal
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
			error = err.message || 'Failed to save AI model. Check your settings.';
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

	function applyPreset(type: 'openai' | 'anthropic' | 'gemini') {
		const presets = {
			openai: { provider: 'OpenAI', model: 'gpt-4o' },
			anthropic: { provider: 'Anthropic', model: 'claude-3-5-sonnet-latest' },
			gemini: { provider: 'Gemini', model: 'gemini-1.5-pro' }
		};
		const p = presets[type];
		form.provider_name = p.provider;
		form.model_name = p.model;
	}
	import { Skeleton } from '$lib/components/ui/skeleton';
</script>

<div class="container mx-auto max-w-7xl space-y-12 p-6 lg:p-12">

	<!-- Header -->
	<header class="flex flex-col md:flex-row md:items-end justify-between gap-8 pt-4">
		<div class="max-w-2xl space-y-4">
			<div class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-primary uppercase">
				<Settings2 class="h-4 w-4" />
				<span>AI Configuration</span>
			</div>
			<h1 class="font-display text-4xl md:text-6xl font-black tracking-tighter text-white leading-none uppercase">
				AI <span class="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Models</span>
			</h1>
			<p class="font-sans text-lg text-muted-foreground leading-relaxed max-w-2xl opacity-80">
				Configure the AI brains that power your learning experience. Add your API keys to get started.
			</p>
		</div>

		<Button
			onclick={() => {
				isAddingProvider = !isAddingProvider;
				if (!isAddingProvider) resetForm();
			}}
			variant={isAddingProvider ? "outline" : "default"}
			class="h-16 px-10 rounded-2xl font-black tracking-widest uppercase transition-all shadow-lg flex items-center gap-3"
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
		<div transition:fade class="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-bold flex items-center gap-3 mx-auto max-w-md shadow-2xl backdrop-blur-xl fixed top-24 left-1/2 -translate-x-1/2 z-50">
			<CheckCircle2 class="h-4 w-4" />
			{successMessage}
		</div>
	{/if}

	{#if isAddingProvider}
		<section in:fly={{ y: 20, duration: 600 }} class="max-w-3xl mx-auto relative">
			<div class="absolute -z-10 inset-0 bg-indigo-500/5 blur-[100px] rounded-full"></div>
			<Card.Root class="rounded-[2.5rem] border-white/10 bg-slate-900/40 backdrop-blur-3xl shadow-2xl ring-1 ring-white/10 overflow-hidden">
				<Card.Header class="p-10 border-b border-white/5 bg-white/2">
					<div class="flex items-center gap-4">
						<div class="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
							<Cpu class="h-6 w-6 text-indigo-400" />
						</div>
						<div>
							<Card.Title class="font-display text-3xl font-black text-white uppercase">{editingProviderId ? 'Edit Model' : 'New AI Model'}</Card.Title>
							<Card.Description class="font-sans text-lg text-muted-foreground opacity-70">Configure access to an AI service provider.</Card.Description>
						</div>
					</div>
				</Card.Header>

				<Card.Content class="p-10 space-y-10">
					{#if error}
						<div class="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 font-bold flex items-center gap-3">
							<XCircle class="h-5 w-5" />
							{error}
						</div>
					{/if}

					{#if !editingProviderId}
						<div class="space-y-3">
							<Label class="text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">Speed Presets</Label>
							<div class="flex flex-wrap gap-3">
								{#each ['openai', 'anthropic', 'gemini'] as preset}
									<button 
										onclick={() => applyPreset(preset as any)}
										class="px-5 py-2 rounded-full bg-slate-900 border border-border text-xs font-bold text-white hover:bg-muted hover:border-primary/50 transition-all flex items-center gap-2"
									>
										<Zap class="w-3 h-3 text-primary" />
										{preset.charAt(0).toUpperCase() + preset.slice(1)}
									</button>
								{/each}
							</div>
						</div>
					{/if}

					<form onsubmit={handleSubmit} class="space-y-8">
						<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
							<div class="space-y-3">
								<Label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">AI Provider</Label>
								<Input bind:value={form.provider_name} placeholder="e.g. OpenAI" required class="h-14 bg-background border-border rounded-xl px-6 text-white" />
							</div>
							<div class="space-y-3">
								<Label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">Model Name</Label>
								<Input bind:value={form.model_name} placeholder="e.g. gpt-4o" required class="h-14 bg-background border-border rounded-xl px-6 text-white" />
							</div>
						</div>

						<div class="space-y-3">
							<Label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">API Key</Label>
							<Input type="password" bind:value={form.api_key} placeholder={editingProviderId ? '••••••••' : 'sk-...'} required={!editingProviderId} class="h-14 bg-background border-border rounded-xl px-6 text-white" />
						</div>

						<div class="space-y-3">
							<Label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1">Base URL (Optional)</Label>
							<Input bind:value={form.base_url} placeholder="https://api.openai.com/v1" class="h-14 bg-background border-border rounded-xl px-6 text-white" />
						</div>

						<div class="flex gap-4 pt-4">
							<Button variant="ghost" type="button" onclick={() => { isAddingProvider = false; resetForm(); }} class="flex-1 h-14 rounded-xl font-bold">Cancel</Button>
							<Button type="submit" variant="default" disabled={isSubmitting} class="flex-1 h-14 font-black rounded-xl">
								{#if isSubmitting}
									<Loader2 class="w-4 h-4 animate-spin mr-2" />
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
				<h2 class="text-2xl font-black text-white uppercase tracking-tight font-syne flex items-center gap-3">
					<Globe class="h-6 w-6 text-indigo-400" />
					Active Models
				</h2>
				<span class="text-[10px] bg-white/5 px-4 py-2 rounded-full font-black text-slate-500 uppercase tracking-widest">
					{providers.length} Registered
				</span>
			</div>

			{#if isLoading}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {#each Array(3) as _}
                        <div class="rounded-[2rem] border border-white/5 bg-slate-950/40 p-8 h-[320px] space-y-8 flex flex-col justify-between">
                            <div class="space-y-6">
                                <div class="flex justify-between items-start">
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
				<div class="py-32 text-center bg-slate-900/20 border-2 border-dashed border-white/5 rounded-[3rem] space-y-8" in:scale>
					<div class="bg-slate-950 rounded-full h-24 w-24 flex items-center justify-center mx-auto border border-white/10">
						<Terminal class="h-10 w-10 text-slate-700" />
					</div>
					<div class="max-w-sm mx-auto space-y-3">
						<h3 class="text-2xl font-bold text-white uppercase">No AI Models Ready</h3>
						<p class="text-slate-500 font-serif italic">Add an AI provider to start generating course content.</p>
					</div>
					<Button onclick={() => isAddingProvider = true} variant="outline" class="rounded-xl border-indigo-500/50 text-indigo-400 px-8">Add First Model</Button>
				</div>
			{:else}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
					{#each providers as provider, i (provider.id)}
						<div in:fly={{ y: 20, delay: i * 100 }}>
							<Card.Root class="group relative rounded-[2rem] border-white/5 bg-slate-950/40 hover:bg-slate-900/60 ring-1 ring-white/10 hover:ring-indigo-500/30 transition-all duration-500 overflow-hidden shadow-xl h-full flex flex-col">
								<Card.Header class="p-8 pb-4">
									<div class="flex items-start justify-between mb-6">
										<div class="p-4 rounded-xl bg-indigo-500/10 group-hover:scale-110 transition-transform">
											<Cpu class="h-6 w-6 text-indigo-400" />
										</div>
										<div class="flex items-center gap-1">
											<Button variant="ghost" size="icon" onclick={() => startEdit(provider)} class="text-slate-600 hover:text-white rounded-lg"><Settings2 class="w-4 h-4" /></Button>
											<Button variant="ghost" size="icon" onclick={() => deleteProvider(provider.id)} class="text-slate-600 hover:text-red-400 rounded-lg"><Trash2 class="w-4 h-4" /></Button>
										</div>
									</div>
									<div class="space-y-1">
										<Card.Title class="text-2xl font-black text-white font-syne">{provider.provider_name}</Card.Title>
										<div class="flex items-center gap-2">
											<div class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
											<span class="text-[10px] font-black text-slate-500 uppercase tracking-widest">{provider.model_name}</span>
										</div>
									</div>
								</Card.Header>

								<Card.Content class="p-8 pt-4 flex-grow">
									<div class="space-y-4">
										<div class="p-3 bg-white/2 rounded-xl text-xs text-slate-400 font-medium truncate flex items-center gap-3">
											<Globe class="w-3 h-3 text-slate-600" />
											{provider.base_url || 'Default API Endpoint'}
										</div>
										<div class="p-3 bg-white/2 rounded-xl text-xs text-slate-400 font-medium flex items-center gap-3">
											<ShieldCheck class="w-3 h-3 text-emerald-500/50" />
											API Key Encrypted
										</div>
									</div>
								</Card.Content>

								<Card.Footer class="p-6 bg-white/2 border-t border-white/5">
									<Button variant="ghost" class="w-full text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] group-hover:text-white transition-colors">Configure Details</Button>
								</Card.Footer>
							</Card.Root>
						</div>
					{/each}
				</div>
			{/if}
		</section>
	{/if}
</div>

<style>
	.font-display { font-family: var(--font-display); }
	.font-sans { font-family: var(--font-sans); }
</style>
