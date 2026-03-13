<script lang="ts">
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import { apiFetch } from "$lib/api";
    import { goto } from "$app/navigation";
    import { auth } from "$lib/stores/auth.svelte";
    import { LockKeyhole, Loader2, Sparkles, LogIn, ShieldCheck, KeyRound, UserRound } from "@lucide/svelte";
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
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const result = await apiFetch('/auth/token', {
                method: 'POST',
                body: formData
            });

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

<div class="flex items-center justify-center min-h-[calc(100vh-4rem)] p-4 relative overflow-hidden">
    <!-- Background Decor -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/5 blur-[120px] rounded-full -z-10 animate-pulse"></div>
    <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/5 blur-[120px] rounded-full -z-10 animate-pulse" style="animation-delay: 2s"></div>

    <div in:fly={{ y: 20, duration: 800 }} class="w-full max-w-md relative z-10">
        <div class="text-center mb-10 space-y-4">
            <div class="inline-flex items-center justify-center p-4 mb-2 rounded-3xl bg-indigo-500/10 border border-indigo-500/20 shadow-[0_0_30px_rgba(99,102,241,0.15)] group hover:scale-110 transition-transform duration-500">
                <ShieldCheck class="w-10 h-10 text-indigo-400" />
            </div>
            <div class="space-y-1">
                <h1 class="text-5xl font-bold tracking-tight text-white drop-shadow-sm font-sans flex items-center justify-center gap-2">
                    Log in to <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">Excelsior</span>
                    <Sparkles class="w-5 h-5 text-indigo-500/50" />
                </h1>
                <p class="text-slate-400 text-lg font-serif italic">Unlock your personalized courses.</p>
            </div>
        </div>

        <Card.Root class="overflow-hidden border-white/10 bg-slate-900/40 backdrop-blur-3xl shadow-2xl ring-1 ring-white/15 rounded-[2.5rem]">
            <Card.Content class="p-10">
                {#if error}
                    <div transition:fade class="mb-8 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-medium flex items-center gap-2">
                        <div class="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0"></div>
                        {error}
                    </div>
                {/if}

                <form onsubmit={handleLogin} class="space-y-6">
                    <div class="space-y-2.5">
                        <Label for="username" class="text-xs font-bold uppercase tracking-[0.2em] text-slate-500 ml-1 flex items-center gap-2">
                            <UserRound class="w-3 h-3" /> Username
                        </Label>
                        <Input 
                            id="username" 
                            type="text" 
                            placeholder="Your Username" 
                            bind:value={username} 
                            required 
                            class="h-14 border-white/10 bg-white/5 focus:bg-white/10 focus:ring-indigo-500/50 transition-all rounded-2xl px-5 text-base"
                        />
                    </div>
                    <div class="space-y-2.5">
                        <div class="flex items-center justify-between ml-1">
                            <Label for="password" class="text-xs font-bold uppercase tracking-[0.2em] text-slate-500 flex items-center gap-2">
                                <KeyRound class="w-3 h-3" /> Password
                            </Label>
                            <a href="/forgot-password" class="text-[10px] text-indigo-400 hover:text-indigo-300 font-black uppercase tracking-widest transition-colors decoration-dotted hover:underline underline-offset-4">Lost Access?</a>
                        </div>
                        <Input 
                            id="password" 
                            type="password" 
                            placeholder="••••••••" 
                            bind:value={password} 
                            required 
                            class="h-14 border-white/10 bg-white/5 focus:bg-white/10 focus:ring-indigo-500/50 transition-all rounded-2xl px-5 text-base"
                        />
                    </div>

                    <Button 
                        type="submit" 
                        class="w-full h-14 bg-indigo-600 hover:bg-indigo-500 text-white font-black text-sm uppercase tracking-[0.2em] transition-all duration-500 rounded-2xl shadow-[0_0_25px_rgba(79,70,229,0.3)] hover:shadow-[0_0_40px_rgba(79,70,229,0.5)] hover:-translate-y-1 relative overflow-hidden group" 
                        disabled={isLoading}
                    >
                        {#if isLoading}
                            <Loader2 class="mr-2 h-5 w-5 animate-spin" />
                            Logging in...
                        {:else}
                            <LogIn class="mr-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                            Log In
                        {/if}
                    </Button>
                </form>
            </Card.Content>
            
            <Card.Footer class="p-8 border-t border-white/5 flex justify-center bg-white/[0.02]">
                <p class="text-slate-500 text-sm font-medium">
                    New to the academy? 
                    <a href="/register" class="text-indigo-400 hover:text-indigo-300 font-bold transition-all decoration-solid hover:underline underline-offset-8">Register here</a>
                </p>
            </Card.Footer>
        </Card.Root>

        <div class="mt-8 text-center" in:fade={{ delay: 1000 }}>
            <div class="text-[10px] text-slate-600 font-bold uppercase tracking-[0.3em] inline-flex items-center gap-2">
                <div class="h-px w-8 bg-slate-800"></div>
                Knowledge Awaits
                <div class="h-px w-8 bg-slate-800"></div>
            </div>
        </div>
    </div>
</div>
