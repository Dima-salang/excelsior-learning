<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { apiFetch } from '$lib/api';
	import { goto } from '$app/navigation';
	import { UserPlus } from 'lucide-svelte';
	import { fade, fly } from 'svelte/transition';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let isLoading = $state(false);
	let error = $state('');

	async function handleRegister(e: SubmitEvent) {
		e.preventDefault();
		isLoading = true;
		error = '';

		try {
			await apiFetch('/auth/register', {
				method: 'POST',
				body: JSON.stringify({ username, email, password })
			});
			goto('/login');
		} catch (err: any) {
			error = err.message || 'Failed to register';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="flex min-h-[calc(100vh-4rem)] items-center justify-center p-6">
	<div in:fly={{ y: 20, duration: 400 }} class="w-full max-w-md">
		<div class="mb-8 text-center">
			<div
				class="mb-4 inline-flex items-center justify-center rounded-2xl border border-border bg-primary/10 p-3"
			>
				<UserPlus class="h-8 w-8 text-primary" />
			</div>
			<h1 class="text-3xl font-bold tracking-tight">Join Excelsior</h1>
			<p class="mt-2 text-muted-foreground">Your journey into knowledge begins here.</p>
		</div>

		<Card.Root class="overflow-hidden rounded-xl border-border">
			<Card.Content class="p-6">
				{#if error}
					<div
						transition:fade
						class="mb-6 rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive"
					>
						{error}
					</div>
				{/if}

				<form onsubmit={handleRegister} class="space-y-5">
					<div class="space-y-2">
						<Label for="username" class="text-sm font-medium">Username</Label>
						<Input
							id="username"
							type="text"
							placeholder="Choose a username"
							bind:value={username}
							required
							class="h-11"
						/>
					</div>
					<div class="space-y-2">
						<Label for="email" class="text-sm font-medium">Email</Label>
						<Input
							id="email"
							type="email"
							placeholder="you@example.com"
							bind:value={email}
							required
							class="h-11"
						/>
					</div>
					<div class="space-y-2">
						<Label for="password" class="text-sm font-medium">Password</Label>
						<Input
							id="password"
							type="password"
							placeholder="Create a password"
							bind:value={password}
							required
							class="h-11"
						/>
					</div>

					<Button type="submit" class="w-full" disabled={isLoading}>
						{#if isLoading}
							<UserPlus class="mr-2 h-4 w-4 animate-spin" />
							Creating account...
						{:else}
							<UserPlus class="mr-2 h-4 w-4" />
							Create Account
						{/if}
					</Button>
				</form>
			</Card.Content>

			<Card.Footer class="flex justify-center border-t border-border p-6">
				<p class="text-sm text-muted-foreground">
					Already have an account?
					<a href="/login" class="font-medium text-primary hover:underline">Sign in</a>
				</p>
			</Card.Footer>
		</Card.Root>
	</div>
</div>
