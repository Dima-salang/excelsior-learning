<script lang="ts">
	import { BrainCircuit, ChevronDown, LogOut, User, Settings, Sparkles, BookOpen, Layers, MessageCircle } from 'lucide-svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { page } from '$app/state';
	import { fade, fly, scale } from 'svelte/transition';
	import { quintOut, backOut } from 'svelte/easing';

	let dropdownOpen = $state(false);
	let loggingOut = $state(false);
	let showLogoutMessage = $state(false);

	const isActive = (path: string) => {
		if (path === '/dashboard') {
			return page.url.pathname === '/dashboard' || page.url.pathname === '/';
		}
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
	class="sticky top-0 z-50 flex w-full items-center justify-between border-b border-border bg-background/95 px-6 py-3 backdrop-blur-sm md:px-8"
	in:fade={{ duration: 300 }}
>
	<div class="flex items-center gap-10">
		<a href="/dashboard" class="flex items-center gap-2">
			<div class="flex flex-col">
				<span class="font-display text-lg font-bold tracking-tight">EXCELSIOR</span>
				<span class="text-[9px] font-medium tracking-widest text-primary uppercase">Academy</span>
			</div>
		</a>
		<div class="hidden items-center gap-1 text-sm md:flex">
			<a
				href="/dashboard"
				class="relative rounded-md px-3 py-2 transition-colors hover:bg-muted {isActive('/dashboard')
					? 'font-medium text-foreground'
					: 'text-muted-foreground'}"
			>
				Dashboard
			</a>
			<a
				href="/lectures"
				class="relative rounded-md px-3 py-2 transition-colors hover:bg-muted {isActive('/lectures')
					? 'font-medium text-foreground'
					: 'text-muted-foreground'}"
			>
				Courses
			</a>
			<a
				href="/decks"
				class="relative rounded-md px-3 py-2 transition-colors hover:bg-muted {isActive('/decks')
					? 'font-medium text-foreground'
					: 'text-muted-foreground'}"
			>
				Decks
			</a>
			<a
				href="/quiz"
				class="relative rounded-md px-3 py-2 transition-colors hover:bg-muted {isActive('/quiz')
					? 'font-medium text-foreground'
					: 'text-muted-foreground'}"
			>
				Quiz
			</a>
			<a
				href="/chat"
				class="relative rounded-md px-3 py-2 transition-colors hover:bg-muted {isActive('/chat')
					? 'font-medium text-foreground'
					: 'text-muted-foreground'}"
			>
				AI Tutor
			</a>
			<a
				href="/generate"
				class="relative rounded-md px-3 py-2 transition-colors hover:bg-muted {isActive('/generate')
					? 'font-medium text-foreground'
					: 'text-muted-foreground'}"
			>
				Generate
			</a>
		</div>
	</div>

	<div class="relative flex items-center gap-2">
		<button
			onclick={toggleDropdown}
			onkeydown={(e) => e.key === 'Enter' && toggleDropdown()}
			class="flex items-center gap-2 rounded-full px-3 py-1.5 transition-colors hover:bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
			aria-expanded={dropdownOpen}
			aria-haspopup="true"
		>
			<span class="text-sm font-medium">{auth.user?.username || 'Guest'}</span>
			<div
				class="flex h-8 w-8 items-center justify-center rounded-full border border-border bg-secondary"
			>
				<span class="text-xs font-semibold text-primary uppercase">
					{auth.user?.username?.[0] || 'G'}
				</span>
			</div>
			<ChevronDown
				class="h-4 w-4 text-muted-foreground transition-transform {dropdownOpen
					? 'rotate-180'
					: ''}"
			/>
		</button>

		{#if dropdownOpen}
			<div
				class="absolute top-full right-0 z-50 mt-2 min-w-[200px] origin-top-right"
				in:fly={{ y: -5, duration: 150 }}
				out:fly={{ y: -5, duration: 100 }}
				role="menu"
			>
				<div class="rounded-lg border border-border bg-popover p-1 shadow-lg">
					<div class="flex items-center gap-3 px-3 py-2">
						<div
							class="flex h-8 w-8 items-center justify-center rounded-full border border-border bg-secondary"
						>
							<User class="h-4 w-4 text-muted-foreground" />
						</div>
						<div class="flex flex-col">
							<span class="text-sm font-medium">{auth.user?.username}</span>
							<span class="text-xs text-muted-foreground">{auth.user?.email}</span>
						</div>
					</div>

					<div class="my-1 h-px bg-border"></div>

					<a
						href="/settings"
						onclick={closeDropdown}
						class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
						role="menuitem"
					>
						<Settings class="h-4 w-4" />
						Settings
					</a>

					<a
						href="/providers"
						onclick={closeDropdown}
						class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground md:hidden"
						role="menuitem"
					>
						AI Models
					</a>

					<div class="my-1 h-px bg-border"></div>

					<button
						onclick={handleLogout}
						disabled={loggingOut}
						class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-destructive transition-colors hover:bg-destructive/10 disabled:opacity-50"
						role="menuitem"
					>
						{#if loggingOut}
							<LogOut class="h-4 w-4 animate-pulse" />
							Signing out...
						{:else}
							<LogOut class="h-4 w-4" />
							Sign out
						{/if}
					</button>
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
		in:fade={{ duration: 200 }}
		out:fade={{ duration: 150 }}
	>
		<div
			class="flex flex-col items-center gap-4"
			in:scale={{ duration: 300, easing: backOut, start: 0.95 }}
		>
			<div class="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
				<Sparkles class="h-8 w-8 animate-pulse text-primary" />
			</div>
			<div class="text-center">
				<h2 class="font-semibold">You've been signed out</h2>
				<p class="text-sm text-muted-foreground">Redirecting to login...</p>
			</div>
		</div>
	</div>
{/if}
