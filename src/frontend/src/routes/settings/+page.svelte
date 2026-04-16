<script lang="ts">
	import { settings, type Theme } from '$lib/stores/settings.svelte';
	import { fade, fly } from 'svelte/transition';
	import { Palette, Monitor, Sun, Moon, Check } from 'lucide-svelte';

	const themeOptions: { value: Theme; label: string; icon: typeof Sun; description: string }[] = [
		{
			value: 'light',
			label: 'Light',
			icon: Sun,
			description: 'Clean and bright for daytime use'
		},
		{
			value: 'dark',
			label: 'Dark',
			icon: Moon,
			description: 'Easy on the eyes at night'
		},
		{
			value: 'system',
			label: 'System',
			icon: Monitor,
			description: 'Syncs with your device settings'
		}
	];

	function setTheme(theme: Theme) {
		settings.setTheme(theme);
	}
</script>

<svelte:head>
	<title>Appearance — Excelsior</title>
</svelte:head>

<div class="min-h-[calc(100vh-64px)] px-6 py-12 md:px-12">
	<div class="mx-auto max-w-2xl">
		<header class="mb-10" in:fade={{ duration: 300 }}>
			<div class="mb-4 flex items-center gap-3">
				<div class="rounded-xl border border-border bg-secondary p-2">
					<Palette class="h-5 w-5 text-foreground" />
				</div>
				<span class="text-sm font-medium text-muted-foreground">Appearance</span>
			</div>
			<h1 class="text-3xl font-bold tracking-tight">Theme</h1>
			<p class="mt-2 text-muted-foreground">Choose your preferred color theme for the interface.</p>
		</header>

		<div class="space-y-3" in:fly={{ y: 10, duration: 400 }}>
			{#each themeOptions as option}
				<button
					onclick={() => setTheme(option.value)}
					class="group flex w-full items-center justify-between rounded-lg border p-4 transition-colors hover:bg-accent/50 {settings.theme ===
					option.value
						? 'border-primary bg-accent'
						: 'border-border'}"
				>
					<div class="flex items-center gap-4">
						<div
							class="flex h-10 w-10 items-center justify-center rounded-md bg-secondary {settings.theme ===
							option.value
								? 'bg-primary/10'
								: ''}"
						>
							<option.icon
								class="h-5 w-5 {settings.theme === option.value
									? 'text-primary'
									: 'text-muted-foreground'}"
							/>
						</div>
						<div class="text-left">
							<p class="font-medium">{option.label}</p>
							<p class="text-sm text-muted-foreground">{option.description}</p>
						</div>
					</div>
					{#if settings.theme === option.value}
						<div
							class="flex h-6 w-6 items-center justify-center rounded-full bg-primary"
							in:fade={{ duration: 200 }}
						>
							<Check class="h-3.5 w-3.5 text-primary-foreground" />
						</div>
					{/if}
				</button>
			{/each}
		</div>
	</div>
</div>
