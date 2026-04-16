<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { settings } from '$lib/stores/settings.svelte';
	import { MessageCircle, Plus, Cpu, CalendarDays } from '@lucide/svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import ChatSession from '$lib/components/ChatSession.svelte';

	interface Provider {
		id: number;
		provider_name: string;
		model_name: string;
	}

	interface ChatInfo {
		id: number;
		title: string;
		updated_at: string;
	}

	let providers = $state<Provider[]>([]);
	let chats = $state<ChatInfo[]>([]);
	let activeChatId = $state<number | null>(null);
	let isLoading = $state(true);

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
			const [providersData, chatsData] = await Promise.all([
				apiFetch(`/llm/providers?user_id=${user.id}`),
				apiFetch(`/chat/conversations/${user.id}`)
			]);
			providers = providersData || [];
			chats = Array.isArray(chatsData) ? chatsData : [];

			if (providers.length > 0 && !settings.selectedProviderId) {
				settings.setProvider(providers[0].id);
			}

			// If no active chat, and there are chats in list, maybe keep it null for 'New Chat'
		} catch (err) {
			console.error('Failed to fetch data:', err);
		} finally {
			isLoading = false;
		}
	}

	function startNewChat() {
		activeChatId = null;
	}

	function selectChat(id: number) {
		activeChatId = id;
	}

	// Called by ChatSession when a chat is deleted or when we should refresh the list
	async function refreshChatList() {
		const user = auth.user;
		if (!user?.id) return;
		try {
			const chatsData = await apiFetch(`/chat/conversations/${user.id}`);
			chats = Array.isArray(chatsData) ? chatsData : [];
		} catch (err) {}
	}

	// Watch activeChatId changes to refresh list in case title changes or deleted
	// (we can also manually trigger this)
	$effect(() => {
		if (activeChatId) {
			refreshChatList();
		}
	});
</script>

<svelte:head>
	<title>AI Tutor Chat — Excelsior</title>
</svelte:head>

<div class="flex h-[calc(100vh-73px)] overflow-hidden bg-background">
	<!-- Left Sidebar: Chat List -->
	<aside
		class="flex hidden w-72 flex-col border-r border-border bg-card/40 backdrop-blur-3xl md:flex"
	>
		<div class="flex items-center justify-between border-b border-border p-4">
			<Button
				onclick={startNewChat}
				variant="outline"
				class="flex w-full justify-center gap-2 rounded-xl border-indigo-500/30 bg-indigo-500/10 font-black tracking-widest text-indigo-400 uppercase hover:bg-indigo-500/20 hover:text-indigo-300"
			>
				<Plus class="h-4 w-4" />
				New Chat
			</Button>
		</div>

		<div class="border-b border-border p-4">
			<div class="relative">
				<select
					bind:value={settings.selectedProviderId}
					onchange={() => settings.setProvider(Number(settings.selectedProviderId))}
					class="h-10 w-full cursor-pointer appearance-none rounded-xl border border-border bg-secondary px-3 pr-8 text-[10px] font-bold text-foreground shadow-lg transition-all outline-none focus:ring-1 focus:ring-primary"
				>
					{#if providers.length === 0}
						<option value={null} class="bg-card text-foreground">No models</option>
					{/if}
					{#each providers as p}
						<option value={p.id} class="bg-card text-foreground"
							>{p.provider_name} — {p.model_name}</option
						>
					{/each}
				</select>
				<Cpu
					class="pointer-events-none absolute top-1/2 right-2.5 h-3 w-3 -translate-y-1/2 text-muted-foreground"
				/>
			</div>
		</div>

		<div class="custom-scrollbar flex-1 space-y-2 overflow-y-auto p-4">
			<div
				class="mb-4 flex items-center gap-2 text-[10px] font-black tracking-widest text-slate-600 uppercase"
			>
				<CalendarDays class="h-3 w-3" />
				Recent Conversations
			</div>

			{#if chats.length === 0 && !isLoading}
				<div class="py-10 text-center text-xs font-bold text-slate-600">No past conversations</div>
			{:else}
				{#each chats as chat}
					<button
						onclick={() => selectChat(chat.id)}
						class="w-full rounded-xl border p-3 text-left transition-all {activeChatId === chat.id
							? 'border-primary/20 bg-primary/10 text-primary-foreground'
							: 'border-transparent text-slate-400 hover:bg-white/5 hover:text-slate-300'}"
					>
						<p class="truncate text-xs font-bold">{chat.title}</p>
						<p class="mt-1 flex items-center text-[9px] font-bold text-slate-600">
							{new Date(chat.updated_at).toLocaleDateString()}
						</p>
					</button>
				{/each}
			{/if}
		</div>
	</aside>

	<!-- Main Chat View -->
	<main class="relative flex flex-1 flex-col bg-background">
		{#if isLoading}
			<div class="flex h-full items-center justify-center">
				<div
					class="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent"
				></div>
			</div>
		{:else}
			{#key activeChatId}
				<ChatSession
					bind:chatId={activeChatId}
					{providers}
					onChatDeleted={() => {
						startNewChat();
						refreshChatList();
					}}
				/>
			{/key}
		{/if}
	</main>
</div>

<style>
	.custom-scrollbar::-webkit-scrollbar {
		width: 4px;
	}
	.custom-scrollbar::-webkit-scrollbar-track {
		background: transparent;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.05);
		border-radius: 10px;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb:hover {
		background: rgba(255, 255, 255, 0.1);
	}
</style>
