<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { apiFetch, API_BASE_URL } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { settings } from '$lib/stores/settings.svelte';
	import { MessageCircle, Send, Loader2, BrainCircuit, User, Cpu, Trash2 } from '@lucide/svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { marked } from 'marked';
	import markedKatex from 'marked-katex-extension';
	import 'katex/dist/katex.min.css';
	import { tick } from 'svelte';

	interface ChatMessage {
		role: 'user' | 'assistant' | 'system';
		content: string;
	}

	interface Provider {
		id: number;
		provider_name: string;
		model_name: string;
	}

	let {
		chatId = $bindable(null),
		lectureId = null,
		lectureContext = null,
		providers = [] as Provider[],
		onChatDeleted = () => {}
	} = $props<{
		chatId: number | null;
		lectureId?: number | null;
		lectureContext?: string | null;
		providers?: Provider[];
		onChatDeleted?: () => void;
	}>();

	let messages = $state<ChatMessage[]>([]);
	let prompt = $state('');
	let isGenerating = $state(false);
	let error = $state('');
	let isLoadingHistory = $state(false);
	let chatContainer: HTMLElement;

	marked.use(markedKatex({ throwOnError: false }));

	$effect(() => {
		if (chatId) {
			fetchHistory(chatId);
		} else {
			messages = [];
		}
	});

	async function fetchHistory(id: number) {
		const user = auth.user;
		if (!user?.id) return;
		isLoadingHistory = true;
		try {
			const msgs = await apiFetch(`/chat/conversation/${id}/messages?user_id=${user.id}`);
			messages = Array.isArray(msgs) ? msgs.map((m) => ({ role: m.role, content: m.content })) : [];
			await scrollToBottom();
		} catch (err) {
			console.error('Failed to load chat history', err);
		} finally {
			isLoadingHistory = false;
		}
	}

	async function scrollToBottom() {
		await tick();
		if (chatContainer) {
			chatContainer.scrollTo({
				top: chatContainer.scrollHeight,
				behavior: 'smooth'
			});
		}
	}

	async function handleSubmit(e?: SubmitEvent) {
		e?.preventDefault();
		if (!prompt.trim() || isGenerating || !settings.selectedProviderId) return;

		const user = auth.user;
		if (!user?.id) return;

		const currentPrompt = prompt.trim();
		prompt = '';

		let currentChatId = chatId;

		if (!currentChatId) {
			try {
				const title =
					currentPrompt.length > 30 ? currentPrompt.substring(0, 30) + '...' : currentPrompt;
				const params = new URLSearchParams({
					user_id: user.id.toString(),
					title: title
				});
				if (lectureId) params.append('lecture_id', lectureId.toString());

				const newChat = await apiFetch(`/chat/conversation?${params.toString()}`, {
					method: 'POST'
				});
				currentChatId = newChat.id;
				chatId = currentChatId;
			} catch (err: any) {
				error = 'Failed to create chat session';
				return;
			}
		}

		if (!currentChatId) return;

		const userMessage: ChatMessage = { role: 'user', content: currentPrompt };
		messages = [...messages, userMessage];

		error = '';
		isGenerating = true;
		await scrollToBottom();

		try {
			await apiFetch(`/chat/conversation/${currentChatId}/messages`, {
				method: 'POST',
				body: JSON.stringify({
					user_id: user.id,
					role: 'user',
					content: currentPrompt
				})
			});

			const chat_history = messages.slice(0, -1).map((m) => ({
				role: m.role,
				content: m.content
			}));

			if (lectureContext && chat_history.length === 0) {
				chat_history.unshift({ role: 'system', content: `Context:\n${lectureContext}` });
			}

			const response = await fetch(`${API_BASE_URL}/chat/conversation/${currentChatId}/generate`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${auth.token}`
				},
				body: JSON.stringify({
					user_id: user.id,
					user_prompt: currentPrompt,
					provider_id: settings.selectedProviderId,
					chat_history: chat_history.length > 0 ? chat_history : null
				})
			});

			if (!response.ok || !response.body) {
				throw new Error('Failed to generate response.');
			}

			const asstMessage: ChatMessage = { role: 'assistant', content: '' };
			messages = [...messages, asstMessage];

			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let done = false;

			while (!done) {
				const { value, done: readerDone } = await reader.read();
				done = readerDone;
				if (value) {
					const chunkStr = decoder.decode(value, { stream: true });
					const lines = chunkStr.split('\n');
					for (const line of lines) {
						if (line.startsWith('data: ')) {
							const data = line.slice(6);
							if (data === '[DONE]') {
								done = true;
								break;
							} else if (data.startsWith('[ERROR]')) {
								error = data.slice(7).trim();
								break;
							} else {
								messages[messages.length - 1].content += data;
							}
						}
					}
					messages = [...messages];
					await scrollToBottom();
				}
			}
		} catch (err: any) {
			error = err.message || 'Failed to get a response.';
		} finally {
			isGenerating = false;
			await scrollToBottom();
		}
	}

	async function clearChat() {
		if (chatId) {
			try {
				await apiFetch(`/chat/conversation/${chatId}`, { method: 'DELETE' });
				chatId = null;
				messages = [];
				onChatDeleted();
			} catch (err) {
				console.error('Failed to clear chat', err);
			}
		} else {
			messages = [];
		}
	}

	function renderMarkdown(content: string): string {
		if (!content) return '';
		return marked.parse(content, { breaks: true, gfm: true }) as string;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSubmit();
		}
	}
</script>

<div class="flex flex-1 flex-col overflow-hidden bg-transparent">
	<!-- Header -->
	<header class="relative z-10 flex items-center justify-between border-b border-border bg-card/60 px-4 py-3 backdrop-blur-2xl md:px-6">
		<div class="flex items-center gap-3">
			<div class="rounded-xl border border-primary/20 bg-primary/10 p-2">
				<MessageCircle class="h-4 w-4 text-primary" />
			</div>
			<div>
				<h2 class="font-display text-lg font-black tracking-tighter uppercase text-foreground">Tutor Chat</h2>
			</div>
		</div>
		<div class="flex items-center gap-2">
			{#if messages.length > 0}
				<Button
					variant="ghost"
					onclick={clearChat}
					class="h-8 rounded-lg px-2 text-[10px] font-black tracking-widest text-muted-foreground uppercase hover:bg-destructive/10 hover:text-destructive"
				>
					<Trash2 class="h-3.5 w-3.5" />
				</Button>
			{/if}
		</div>
	</header>

	<!-- Chat Area -->
	<div bind:this={chatContainer} class="custom-scrollbar relative flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-6 md:px-6">
		{#if isLoadingHistory}
			<div class="flex flex-1 items-center justify-center">
				<Loader2 class="h-6 w-6 animate-spin text-primary" />
			</div>
		{:else if messages.length === 0}
			<div class="flex flex-1 flex-col items-center justify-center space-y-6" in:scale={{ duration: 400, start: 0.95 }}>
				<div class="relative">
					<div class="absolute inset-0 animate-pulse rounded-full bg-primary/10 blur-[40px]"></div>
					<div class="relative rounded-3xl border border-border bg-card/60 p-8 backdrop-blur-xl">
						<BrainCircuit class="h-12 w-12 text-primary/60" />
					</div>
				</div>
				<p class="max-w-[250px] text-center font-sans text-sm leading-relaxed text-muted-foreground">
					Start a new conversation. Ask any question about your studies!
				</p>
			</div>
		{:else}
			{#each messages as message, i (i)}
				<div class="flex gap-3 {message.role === 'user' ? 'justify-end' : 'justify-start'}" in:fly={{ y: 10, duration: 300 }}>
					{#if message.role === 'assistant'}
						<div class="mt-1 shrink-0">
							<div class="flex h-7 w-7 items-center justify-center rounded-xl bg-primary/10 ring-1 ring-primary/20">
								<BrainCircuit class="h-4 w-4 text-primary" />
							</div>
						</div>
					{/if}

					<div class="max-w-[85%] {message.role === 'user' ? 'rounded-[1.5rem] rounded-br-md border border-primary/20 bg-primary/10 px-5 py-3' : 'max-w-2xl min-w-0 flex-1'}">
						{#if message.role === 'user'}
							<p class="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
								{message.content}
							</p>
						{:else}
							<div class="prose-chat">
								{@html renderMarkdown(message.content)}
							</div>
						{/if}
					</div>

					{#if message.role === 'user'}
						<div class="mt-1 shrink-0">
							<div class="flex h-7 w-7 items-center justify-center rounded-xl bg-muted ring-1 ring-border">
								<User class="h-4 w-4 text-muted-foreground" />
							</div>
						</div>
					{/if}
				</div>
			{/each}
			{#if isGenerating}
				<div class="flex justify-start gap-3" in:fly={{ y: 10, duration: 300 }}>
					<div class="mt-1 shrink-0">
						<div class="flex h-7 w-7 items-center justify-center rounded-xl bg-primary/10 ring-1 ring-primary/20">
							<BrainCircuit class="h-4 w-4 text-primary" />
						</div>
					</div>
					<div class="max-w-2xl min-w-0 flex-1 px-4 py-2">
						<div class="flex gap-1">
							<span class="typing-dot h-1.5 w-1.5 rounded-full bg-primary"></span>
							<span class="typing-dot h-1.5 w-1.5 rounded-full bg-primary" style="animation-delay: 0.15s"></span>
							<span class="typing-dot h-1.5 w-1.5 rounded-full bg-primary" style="animation-delay: 0.3s"></span>
						</div>
					</div>
				</div>
			{/if}
		{/if}
	</div>

	<!-- Input Area -->
	<div class="border-t border-border bg-card/40 p-3 backdrop-blur-2xl">
		<form onsubmit={handleSubmit} class="flex items-end gap-2">
			<div class="relative flex-1">
				<textarea
					bind:value={prompt}
					onkeydown={handleKeydown}
					disabled={isGenerating || providers.length === 0}
					placeholder={providers.length === 0 ? 'No models available' : 'Message...'}
					rows="1"
					class="custom-scrollbar w-full resize-none rounded-2xl border border-border bg-secondary/80 px-4 py-3 text-sm shadow-inner transition-all outline-none placeholder:text-muted-foreground/50 focus:border-primary/30 focus:ring-1 focus:ring-primary/20 disabled:opacity-50 text-foreground"
					style="max-height: 120px; min-height: 44px;"
					oninput={(e) => {
						const target = e.currentTarget;
						target.style.height = 'auto';
						target.style.height = Math.min(target.scrollHeight, 120) + 'px';
					}}
				></textarea>
			</div>
			<Button
				type="submit"
				disabled={isGenerating || !prompt.trim() || providers.length === 0}
				class="h-[44px] w-[44px] shrink-0 rounded-xl shadow-md transition-all hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0"
			>
				<Send class="h-4 w-4" />
			</Button>
		</form>
		{#if error}
			<p class="mt-2 text-center text-[10px] font-bold text-destructive">{error}</p>
		{/if}
	</div>
</div>

<style>
	.font-display {
		font-family: var(--font-display);
	}

	:global(.prose-chat p) {
		font-size: 0.9375rem;
		line-height: 1.6;
		margin-bottom: 0.75em;
		color: var(--prose-body);
	}
	:global(.prose-chat pre) {
		background: var(--prose-pre-bg);
		border: 1px solid var(--border);
		padding: 1rem;
		border-radius: 0.75rem;
		margin: 1rem 0;
		overflow-x: auto;
		font-size: 0.85rem;
	}
	:global(.prose-chat code) {
		color: var(--prose-code);
		font-size: 0.85em;
		background: var(--prose-code-bg);
		padding: 0.15rem 0.35rem;
		border-radius: 0.35rem;
	}
	:global(.prose-chat pre code) {
		background: transparent;
		padding: 0;
		color: var(--foreground);
	}

	:global(.prose-chat table) {
		width: 100%;
		border-collapse: collapse;
		margin: 1.5rem 0;
	}
	:global(.prose-chat th),
	:global(.prose-chat td) {
		border: 1px solid var(--border);
		padding: 0.75rem 1rem;
		text-align: left;
	}
	:global(.prose-chat th) {
		background: var(--muted);
		font-weight: 600;
		color: var(--foreground);
	}
	:global(.prose-chat ul),
	:global(.prose-chat ol) {
		padding-left: 1.5rem;
		margin: 1rem 0;
	}
	:global(.prose-chat ul) {
		list-style-type: disc;
	}
	:global(.prose-chat ol) {
		list-style-type: decimal;
	}
	:global(.prose-chat li) {
		margin-bottom: 0.5rem;
	}

	@keyframes typing-bounce {
		0%,
		80%,
		100% {
			transform: translateY(0);
			opacity: 0.3;
		}
		40% {
			transform: translateY(-4px);
			opacity: 1;
		}
	}
	.typing-dot {
		animation: typing-bounce 1.2s ease-in-out infinite;
	}

	.custom-scrollbar::-webkit-scrollbar {
		width: 4px;
	}
	.custom-scrollbar::-webkit-scrollbar-track {
		background: transparent;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: var(--border);
		border-radius: 10px;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb:hover {
		background: var(--muted);
	}
</style>
