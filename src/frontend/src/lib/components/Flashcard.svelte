<script lang="ts">
	import { fade, fly, slide } from 'svelte/transition';
	import { CheckCircle2, XCircle, HelpCircle, ArrowRight, RotateCcw } from '@lucide/svelte';
	import { Button } from '$lib/components/ui/button';
	import { cn } from '$lib/utils';

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
		'group relative mb-8 overflow-hidden rounded-3xl border border-white/5 bg-slate-900/40 p-8 shadow-2xl backdrop-blur-md transition-all duration-500 hover:border-indigo-500/30 hover:bg-slate-900/60',
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

		<h3 class={cn("text-xl leading-relaxed font-bold text-white md:text-2xl", compact && "text-base md:text-lg")}>
			{front}
		</h3>

		<div class={cn("space-y-3", compact && "space-y-2")} style="perspective: 1000px;">
			{#if options}
				{#each options as option, idx}
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
									: 'border-white/5 bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white'
						)}
					>
						<span>{option}</span>
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
				<p class="font-serif text-xs leading-relaxed text-indigo-300 italic">
					<strong
						class="mr-2 text-[9px] font-black tracking-widest text-indigo-400 uppercase not-italic"
						>Insight:</strong
					>
					{explanation}
				</p>
				{#if !isCorrect}
					<Button
						variant="ghost"
						size="sm"
						onclick={reset}
						class="mt-4 h-8 gap-2 px-0 text-[10px] font-black tracking-widest text-slate-500 uppercase hover:bg-white/5 hover:text-white"
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
</style>

