<script lang="ts">
	import { BrainCircuit, ChevronDown, LogOut, User, Settings, Sparkles } from '@lucide/svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { page } from '$app/state';
	import { fade, fly, scale } from 'svelte/transition';
	import { quintOut, backOut } from 'svelte/easing';

	let dropdownOpen = $state(false);
	let loggingOut = $state(false);
	let showLogoutMessage = $state(false);

	const isActive = (path: string) => {
		if (path === '/') return page.url.pathname === '/';
		return page.url.pathname.startsWith(path);
	};

	function toggleDropdown() {
		dropdownOpen = !dropdownOpen;
	}

	function closeDropdown() {
		dropdownOpen = false;
	}

	async function handleLogout() {
		dropdownOpen = false;
		loggingOut = true;

		await new Promise((resolve) => setTimeout(resolve, 800));

		auth.logout();
		loggingOut = false;
		showLogoutMessage = true;

		await new Promise((resolve) => setTimeout(resolve, 1500));
		showLogoutMessage = false;
		window.location.href = '/login';
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && dropdownOpen) {
			closeDropdown();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<nav
	class="sticky top-0 z-50 flex w-full items-center justify-between border-b border-white/5 bg-background/80 px-6 py-4 backdrop-blur-3xl backdrop-saturate-150 md:px-12"
	in:fade={{ duration: 300 }}
>
	<div class="flex items-center gap-12">
		<a href="/" class="group flex items-center gap-3 px-2">
			<div class="flex flex-col">
				<span class="font-display text-xl font-black tracking-tighter text-white uppercase"
					>EXCELSIOR</span
				>
				<span
					class="-mt-1 font-display text-[8px] font-black tracking-[0.4em] text-primary uppercase"
					>Academy</span
				>
			</div>
		</a>
		<div
			class="hidden items-center gap-8 text-xs font-black tracking-widest text-muted-foreground uppercase md:flex"
		>
			<a
				href="/"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/')
					? 'text-foreground'
					: ''}"
			>
				Dashboard
				{#if isActive('/')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/providers"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/providers')
					? 'text-foreground'
					: ''}"
			>
				AI Models
				{#if isActive('/providers')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/generate"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/generate')
					? 'text-foreground'
					: ''}"
			>
				Generate
				{#if isActive('/generate')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/chat"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/chat')
					? 'text-foreground'
					: ''}"
			>
				Chat
				{#if isActive('/chat')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
			<a
				href="/decks"
				class="relative pb-1 transition-all hover:text-foreground {isActive('/decks')
					? 'text-foreground'
					: ''}"
			>
				Decks
				{#if isActive('/decks')}
					<div
						class="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
					></div>
				{/if}
			</a>
		</div>
	</div>

	<div class="relative flex items-center gap-4 pr-2">
		<button
			onclick={toggleDropdown}
			onkeydown={(e) => e.key === 'Enter' && toggleDropdown()}
			class="group flex items-center gap-3 rounded-full px-3 py-2 transition-all duration-300 hover:bg-white/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
			aria-expanded={dropdownOpen}
			aria-haspopup="true"
		>
			<div class="mr-1 flex flex-col items-end">
				<span class="text-xs font-black text-foreground transition-colors group-hover:text-primary"
					>{auth.user?.username || 'Guest'}</span
				>
			</div>
			<div
				class="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-secondary transition-all duration-300 group-hover:border-primary/40 group-hover:shadow-[0_0_15px_rgba(99,102,241,0.2)] {dropdownOpen
					? 'border-primary/60 shadow-[0_0_20px_rgba(99,102,241,0.3)]'
					: ''}"
			>
				<span class="text-xs font-black text-primary uppercase"
					>{auth.user?.username?.[0] || 'G'}</span
				>
			</div>
			<ChevronDown
				class="h-4 w-4 text-muted-foreground transition-all duration-300 group-hover:text-primary {dropdownOpen
					? 'rotate-180 text-primary'
					: ''}"
			/>
		</button>

		{#if dropdownOpen}
			<div
				class="absolute top-full right-0 z-50 mt-3 min-w-[240px] origin-top-right"
				in:fly={{ y: -10, duration: 200, easing: quintOut }}
				out:fly={{ y: -10, duration: 150, easing: quintOut }}
				role="menu"
			>
				<div
					class="relative overflow-hidden rounded-2xl border border-white/10 bg-popover/95 p-2 shadow-2xl shadow-black/50 backdrop-blur-xl"
					style="background: linear-gradient(135deg, oklch(0.12 0.02 260 / 0.95) 0%, oklch(0.15 0.03 260 / 0.98) 100%);"
				>
					<div
						class="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent"
					></div>

					<div class="relative">
						<div class="mb-2 flex items-center gap-3 px-3 py-2">
							<div
								class="flex h-10 w-10 items-center justify-center rounded-xl border border-primary/20 bg-primary/10 shadow-inner"
							>
								<User class="h-5 w-5 text-primary" />
							</div>
							<div class="flex flex-col">
								<span class="font-bold text-foreground">{auth.user?.username}</span>
								<span class="text-xs text-muted-foreground">{auth.user?.email}</span>
							</div>
						</div>

						<div
							class="my-2 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"
						></div>

						<div class="space-y-1">
							<a
								href="/settings"
								onclick={closeDropdown}
								class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-muted-foreground transition-all duration-200 hover:bg-white/5 hover:text-foreground"
								role="menuitem"
							>
								<Settings class="h-4 w-4" />
								Settings
							</a>
						</div>

						<div
							class="my-2 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"
						></div>

						<button
							onclick={handleLogout}
							disabled={loggingOut}
							class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 disabled:opacity-50"
							role="menuitem"
						>
							{#if loggingOut}
								<div class="relative">
									<div class="h-4 w-4 animate-spin rounded-full border-2 border-primary/30"></div>
									<div
										class="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-primary"
									></div>
								</div>
								<span class="text-primary">Signing out...</span>
							{:else}
								<LogOut class="h-4 w-4 text-destructive" />
								<span class="text-destructive">Sign out</span>
							{/if}
						</button>
					</div>
				</div>
			</div>

			<button
				class="fixed inset-0 z-40 cursor-default"
				onclick={closeDropdown}
				aria-label="Close dropdown"
				tabindex="-1"
			></button>
		{/if}
	</div>
</nav>

{#if showLogoutMessage}
	<div
		class="fixed inset-0 z-[100] flex items-center justify-center bg-background/80 backdrop-blur-xl"
		in:fade={{ duration: 300 }}
		out:fade={{ duration: 200 }}
	>
		<div
			class="flex flex-col items-center gap-6"
			in:scale={{ duration: 400, easing: backOut, start: 0.9 }}
		>
			<div
				class="relative flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-primary/20 to-primary/5 shadow-2xl shadow-primary/20"
			>
				<Sparkles class="h-10 w-10 animate-pulse text-primary" />
			</div>
			<div class="text-center">
				<h2 class="font-display text-2xl font-black tracking-tight text-foreground">
					You've been signed out
				</h2>
				<p class="mt-2 text-sm text-muted-foreground">Redirecting to login...</p>
			</div>
		</div>
	</div>
{/if}

<style>
	.font-display {
		font-family: var(--font-display);
	}
</style>
