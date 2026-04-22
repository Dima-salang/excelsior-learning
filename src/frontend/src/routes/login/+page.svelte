<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { apiFetch } from '$lib/api';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth.svelte';
	import { LogIn, ShieldCheck } from 'lucide-svelte';
	import { fade, fly } from 'svelte/transition';

	let username = $state('');
	let password = $state('');
	let isLoading = $state(false);
	let error = $state('');

	async function handleLogin(e: SubmitEvent) {
		e.preventDefault();
		isLoading = true;
		error = '';

		try {
			const formData = new URLSearchParams();
			formData.append('username', username);
			formData.append('password', password);

			const result = await apiFetch('/auth/token', {
				method: 'POST',
				body: formData
			});

			const userData = await apiFetch('/auth/me', {
				headers: {
					Authorization: `Bearer ${result.access_token}`
				}
			});

			auth.login(result.access_token, userData);
			goto('/');
		} catch (err: any) {
			error = err.message || 'Invalid credentials or system error';
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
				<ShieldCheck class="h-8 w-8 text-primary" />
			</div>
			<h1 class="text-3xl font-bold tracking-tight">Log in to Excelsior</h1>
			<p class="mt-2 text-muted-foreground">Unlock your personalized learning experience.</p>
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

				<form onsubmit={handleLogin} class="space-y-5">
					<div class="space-y-2">
						<Label for="username" class="text-sm font-medium">Username</Label>
						<Input
							id="username"
							type="text"
							placeholder="Enter your username"
							bind:value={username}
							required
							class="h-11"
						/>
					</div>
					<div class="space-y-2">
						<Label for="password" class="text-sm font-medium">Password</Label>
						<Input
							id="password"
							type="password"
							placeholder="Enter your password"
							bind:value={password}
							required
							class="h-11"
						/>
					</div>

					<Button type="submit" class="w-full" disabled={isLoading}>
						{#if isLoading}
							<LogIn class="mr-2 h-4 w-4 animate-spin" />
							Logging in...
						{:else}
							<LogIn class="mr-2 h-4 w-4" />
							Log In
						{/if}
					</Button>
				</form>
			</Card.Content>

			<Card.Footer class="flex justify-center border-t border-border p-6">
				<p class="text-sm text-muted-foreground">
					New to the academy?
					<a href="/register" class="font-medium text-primary hover:underline">Register here</a>
				</p>
			</Card.Footer>
		</Card.Root>
	</div>
</div>
