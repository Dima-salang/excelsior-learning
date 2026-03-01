<script lang="ts">
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import { apiFetch } from "$lib/api";
    import { goto } from "$app/navigation";
    import { cn } from "$lib/utils";
    import { UserPlus, Loader2, Sparkles } from "@lucide/svelte";
    import { fade, fly } from "svelte/transition";

    let username = $state("");
    let email = $state("");
    let password = $state("");
    let isLoading = $state(false);
    let error = $state("");

    async function handleRegister(e: SubmitEvent) {
        e.preventDefault();
        isLoading = true;
        error = "";

        try {
            await apiFetch('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });
            // Redirect to login after successful registration
            goto('/login');
        } catch (err: any) {
            error = err.message || "Failed to register";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="flex items-center justify-center min-h-[calc(100vh-4rem)] p-4">
    <div in:fly={{ y: 20, duration: 800 }} class="w-full max-w-md">
        <div class="text-center mb-8 space-y-2">
            <div class="inline-flex items-center justify-center p-3 mb-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 shadow-[0_0_20px_rgba(34,211,238,0.1)]">
                <UserPlus class="w-8 h-8 text-cyan-400" />
            </div>
            <h1 class="text-4xl font-bold tracking-tight text-white drop-shadow-sm font-sans flex items-center justify-center gap-2">
                Join <span class="text-cyan-400">Excelsior</span>
                <Sparkles class="w-4 h-4 text-cyan-500/50" />
            </h1>
            <p class="text-slate-400 text-lg font-serif italic">Your celestial journey into knowledge begins here.</p>
        </div>

        <Card.Root class="overflow-hidden border-white/5 bg-slate-900/40 backdrop-blur-xl shadow-2xl ring-1 ring-white/10">
            <Card.Content class="p-8">
                {#if error}
                    <div transition:fade class="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                        {error}
                    </div>
                {/if}

                <form onsubmit={handleRegister} class="space-y-5">
                    <div class="space-y-2">
                        <Label for="username" class="text-xs font-semibold uppercase tracking-widest text-slate-500 ml-1">Academic Identifier</Label>
                        <Input 
                            id="username" 
                            type="text" 
                            placeholder="username" 
                            bind:value={username} 
                            required 
                            class="h-12 border-white/10 bg-white/5 focus:bg-white/10 focus:ring-cyan-500/50 transition-all rounded-xl"
                        />
                    </div>
                    <div class="space-y-2">
                        <Label for="email" class="text-xs font-semibold uppercase tracking-widest text-slate-500 ml-1">E-Mail Address</Label>
                        <Input 
                            id="email" 
                            type="email" 
                            placeholder="scholar@excelsior.edu" 
                            bind:value={email} 
                            required 
                            class="h-12 border-white/10 bg-white/5 focus:bg-white/10 focus:ring-cyan-500/50 transition-all rounded-xl"
                        />
                    </div>
                    <div class="space-y-2">
                        <Label for="password" class="text-xs font-semibold uppercase tracking-widest text-slate-500 ml-1">Access Key</Label>
                        <Input 
                            id="password" 
                            type="password" 
                            placeholder="••••••••" 
                            bind:value={password} 
                            required 
                            class="h-12 border-white/10 bg-white/5 focus:bg-white/10 focus:ring-cyan-500/50 transition-all rounded-xl"
                        />
                    </div>

                    <Button 
                        type="submit" 
                        class="w-full h-12 bg-cyan-600 hover:bg-cyan-500 text-white font-bold transition-all duration-300 rounded-xl shadow-[0_0_20px_rgba(8,145,178,0.2)] hover:shadow-[0_0_30px_rgba(8,145,178,0.4)] hover:-translate-y-0.5" 
                        disabled={isLoading}
                    >
                        {#if isLoading}
                            <Loader2 class="mr-2 h-5 w-5 animate-spin" />
                            Initializing...
                        {:else}
                            Ascend Now
                        {/if}
                    </Button>
                </form>
            </Card.Content>
            
            <Card.Footer class="p-6 border-t border-white/5 flex justify-center bg-white/2">
                <p class="text-slate-500 text-sm">
                    Already a member? 
                    <a href="/login" class="text-cyan-400 hover:text-cyan-300 font-semibold transition-colors decoration-dotted hover:underline underline-offset-4">Sign in here</a>
                </p>
            </Card.Footer>
        </Card.Root>
    </div>
</div>
