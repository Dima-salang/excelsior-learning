<script lang="ts">
	import { fade, fly, slide } from 'svelte/transition';
	import { CheckCircle2, XCircle, HelpCircle, ArrowRight, RotateCcw } from '@lucide/svelte';
	import { Button } from '$lib/components/ui/button';
	import { cn } from '$lib/utils';
	import { marked } from 'marked';

	interface CardProps {
		id: number;
		type: string;
		front: string;
		options?: string[];
		options_ans?: number;
		explanation?: string;
		onAnswered?: (isCorrect: boolean, selectedIdx: number) => void;
		compact?: boolean;
	}

	let {
		id,
		type,
		front,
		options,
		options_ans,
		explanation,
		onAnswered,
		compact = false
	}: CardProps = $props();

	let selectedIdx = $state<number | null>(null);
	let isRevealed = $state(false);
	
	let displayOptions = $derived(
		options && options.length > 0 
			? options 
			: (type === 'truefalse' ? ['True', 'False'] : [])
	);

	let renderedFront = $derived(marked.parse(front, { breaks: true, gfm: true }));
	let renderedOptions = $derived(displayOptions.map(opt => marked.parse(opt, { breaks: true, gfm: true })));
	let renderedExplanation = $derived(explanation ? marked.parse(explanation, { breaks: true, gfm: true }) : '');

	let isCorrect = $derived(selectedIdx !== null && selectedIdx === options_ans);

	function selectOption(idx: number) {
		if (isRevealed) return;
		selectedIdx = idx;
		isRevealed = true;

		if (onAnswered) {
			onAnswered(idx === options_ans, idx);
		}
	}

	function reset() {
		selectedIdx = null;
		isRevealed = false;
	}
</script>

<div
	class={cn(
		'group relative mb-8 overflow-hidden rounded-3xl border border-border bg-card/40 p-8 shadow-2xl backdrop-blur-md transition-all duration-500 hover:border-primary/30 hover:bg-muted/60',
		isRevealed && !isCorrect && 'animate-reject',
		compact && 'p-5 mb-4 rounded-2xl shadow-lg'
	)}
>
	<!-- Decorative background element -->
	<div
		class={cn(
			"absolute -top-10 -right-10 h-40 w-40 rounded-full bg-indigo-600/10 blur-[80px] transition-all duration-700 group-hover:bg-indigo-600/20",
			compact && "h-24 w-24 blur-[60px]"
		)}
	></div>

	<div class={cn("relative z-10 space-y-6", compact && "space-y-4")}>
		<div class="flex items-center justify-between">
			<span
				class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-indigo-400 uppercase"
			>
				<HelpCircle class="h-3 w-3" />
				Knowledge Check
			</span>
			{#if isRevealed}
				<div in:fade class="flex items-center gap-2">
					{#if isCorrect}
						<span
							class="flex items-center gap-1.5 text-[10px] font-black tracking-widest text-emerald-400 uppercase"
						>
							<CheckCircle2 class="h-3.5 w-3.5" />
							Mastered
						</span>
					{:else}
						<span
							class="flex items-center gap-1.5 text-[10px] font-black tracking-widest text-red-400 uppercase"
						>
							<XCircle class="h-3.5 w-3.5" />
							Incorrect
						</span>
					{/if}
				</div>
			{/if}
		</div>

		<div class={cn("markdown-content text-xl leading-relaxed font-bold text-white md:text-2xl", compact && "text-base md:text-lg")}>
			{@html renderedFront}
		</div>

		<div class={cn("space-y-3", compact && "space-y-2")} style="perspective: 1000px;">
			{#if displayOptions && displayOptions.length > 0}
				{#each displayOptions as option, idx}
					<button
						onclick={() => selectOption(idx)}
						disabled={isRevealed}
						class={cn(
							'group/opt flex w-full items-center justify-between rounded-xl border p-4 text-left text-sm font-medium transition-all duration-300',
							compact && "p-3 text-xs rounded-lg",
							selectedIdx === idx
								? idx === options_ans
									? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.1)]'
									: 'border-red-500/50 bg-red-500/10 text-red-400 shadow-[0_0_20px_rgba(239,68,68,0.1)]'
								: isRevealed && idx === options_ans
									? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400/70'
									: 'border-border bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground'
						)}
					>
						<div class="markdown-content prose-sm prose-invert">
							{@html renderedOptions[idx]}
						</div>
						{#if isRevealed}
							{#if idx === options_ans}
								<CheckCircle2 class="h-4 w-4 text-emerald-500" />
							{:else if selectedIdx === idx}
								<XCircle class="h-4 w-4 text-red-500" />
							{/if}
						{:else}
							<ArrowRight
								class="h-4 w-4 translate-x-2 opacity-0 transition-all group-hover/opt:translate-x-0 group-hover/opt:opacity-100"
							/>
						{/if}
					</button>
				{/each}
			{/if}
		</div>

		{#if isRevealed && explanation}
			<div
				in:slide={{ duration: 400 }}
				class={cn("mt-6 rounded-2xl border border-indigo-500/10 bg-indigo-500/5 p-4", compact && "mt-4 rounded-xl")}
			>
				<div class="font-serif text-xs leading-relaxed text-indigo-300 italic markdown-content">
					<strong
						class="mr-2 text-[9px] font-black tracking-widest text-indigo-400 uppercase not-italic"
						>Insight:</strong
					>
					{@html renderedExplanation}
				</div>
				{#if !isCorrect}
					<Button
						variant="ghost"
						size="sm"
						onclick={reset}
						class="mt-4 h-8 gap-2 px-0 text-[10px] font-black tracking-widest text-muted-foreground uppercase hover:bg-muted hover:text-foreground"
					>
						<RotateCcw class="h-3 w-3" />
						Try Again
					</Button>
				{/if}
			</div>
		{/if}
	</div>
</div>


<style>
	@keyframes reject {
		0%,
		100% {
			transform: translateX(0) rotateY(0deg);
		}
		20% {
			transform: translateX(-10px) rotateY(-5deg);
		}
		40% {
			transform: translateX(10px) rotateY(5deg);
		}
		60% {
			transform: translateX(-5px) rotateY(-2deg);
		}
		80% {
			transform: translateX(5px) rotateY(2deg);
		}
	}

	.animate-reject {
		animation: reject 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
		perspective: 1000px;
		backface-visibility: hidden;
	}

	:global(.markdown-content) {
		line-height: 1.625;
	}
	:global(.markdown-content p) {
		margin-bottom: 0.5rem;
	}
	:global(.markdown-content p:last-child) {
		margin-bottom: 0;
	}
	:global(.markdown-content code) {
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		background-color: rgba(255, 255, 255, 0.1);
		color: #a5b4fc;
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
		font-size: 0.9em;
	}
	:global(.markdown-content pre) {
		padding: 1rem;
		border-radius: 0.75rem;
		background-color: rgba(2, 6, 23, 0.5);
		border: 1px solid rgba(255, 255, 255, 0.05);
		margin-top: 1rem;
		margin-bottom: 1rem;
		overflow-x: auto;
	}
	:global(.markdown-content ul), :global(.markdown-content ol) {
		margin-left: 1rem;
		margin-bottom: 0.5rem;
		list-style-type: disc;
	}
	:global(.markdown-content ul > * + *), :global(.markdown-content ol > * + *) {
		margin-top: 0.25rem;
	}
	:global(.markdown-content strong) {
		font-weight: 900;
		color: white;
	}
</style>

