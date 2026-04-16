<script lang="ts">
	import { fade, fly, slide } from 'svelte/transition';
	import { CheckCircle2, XCircle, HelpCircle, ArrowRight } from '@lucide/svelte';
	import { Button } from '$lib/components/ui/button';
	import { cn } from '$lib/utils';
	import { marked } from 'marked';
	import markedKatex from 'marked-katex-extension';

	marked.use(
		markedKatex({
			throwOnError: false
		})
	);

	interface CardProps {
		id: number;
		type: string;
		front: string;
		options?: string[];
		options_ans?: number;
		explanation?: string;
		onAnswered?: (isCorrect: boolean, selectedIdx: number) => void;
		compact?: boolean;
		showRating?: boolean;
	}

	let {
		id,
		type,
		front,
		options,
		options_ans,
		explanation,
		onAnswered,
		compact = false,
		showRating = false
	}: CardProps = $props();

	let selectedIdx = $state<number | null>(null);
	let isRevealed = $state(false);

	let displayOptions = $derived(
		options && options.length > 0 ? options : type === 'truefalse' ? ['True', 'False'] : []
	);

	let renderedFront = $derived(marked.parse(front, { breaks: true, gfm: true }));
	let renderedOptions = $derived(
		displayOptions.map((opt) => marked.parse(opt, { breaks: true, gfm: true }))
	);
	let renderedExplanation = $derived(
		explanation ? marked.parse(explanation, { breaks: true, gfm: true }) : ''
	);

	let isCorrect = $derived(selectedIdx !== null && selectedIdx === options_ans);

	function selectOption(idx: number) {
		if (isRevealed) return;
		selectedIdx = idx;
		isRevealed = true;

		if (onAnswered) {
			onAnswered(idx === options_ans, idx);
		}
	}
</script>

<div
	class={cn(
		'group relative mb-8 overflow-hidden rounded-3xl border border-border bg-card/40 p-8 shadow-2xl backdrop-blur-md transition-all duration-500 hover:border-primary/30 hover:bg-muted/60',
		isRevealed && !isCorrect && 'animate-reject',
		compact && 'mb-4 rounded-2xl p-5 shadow-lg',
		showRating && isRevealed && 'ring-2 ring-primary/50 ring-offset-4 ring-offset-background'
	)}
>
	<div class="relative z-10 space-y-6" class:space-y-4={compact}>
		<div class="flex items-center justify-between">
			<span class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-primary uppercase">
				<HelpCircle class="h-3 w-3" />
				Knowledge Check
			</span>
			{#if isRevealed}
				<div in:fade class="flex items-center gap-2">
					{#if isCorrect}
						<span class="flex items-center gap-1.5 text-[10px] font-black tracking-widest text-success uppercase">
							<CheckCircle2 class="h-3.5 w-3.5" />
							Mastered
						</span>
					{:else}
						<span class="flex items-center gap-1.5 text-[10px] font-black tracking-widest text-destructive uppercase">
							<XCircle class="h-3.5 w-3.5" />
							Incorrect
						</span>
					{/if}
				</div>
			{/if}
		</div>

		<div
			class="markdown-content text-xl leading-relaxed font-bold md:text-2xl"
			class:text-base={compact}
			class:md:text-lg={compact}
		>
			{@html renderedFront}
		</div>

		<div class="space-y-3" class:space-y-2={compact} style="perspective: 1000px;">
			{#if displayOptions && displayOptions.length > 0}
				{#each displayOptions as option, idx}
					<button
						onclick={() => selectOption(idx)}
						disabled={isRevealed}
						class={cn(
							'group/opt flex w-full items-center justify-between rounded-xl border p-4 text-left text-sm font-medium transition-all duration-300',
							compact && 'rounded-lg p-3 text-xs',
							selectedIdx === idx
								? idx === options_ans
									? 'border-success/50 bg-success/10 text-success shadow-[0_0_20px_rgba(var(--color-success),0.1)]'
									: 'border-destructive/50 bg-destructive/10 text-destructive shadow-[0_0_20px_rgba(var(--color-destructive),0.1)]'
								: isRevealed && idx === options_ans
									? 'border-success/20 bg-success/5 text-success/70'
									: 'border-border bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground'
						)}
					>
						<div class="markdown-content prose-sm">
							{@html renderedOptions[idx]}
						</div>
						{#if isRevealed}
							{#if idx === options_ans}
								<CheckCircle2 class="h-4 w-4 text-success" />
							{:else if selectedIdx === idx}
								<XCircle class="h-4 w-4 text-destructive" />
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
				class={cn(
					'mt-6 rounded-2xl border border-primary/10 bg-primary/5 p-4',
					compact && 'mt-4 rounded-xl'
				)}
			>
				<div class="markdown-content font-sans text-xs leading-relaxed text-muted-foreground italic">
					<strong
						class="mr-2 text-[9px] font-black tracking-widest text-primary uppercase not-italic"
						>Insight:</strong
					>
					{@html renderedExplanation}
				</div>
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
		color: var(--foreground);
	}
	:global(.markdown-content p:last-child) {
		margin-bottom: 0;
	}
	:global(.markdown-content code) {
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		background-color: var(--prose-code-bg);
		color: var(--prose-code);
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New',
			monospace;
		font-size: 0.9em;
	}
	:global(.markdown-content pre) {
		padding: 1rem;
		border-radius: 0.75rem;
		background-color: var(--prose-pre-bg);
		border: 1px solid var(--border);
		margin-top: 1rem;
		margin-bottom: 1rem;
		overflow-x: auto;
	}
	:global(.markdown-content pre code) {
		background-color: transparent;
		padding: 0;
	}
	:global(.markdown-content ul),
	:global(.markdown-content ol) {
		margin-left: 1rem;
		margin-bottom: 0.5rem;
		list-style-type: disc;
	}
	:global(.markdown-content ul > * + *),
	:global(.markdown-content ol > * + *) {
		margin-top: 0.25rem;
	}
	:global(.markdown-content strong) {
		font-weight: 900;
		color: var(--foreground);
	}
	:global(.markdown-content li) {
		color: var(--foreground);
	}
</style>
