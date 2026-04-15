<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { apiFetch, API_BASE_URL } from '$lib/api';
	import { auth } from '$lib/stores/auth.svelte';
	import { settings } from '$lib/stores/settings.svelte';
	import {
		MessageCircle,
		Send,
		Loader2,
		BrainCircuit,
		User,
		ChevronRight,
		Cpu,
		Sparkles,
		Trash2,
		BookOpen
	} from '@lucide/svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { marked } from 'marked';
	import markedKatex from 'marked-katex-extension';
	import 'katex/dist/katex.min.css';
	import { tick } from 'svelte';

	interface Provider {
		id: number;
		provider_name: string;
		model_name: string;
	}

	interface Lecture {
		id: number;
		title: string;
		description?: string;
	}

	interface ChatMessage {
		role: 'user' | 'assistant';
		content: string;
		timestamp: Date;
	}

	let providers = $state<Provider[]>([]);
	let lectures = $state<Lecture[]>([]);
	let messages = $state<ChatMessage[]>([]);
	let prompt = $state('');
	let isStreaming = $state(false);
	let isLoading = $state(true);
	let error = $state('');
	let selectedLectureId = $state<number | null>(null);
	let chatContainer: HTMLElement;

	// Configure marked with Katex
	marked.use(
		markedKatex({
			throwOnError: false
		})
	);

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
			const [providersData, lecturesData] = await Promise.all([
				apiFetch(`/llm/providers?user_id=${user.id}`),
				apiFetch(`/lectures/?user_id=${user.id}`)
			]);
			providers = providersData || [];
			lectures = lecturesData || [];
			if (providers.length > 0 && !settings.selectedProviderId) {
				settings.setProvider(providers[0].id);
			}
		} catch (err) {
			console.error('Failed to fetch data:', err);
		} finally {
			isLoading = false;
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

	function getLectureContext(): string | null {
		if (!selectedLectureId) return null;
		const lecture = lectures.find((l) => l.id === selectedLectureId);
		if (!lecture) return null;
		return `Lecture Title: ${lecture.title}\nDescription: ${lecture.description || 'N/A'}`;
	}

	async function handleSubmit(e?: SubmitEvent) {
		e?.preventDefault();
		if (!prompt.trim() || isStreaming || !settings.selectedProviderId) return;

		const user = auth.user;
		if (!user?.id) return;

		const userMessage: ChatMessage = {
			role: 'user',
			content: prompt.trim(),
			timestamp: new Date()
		};
		messages = [...messages, userMessage];

		const assistantMessage: ChatMessage = {
			role: 'assistant',
			content: '',
			timestamp: new Date()
		};
		messages = [...messages, assistantMessage];

		const currentPrompt = prompt.trim();
		prompt = '';
		isStreaming = true;
		error = '';

		await scrollToBottom();

		try {
			const token = localStorage.getItem('access_token');

			// Build chat history from all messages BEFORE this turn
			// (exclude the user message we just added and the empty assistant placeholder)
			const chat_history = messages.slice(0, -2).map((m) => ({
				role: m.role,
				content: m.content
			}));

			const response = await fetch(`${API_BASE_URL}/llm/chat`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					...(token ? { Authorization: `Bearer ${token}` } : {})
				},
				body: JSON.stringify({
					prompt: currentPrompt,
					provider_id: settings.selectedProviderId,
					user_id: user.id,
					lecture_context: getLectureContext(),
					chat_history: chat_history.length > 0 ? chat_history : null
				})
			});

			if (!response.ok) {
				let errorData = {} as any;
				try {
					errorData = await response.json();
				} catch {
					errorData = { detail: response.statusText };
				}
				throw new Error(errorData.detail || 'Chat request failed');
			}

			const reader = response.body?.getReader();
			const decoder = new TextDecoder();

			if (!reader) throw new Error('No response stream available');

			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });

				// Process SSE lines
				const lines = buffer.split('\n');
				buffer = lines.pop() || '';

				for (const line of lines) {
					if (line.startsWith('data: ')) {
						const data = line.slice(6);

						if (data === '[DONE]') {
							break;
						}

						if (data.startsWith('[ERROR]')) {
							throw new Error(data.slice(8));
						}

						// Append chunk to the last assistant message
						const lastMsg = messages[messages.length - 1];
						if (lastMsg && lastMsg.role === 'assistant') {
							lastMsg.content += data;
							messages = [...messages]; // trigger reactivity
						}
					}
				}

				await scrollToBottom();
			}
		} catch (err: any) {
			error = err.message || 'Failed to get a response. Please try again.';
			// Remove the empty assistant message if there was an error
			const lastMsg = messages[messages.length - 1];
			if (lastMsg && lastMsg.role === 'assistant' && !lastMsg.content) {
				messages = messages.slice(0, -1);
			}
		} finally {
			isStreaming = false;
			await scrollToBottom();
		}
	}

	function clearChat() {
		messages = [];
		error = '';
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

<svelte:head>
	<title>AI Chat — Excelsior</title>
	<meta name="description" content="Chat with your AI tutor about any topic or lecture." />
</svelte:head>

<div class="chat-page flex h-[calc(100vh-73px)] flex-col overflow-hidden">
	<!-- Chat Header -->
	<header
		class="relative z-10 flex items-center justify-between border-b border-border bg-card/30 px-6 py-4 backdrop-blur-2xl"
		in:fade={{ duration: 600 }}
	>
		<div class="flex items-center gap-4">
			<div class="rounded-2xl border border-indigo-500/20 bg-indigo-500/10 p-3">
				<MessageCircle class="h-5 w-5 text-indigo-400" />
			</div>
			<div>
				<h1 class="font-display text-xl font-black tracking-tighter text-white uppercase">
					AI Tutor
				</h1>
				<p class="text-[10px] font-bold tracking-widest text-muted-foreground uppercase">
					{#if isStreaming}
						<span class="inline-flex items-center gap-1.5 text-indigo-400">
							<span class="h-1.5 w-1.5 animate-pulse rounded-full bg-indigo-400"></span>
							Thinking...
						</span>
					{:else}
						Ask me anything
					{/if}
				</p>
			</div>
		</div>

		<div class="flex items-center gap-3">
			<!-- Lecture Context Selector -->
			<div class="relative hidden md:block">
				<select
					bind:value={selectedLectureId}
					class="h-10 w-56 cursor-pointer appearance-none rounded-xl border border-border bg-secondary px-3 pr-8 text-[10px] font-bold text-foreground shadow-lg transition-all outline-none focus:ring-1 focus:ring-primary"
				>
					<option value={null} class="bg-card text-foreground">No course selected</option>
					{#each lectures as lecture}
						<option value={lecture.id} class="bg-card text-foreground">{lecture.title}</option>
					{/each}
				</select>
				<BookOpen
					class="pointer-events-none absolute top-1/2 right-2.5 h-3 w-3 -translate-y-1/2 text-muted-foreground"
				/>
			</div>

			<!-- Provider Selector -->
			<div class="relative hidden md:block">
				<select
					bind:value={settings.selectedProviderId}
					onchange={() => settings.setProvider(Number(settings.selectedProviderId))}
					class="h-10 w-52 cursor-pointer appearance-none rounded-xl border border-border bg-secondary px-3 pr-8 text-[10px] font-bold text-foreground shadow-lg transition-all outline-none focus:ring-1 focus:ring-primary"
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

			{#if messages.length > 0}
				<Button
					variant="ghost"
					onclick={clearChat}
					class="h-10 rounded-xl px-3 text-[10px] font-black tracking-widest text-slate-500 uppercase hover:bg-red-500/10 hover:text-red-400"
				>
					<Trash2 class="mr-1.5 h-3.5 w-3.5" />
					Clear
				</Button>
			{/if}
		</div>
	</header>

	<!-- Chat Messages Area -->
	<div
		bind:this={chatContainer}
		class="custom-scrollbar flex flex-1 flex-col gap-1 overflow-y-auto px-4 py-6 md:px-8"
	>
		{#if messages.length === 0 && !isLoading}
			<!-- Empty State -->
			<div
				class="flex flex-1 flex-col items-center justify-center space-y-8"
				in:scale={{ duration: 600, start: 0.95 }}
			>
				<div class="relative">
					<div
						class="absolute inset-0 animate-pulse rounded-full bg-indigo-500/10 blur-[60px]"
					></div>
					<div
						class="relative rounded-[2rem] border border-white/5 bg-card/60 p-10 backdrop-blur-xl"
					>
						<BrainCircuit class="h-16 w-16 text-indigo-400/60" />
					</div>
				</div>
				<div class="max-w-md space-y-3 text-center">
					<h2
						class="font-display text-2xl font-black tracking-tighter text-white uppercase md:text-3xl"
					>
						Start a Conversation
					</h2>
					<p class="font-serif text-base leading-relaxed text-slate-500 italic">
						Ask your AI tutor about any topic. Select a lecture context above to ground responses in
						your study material.
					</p>
				</div>

				<!-- Suggested Prompts -->
				<div class="grid max-w-xl grid-cols-1 gap-3 pt-4 md:grid-cols-2">
					{#each ["Explain the concept of recursion like I'm 5", 'What are the key differences between TCP and UDP?', 'Help me understand quantum entanglement', 'Break down the Big-O notation for sorting algorithms'] as suggestion, i}
						<button
							onclick={() => {
								prompt = suggestion;
								handleSubmit();
							}}
							class="group rounded-2xl border border-white/5 bg-card/40 p-4 text-left transition-all duration-300 hover:-translate-y-0.5 hover:border-indigo-500/20 hover:bg-indigo-500/5 hover:shadow-lg"
							in:fly={{ y: 15, delay: 200 + i * 80, duration: 500 }}
						>
							<p
								class="text-xs leading-relaxed font-bold text-slate-400 group-hover:text-slate-300"
							>
								{suggestion}
							</p>
						</button>
					{/each}
				</div>
			</div>
		{:else}
			<!-- Message List -->
			{#each messages as message, i (i)}
				<div
					class="flex gap-4 {message.role === 'user' ? 'justify-end' : 'justify-start'}"
					in:fly={{ y: 10, duration: 300 }}
				>
					{#if message.role === 'assistant'}
						<div class="mt-1 shrink-0">
							<div
								class="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-500/10 ring-1 ring-indigo-500/20"
							>
								<BrainCircuit class="h-4 w-4 text-indigo-400" />
							</div>
						</div>
					{/if}

					<div
						class="max-w-[75%] {message.role === 'user'
							? 'rounded-[1.5rem] rounded-br-lg border border-indigo-500/20 bg-indigo-500/10 px-6 py-4'
							: 'max-w-3xl min-w-0 flex-1'}"
					>
						{#if message.role === 'user'}
							<p class="text-sm leading-relaxed whitespace-pre-wrap text-white/90">
								{message.content}
							</p>
						{:else}
							<div class="prose-chat">
								{#if message.content}
									{@html renderMarkdown(message.content)}
								{:else if isStreaming && i === messages.length - 1}
									<div class="flex items-center gap-2 py-2">
										<div class="flex gap-1">
											<span class="typing-dot h-1.5 w-1.5 rounded-full bg-indigo-400"></span>
											<span
												class="typing-dot h-1.5 w-1.5 rounded-full bg-indigo-400"
												style="animation-delay: 0.15s"
											></span>
											<span
												class="typing-dot h-1.5 w-1.5 rounded-full bg-indigo-400"
												style="animation-delay: 0.3s"
											></span>
										</div>
									</div>
								{/if}
							</div>
						{/if}
					</div>

					{#if message.role === 'user'}
						<div class="mt-1 shrink-0">
							<div
								class="flex h-8 w-8 items-center justify-center rounded-xl bg-white/5 ring-1 ring-white/10"
							>
								<User class="h-4 w-4 text-slate-400" />
							</div>
						</div>
					{/if}
				</div>
			{/each}
		{/if}

		{#if error}
			<div class="mx-auto max-w-2xl rounded-2xl border border-red-500/20 bg-red-500/5 p-4" in:fade>
				<p class="text-center text-sm font-bold text-red-400">{error}</p>
			</div>
		{/if}
	</div>

	<!-- Input Bar -->
	<div class="relative border-t border-border bg-card/40 px-4 py-4 backdrop-blur-2xl md:px-8">
		<!-- Mobile Selectors -->
		<div class="mb-3 flex gap-2 md:hidden">
			<div class="relative flex-1">
				<select
					bind:value={selectedLectureId}
					class="h-9 w-full cursor-pointer appearance-none rounded-lg border border-border bg-secondary px-3 text-[10px] font-bold text-foreground outline-none"
				>
					<option value={null}>No course selected</option>
					{#each lectures as lecture}
						<option value={lecture.id}>{lecture.title}</option>
					{/each}
				</select>
			</div>
			<div class="relative flex-1">
				<select
					bind:value={settings.selectedProviderId}
					onchange={() => settings.setProvider(Number(settings.selectedProviderId))}
					class="h-9 w-full cursor-pointer appearance-none rounded-lg border border-border bg-secondary px-3 text-[10px] font-bold text-foreground outline-none"
				>
					{#each providers as p}
						<option value={p.id}>{p.provider_name} — {p.model_name}</option>
					{/each}
				</select>
			</div>
		</div>

		<form onsubmit={handleSubmit} class="flex items-end gap-3">
			<div class="relative flex-1">
				<textarea
					bind:value={prompt}
					onkeydown={handleKeydown}
					disabled={isStreaming || providers.length === 0}
					placeholder={providers.length === 0
						? 'Add an AI model provider first...'
						: 'Ask your AI tutor anything...'}
					rows="1"
					class="custom-scrollbar w-full resize-none rounded-2xl border border-border bg-secondary/60 px-5 py-4 pr-4 text-sm text-white shadow-xl transition-all outline-none placeholder:text-slate-600 focus:border-indigo-500/30 focus:ring-2 focus:ring-indigo-500/10 disabled:cursor-not-allowed disabled:opacity-40"
					style="max-height: 160px; min-height: 52px;"
					oninput={(e) => {
						const target = e.currentTarget;
						target.style.height = 'auto';
						target.style.height = Math.min(target.scrollHeight, 160) + 'px';
					}}
				></textarea>
			</div>

			<Button
				type="submit"
				disabled={isStreaming || !prompt.trim() || providers.length === 0}
				class="h-[52px] w-[52px] shrink-0 rounded-2xl bg-indigo-600 shadow-lg shadow-indigo-500/20 transition-all hover:-translate-y-0.5 hover:bg-indigo-500 hover:shadow-xl disabled:opacity-30 disabled:hover:translate-y-0"
			>
				{#if isStreaming}
					<Loader2 class="h-5 w-5 animate-spin" />
				{:else}
					<Send class="h-5 w-5" />
				{/if}
			</Button>
		</form>

		<p class="mt-2 text-center text-[10px] tracking-wider text-slate-600">
			AI responses may be inaccurate. Always verify important information.
		</p>
	</div>
</div>

<style>
	.font-display {
		font-family: var(--font-display);
	}

	/* Chat prose styling */
	:global(.prose-chat) {
		font-family: var(--font-sans);
		line-height: 1.7;
	}

	:global(.prose-chat p) {
		font-size: 0.9375rem;
		line-height: 1.75;
		margin-top: 0.75em;
		margin-bottom: 0.75em;
		color: #cbd5e1;
	}

	:global(.prose-chat p:first-child) {
		margin-top: 0;
	}

	:global(.prose-chat h1, .prose-chat h2, .prose-chat h3) {
		font-family: var(--font-display);
		letter-spacing: -0.03em;
		font-weight: 800;
		margin-top: 1.5em;
		margin-bottom: 0.75em;
		line-height: 1.2;
		color: white;
	}

	:global(.prose-chat h1) {
		font-size: 1.5rem;
	}
	:global(.prose-chat h2) {
		font-size: 1.25rem;
	}
	:global(.prose-chat h3) {
		font-size: 1.125rem;
	}

	:global(.prose-chat strong) {
		color: white;
		font-weight: 700;
	}

	:global(.prose-chat em) {
		color: #94a3b8;
		font-style: italic;
	}

	:global(.prose-chat code) {
		font-family: 'JetBrains Mono', 'Fira Code', monospace;
		padding: 0.15rem 0.35rem;
		border-radius: 0.35rem;
		font-size: 0.85em;
		color: #818cf8;
		background: rgba(129, 140, 248, 0.1);
	}

	:global(.prose-chat pre) {
		background: #0f172a;
		border: 1px solid rgba(255, 255, 255, 0.05);
		padding: 1.25rem;
		border-radius: 1rem;
		margin: 1.25rem 0;
		overflow-x: auto;
		box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.4);
	}

	:global(.prose-chat pre code) {
		background: transparent;
		padding: 0;
		color: #e2e8f0;
		line-height: 1.6;
		font-size: 0.825rem;
	}

	:global(.prose-chat blockquote) {
		border-left: 3px solid var(--primary);
		background: rgba(99, 102, 241, 0.05);
		padding: 1rem 1.25rem;
		border-radius: 0 0.75rem 0.75rem 0;
		margin: 1rem 0;
		font-style: italic;
		color: #cbd5e1;
	}

	:global(.prose-chat ul, .prose-chat ol) {
		margin-top: 0.75em;
		margin-bottom: 0.75em;
		padding-left: 1.25em;
	}

	:global(.prose-chat ul) {
		list-style-type: disc;
	}

	:global(.prose-chat ol) {
		list-style-type: decimal;
	}

	:global(.prose-chat li) {
		margin-top: 0.35em;
		margin-bottom: 0.35em;
		font-size: 0.9375rem;
		line-height: 1.65;
		color: #cbd5e1;
	}

	:global(.prose-chat a) {
		color: #818cf8;
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	:global(.prose-chat hr) {
		border-color: rgba(255, 255, 255, 0.06);
		margin: 1.5rem 0;
	}

	:global(.prose-chat table) {
		width: 100%;
		border-collapse: collapse;
		margin: 1rem 0;
		font-size: 0.875rem;
	}

	:global(.prose-chat th) {
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		padding: 0.5rem 0.75rem;
		text-align: left;
		color: white;
		font-weight: 700;
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	:global(.prose-chat td) {
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		padding: 0.5rem 0.75rem;
		color: #94a3b8;
	}

	/* Typing animation */
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

	/* Custom scrollbar */
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
