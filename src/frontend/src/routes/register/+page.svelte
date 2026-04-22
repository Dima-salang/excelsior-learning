<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { apiFetch } from '$lib/api';
	import { goto } from '$app/navigation';
	import { UserPlus, Check, X, AlertCircle } from '@lucide/svelte';
	import { fade, fly } from 'svelte/transition';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let isLoading = $state(false);
	let error = $state('');

	function getPasswordStrength(pwd: string): { score: number; label: string; color: string } {
		if (!pwd) return { score: 0, label: '', color: '' };

		let score = 0;
		if (pwd.length >= 8) score += 25;
		if (pwd.length >= 12) score += 15;
		if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score += 20;
		if (/\d/.test(pwd)) score += 20;
		if (/[^a-zA-Z0-9]/.test(pwd)) score += 20;

		if (score >= 80) return { score, label: 'Strong', color: 'bg-success' };
		if (score >= 50) return { score, label: 'Medium', color: 'bg-warning' };
		return { score, label: 'Weak', color: 'bg-destructive' };
	}

	let passwordStrength = $derived(getPasswordStrength(password));
	let passwordsMatch = $derived(password && confirmPassword ? password === confirmPassword : null);
	let canSubmit = $derived(
		username.trim() && 
		email.trim() && 
		password && 
		confirmPassword &&
		passwordsMatch === true &&
		passwordStrength.score >= 50
	);

	const validationChecks = $derived([
		{ label: 'At least 8 characters', valid: password.length >= 8 },
		{ label: 'Contains uppercase & lowercase', valid: /[a-z]/.test(password) && /[A-Z]/.test(password) },
		{ label: 'Contains a number', valid: /\d/.test(password) },
		{ label: 'Contains special character', valid: /[^a-zA-Z0-9]/.test(password) }
	]);

	async function handleRegister(e: SubmitEvent) {
		e.preventDefault();
		if (!canSubmit) return;
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
						{#if password}
							<div class="mt-2 space-y-2">
								<div class="flex h-1.5 w-full overflow-hidden rounded-full bg-muted">
									<div
										class="transition-all {passwordStrength.color}"
										style="width: {passwordStrength.score}%"
									></div>
								</div>
								<div class="flex items-center justify-between text-[10px]">
									<span class="{passwordStrength.color === 'bg-success' ? 'text-success' : passwordStrength.color === 'bg-warning' ? 'text-warning' : 'text-destructive'} font-medium">
										{passwordStrength.label}
									</span>
									<span class="text-muted-foreground">{passwordStrength.score}%</span>
								</div>
							</div>
						{/if}
					</div>

					{#if password}
						<div class="space-y-2 rounded-lg border border-border bg-muted/30 p-3">
							<div class="mb-2 text-[10px] font-bold tracking-widest text-muted-foreground uppercase">
								Password Requirements
							</div>
							<div class="grid grid-cols-2 gap-2">
								{#each validationChecks as check}
									<div class="flex items-center gap-2 text-xs">
										{#if check.valid}
											<Check class="h-3 w-3 text-success" />
										{:else}
											<X class="h-3 w-3 text-muted-foreground/50" />
										{/if}
										<span class="{check.valid ? 'text-success' : 'text-muted-foreground/70'}">
											{check.label}
										</span>
									</div>
								{/each}
							</div>
						</div>
					{/if}

					<div class="space-y-2">
						<Label for="confirmPassword" class="text-sm font-medium">Confirm Password</Label>
						<Input
							id="confirmPassword"
							type="password"
							placeholder="Confirm your password"
							bind:value={confirmPassword}
							required
							class="h-11"
						/>
						{#if confirmPassword && passwordsMatch !== null}
							<div class="flex items-center gap-2 text-xs">
								{#if passwordsMatch}
									<Check class="h-3 w-3 text-success" />
									<span class="text-success">Passwords match</span>
								{:else}
									<AlertCircle class="h-3 w-3 text-destructive" />
									<span class="text-destructive">Passwords do not match</span>
								{/if}
							</div>
						{/if}
					</div>

					<Button type="submit" class="w-full" disabled={isLoading || !canSubmit}>
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
