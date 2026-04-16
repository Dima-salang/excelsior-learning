<script lang="ts">
	import { ChevronDown, Search, X } from '@lucide/svelte';
	import { fade, slide } from 'svelte/transition';
	import { cn } from '$lib/utils';

	interface FilterOption {
		value: string;
		label: string;
	}

	interface Props {
		searchPlaceholder?: string;
		searchValue?: string;
		onSearchChange?: (value: string) => void;
		sortOptions?: FilterOption[];
		sortValue?: string;
		onSortChange?: (value: string) => void;
		statusOptions?: FilterOption[];
		statusValue?: string;
		onStatusChange?: (value: string) => void;
		onClear?: () => void;
		resultCount?: number;
		class?: string;
	}

	let {
		searchPlaceholder = 'Search...',
		searchValue = $bindable(''),
		onSearchChange,
		sortOptions = [],
		sortValue = $bindable('descending'),
		onSortChange,
		statusOptions = [],
		statusValue = $bindable('all'),
		onStatusChange,
		onClear,
		resultCount,
		class: className = ''
	}: Props = $props();

	function handleSearchInput(e: Event) {
		const target = e.target as HTMLInputElement;
		searchValue = target.value;
		onSearchChange?.(target.value);
	}

	function handleSortChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		sortValue = target.value;
		onSortChange?.(target.value);
	}

	function handleStatusChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		statusValue = target.value;
		onStatusChange?.(target.value);
	}

	function clearSearch() {
		searchValue = '';
		onSearchChange?.('');
	}

	function clearAll() {
		searchValue = '';
		sortValue = 'descending';
		statusValue = 'all';
		onClear?.();
	}

	let hasActiveFilters = $derived(
		searchValue !== '' || sortValue !== 'descending' || statusValue !== 'all'
	);
</script>

<div class={cn('space-y-4', className)}>
	<div class="flex flex-col gap-4 sm:flex-row sm:items-center">
		<!-- Search Input -->
		<div class="relative flex-1">
			<Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
			<input
				type="text"
				value={searchValue}
				oninput={handleSearchInput}
				placeholder={searchPlaceholder}
				class="h-11 w-full rounded-xl border border-border bg-card pl-10 pr-10 text-sm transition-all placeholder:text-muted-foreground/50 focus:border-primary/50 focus:bg-card focus:outline-none focus:ring-2 focus:ring-primary/20"
			/>
			{#if searchValue}
				<button
					onclick={clearSearch}
					class="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
					in:fade={{ duration: 150 }}
				>
					<X class="h-3 w-3" />
				</button>
			{/if}
		</div>

		<div class="flex items-center gap-2">
			<!-- Sort Dropdown -->
			{#if sortOptions.length > 0}
				<div class="relative">
					<select
						value={sortValue}
						onchange={handleSortChange}
						class="h-11 appearance-none rounded-xl border border-border bg-card px-4 pr-10 text-sm font-medium transition-all focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/20"
					>
						{#each sortOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
					<ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
				</div>
			{/if}

			<!-- Status Filter Dropdown -->
			{#if statusOptions.length > 0}
				<div class="relative">
					<select
						value={statusValue}
						onchange={handleStatusChange}
						class="h-11 appearance-none rounded-xl border border-border bg-card px-4 pr-10 text-sm font-medium transition-all focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/20"
					>
						{#each statusOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
					<ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
				</div>
			{/if}

			<!-- Clear Filters Button -->
			{#if hasActiveFilters}
				<button
					onclick={clearAll}
					class="flex h-11 items-center gap-2 rounded-xl border border-border bg-card px-4 text-sm font-medium text-muted-foreground transition-all hover:border-destructive/30 hover:bg-destructive/5 hover:text-destructive"
					in:fade={{ duration: 150 }}
				>
					<X class="h-4 w-4" />
					<span class="hidden sm:inline">Clear</span>
				</button>
			{/if}
		</div>
	</div>

	<!-- Active Filters Pills -->
	{#if hasActiveFilters}
		<div class="flex flex-wrap items-center gap-2" transition:slide={{ duration: 200 }}>
			{#if searchValue}
				<span class="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary">
					Search: "{searchValue}"
					<button onclick={clearSearch} class="ml-1 rounded-full hover:bg-primary/20">
						<X class="h-3 w-3" />
					</button>
				</span>
			{/if}
			{#if sortValue !== 'descending'}
				<span class="inline-flex items-center gap-1.5 rounded-full border border-accent/20 bg-accent/10 px-3 py-1.5 text-xs font-medium text-accent">
					Sort: {sortOptions.find(o => o.value === sortValue)?.label || sortValue}
					<button onclick={() => { sortValue = 'descending'; onSortChange?.('descending'); }} class="ml-1 rounded-full hover:bg-accent/20">
						<X class="h-3 w-3" />
					</button>
				</span>
			{/if}
			{#if statusValue !== 'all'}
				<span class="inline-flex items-center gap-1.5 rounded-full border border-success/20 bg-success/10 px-3 py-1.5 text-xs font-medium text-success">
					Status: {statusOptions.find(o => o.value === statusValue)?.label || statusValue}
					<button onclick={() => { statusValue = 'all'; onStatusChange?.('all'); }} class="ml-1 rounded-full hover:bg-success/20">
						<X class="h-3 w-3" />
					</button>
				</span>
			{/if}
		</div>
	{/if}
</div>

<style>
	input[type="text"] {
		appearance: none;
		-webkit-appearance: none;
	}

	select {
		appearance: none;
		-webkit-appearance: none;
	}
</style>
