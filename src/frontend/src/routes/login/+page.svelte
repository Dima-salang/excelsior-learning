<script lang="ts">
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import { apiFetch } from "$lib/api";
    import { goto } from "$app/navigation";
    import { auth } from "$lib/stores/auth";
    import { LockKeyhole, Loader2, Sparkles, LogIn } from "@lucide/svelte";
    import { fade, fly } from "svelte/transition";

    let username = $state("");
    let password = $state("");
    let isLoading = $state(false);
    let error = $state("");

    async function handleLogin(e: SubmitEvent) {
        e.preventDefault();
        isLoading = true;
        error = "";

        try {
            // OAuth2 Password flow expects x-www-form-urlencoded
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const result = await apiFetch('/auth/token', {
                method: 'POST',
                body: formData
            });

            // After getting token, we should fetch user info if we wanted to be robust,
            // but for now let's just save the token and redirect.
            // We can fetch '/auth/me' after login.
            const userData = await apiFetch('/auth/me', {
                headers: {
                    'Authorization': `Bearer ${result.access_token}`
                }
            });

            auth.login(result.access_token, userData);
            goto('/');
        } catch (err: any) {
            error = err.message || "Invalid credentials or system error";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="flex items-center justify-center min-h-[calc(100vh-4rem)] p-4">
    <div in:fly={{ y: 20, duration: 800 }} class="w-full max-w-md">
        <div class="text-center mb-8 space-y-2">
            <div class="inline-flex items-center justify-center p-3 mb-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 shadow-[0_0_20px_rgba(99,102,241,0.1)]">
                <LockKeyhole class="w-8 h-8 text-indigo-400" />
            </div>
            <h1 class="text-4xl font-bold tracking-tight text-white drop-shadow-sm font-sans flex items-center justify-center gap-2">
                Access <span class="text-indigo-400">Excelsior</span>
                <Sparkles class="w-4 h-4 text-indigo-500/50" />
            </h1>
            <p class="text-slate-400 text-lg font-serif italic">Unlock the gates to infinite wisdom.</p>
        </div>

        <Card.Root class="overflow-hidden border-white/5 bg-slate-900/40 backdrop-blur-xl shadow-2xl ring-1 ring-white/10">
            <Card.Content class="p-8">
                {#if error}
                    <div transition:fade class="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                        {error}
                    </div>
                {/if}

                <form onsubmit={handleLogin} class="space-y-5">
                    <div class="space-y-2">
                        <Label for="username" class="text-xs font-semibold uppercase tracking-widest text-slate-500 ml-1">Academic Identifier</Label>
                        <Input 
                            id="username" 
                            type="text" 
                            placeholder="username" 
                            bind:value={username} 
                            required 
                            class="h-12 border-white/10 bg-white/5 focus:bg-white/10 focus:ring-indigo-500/50 transition-all rounded-xl"
                        />
                    </div>
                    <div class="space-y-2">
                        <div class="flex items-center justify-between ml-1">
                            <Label for="password" class="text-xs font-semibold uppercase tracking-widest text-slate-500">Access Key</Label>
                            <a href="/forgot-password" class="text-[10px] text-indigo-400 hover:text-indigo-300 font-bold uppercase tracking-wider transition-colors">Lost Access?</a>
                        </div>
                        <Input 
                            id="password" 
                            type="password" 
                            placeholder="••••••••" 
                            bind:value={password} 
                            required 
                            class="h-12 border-white/10 bg-white/5 focus:bg-white/10 focus:ring-indigo-500/50 transition-all rounded-xl"
                        />
                    </div>

                    <Button 
                        type="submit" 
                        class="w-full h-12 bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-all duration-300 rounded-xl shadow-[0_0_20px_rgba(79,70,229,0.2)] hover:shadow-[0_0_30px_rgba(79,70,229,0.4)] hover:-translate-y-0.5" 
                        disabled={isLoading}
                    >
                        {#if isLoading}
                            <Loader2 class="mr-2 h-5 w-5 animate-spin" />
                            Synchronizing...
                        {:else}
                            <LogIn class="mr-2 h-5 w-5" />
                            Enter Portal
                        {/if}
                    </Button>
                </form>
            </Card.Content>
            
            <Card.Footer class="p-6 border-t border-white/5 flex justify-center bg-white/2">
                <p class="text-slate-500 text-sm">
                    New to the academy? 
                    <a href="/register" class="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors decoration-dotted hover:underline underline-offset-4">Register here</a>
                </p>
            </Card.Footer>
        </Card.Root>
    </div>
</div>
