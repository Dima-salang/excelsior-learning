<script lang="ts">
	import { fade, fly, slide } from 'svelte/transition';
	import { CheckCircle2, XCircle, HelpCircle, ArrowRight } from '@lucide/svelte';
	import { Button } from '$lib/components/ui/button';
	import { cn } from '$lib/utils';
	import MarkdownRenderer from './MarkdownRenderer.svelte';

	interface CardProps {
		id: number;
		type: string;
		front: string;
		back?: string;
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
		back,
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

	let isCorrect = $derived(selectedIdx !== null && selectedIdx === options_ans);
	let isExplanationType = $derived(type === 'explanation');
	let isStandardType = $derived(type === 'standard');

	function selectOption(idx: number) {
		if (isRevealed) return;
		selectedIdx = idx;
		isRevealed = true;

		if (onAnswered) {
			onAnswered(idx === options_ans, idx);
		}
	}

	function handleExplanationReveal() {
		if (isRevealed) return;
		isRevealed = true;
		selectedIdx = 0;
		if (onAnswered) {
			onAnswered(true, 0);
		}
	}

	function handleStandardFlip() {
		isRevealed = !isRevealed;
		if (isRevealed && onAnswered && selectedIdx === null) {
			selectedIdx = 0;
			onAnswered(true, 0);
		}
	}
</script>

<div
	class={cn(
		'group relative mb-8 rounded-3xl transition-all duration-500',
		!isStandardType && 'overflow-hidden border border-border bg-card/40 p-8 shadow-2xl backdrop-blur-md hover:border-primary/30 hover:bg-muted/60',
		isRevealed && !isStandardType && !isCorrect && 'animate-reject',
		compact && !isStandardType && 'mb-4 rounded-2xl p-5 shadow-lg',
		showRating && isRevealed && 'ring-2 ring-primary/50 ring-offset-4 ring-offset-background',
		isStandardType && 'perspective-1000 h-[300px] w-full cursor-pointer'
	)}
	onclick={isStandardType ? handleStandardFlip : undefined}
>
	{#if isStandardType}
		<div
			class={cn(
				'relative h-full w-full transition-all duration-700 [transform-style:preserve-3d]',
				isRevealed && '[transform:rotateY(180deg)]'
			)}
		>
			<!-- Front -->
			<div
				class="absolute inset-0 flex flex-col items-center justify-center rounded-3xl border border-border bg-card/80 p-8 text-center shadow-2xl backdrop-blur-xl [backface-visibility:hidden]"
			>
				<div class="absolute top-6 left-8">
					<span
						class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-primary uppercase"
					>
						<HelpCircle class="h-3 w-3" />
						Question
					</span>
				</div>
				<MarkdownRenderer
					content={front}
					class="text-xl leading-relaxed font-bold md:text-2xl"
					compact
				/>
				<div class="absolute bottom-6 flex items-center gap-2 text-[9px] font-black tracking-widest text-muted-foreground uppercase opacity-50">
					<span>Click to Flip</span>
				</div>
			</div>

			<!-- Back -->
			<div
				class="absolute inset-0 flex flex-col items-center justify-center rounded-3xl border border-primary/30 bg-primary/5 p-8 text-center shadow-2xl backdrop-blur-xl [backface-visibility:hidden] [transform:rotateY(180deg)]"
			>
				<div class="absolute top-6 left-8">
					<span
						class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-success uppercase"
					>
						<CheckCircle2 class="h-3 w-3" />
						Answer
					</span>
				</div>
				<MarkdownRenderer
					content={back || ''}
					class="text-xl leading-relaxed font-bold text-foreground md:text-2xl"
					compact
				/>
			</div>
		</div>
	{:else}
		<div class="relative z-10 space-y-6" class:space-y-4={compact}>
			<div class="flex items-center justify-between">
				<span
					class="flex items-center gap-2 text-[10px] font-black tracking-[0.3em] text-primary uppercase"
				>
					{#if isExplanationType}
						<HelpCircle class="h-3 w-3" />
						Explanation
					{:else}
						<HelpCircle class="h-3 w-3" />
						Knowledge Check
					{/if}
				</span>
				{#if isRevealed}
					<div in:fade class="flex items-center gap-2">
						<span
							class="flex items-center gap-1.5 text-[10px] font-black tracking-widest text-success uppercase"
						>
							<CheckCircle2 class="h-3.5 w-3.5" />
							Revealed
						</span>
					</div>
				{/if}
			</div>

			<MarkdownRenderer
				content={front}
				class="text-xl leading-relaxed font-bold md:text-2xl"
				compact
			/>

			{#if isExplanationType}
				{#if !isRevealed}
					<button
						onclick={handleExplanationReveal}
						class="w-full rounded-xl border border-primary/30 bg-primary/10 p-4 text-center text-sm font-medium text-primary transition-all hover:bg-primary/20"
					>
						Show Explanation
					</button>
				{:else}
					<div
						in:slide={{ duration: 400 }}
						class={cn(
							'mt-6 rounded-2xl border border-primary/10 bg-primary/5 p-4',
							compact && 'mt-4 rounded-xl'
						)}
					>
						<div class="font-sans text-xs leading-relaxed text-muted-foreground italic">
							<strong
								class="mr-2 text-[9px] font-black tracking-widest text-primary uppercase not-italic"
								>Insight:</strong
							>
							<MarkdownRenderer content={explanation || ''} class="inline" />
						</div>
					</div>
				{/if}
			{:else if displayOptions && displayOptions.length > 0}
				<div class="space-y-3" class:space-y-2={compact} style="perspective: 1000px;">
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
							<MarkdownRenderer content={displayOptions[idx]} class="prose-sm" compact />
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
				</div>
			{/if}

			{#if !isExplanationType && isRevealed && explanation}
				<div
					in:slide={{ duration: 400 }}
					class={cn(
						'mt-6 rounded-2xl border border-primary/10 bg-primary/5 p-4',
						compact && 'mt-4 rounded-xl'
					)}
				>
					<div class="font-sans text-xs leading-relaxed text-muted-foreground italic">
						<strong
							class="mr-2 text-[9px] font-black tracking-widest text-primary uppercase not-italic"
							>Insight:</strong
						>
						<MarkdownRenderer content={explanation || ''} class="inline" />
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.perspective-1000 {
		perspective: 1000px;
	}

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
</style>
