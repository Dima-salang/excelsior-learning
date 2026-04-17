<script lang="ts">
	import { marked } from 'marked';
	import markedKatex from 'marked-katex-extension';
	import { cn } from '$lib/utils';

	marked.use(markedKatex({ throwOnError: false }));

	interface MarkdownRendererProps {
		content: string;
		class?: string;
		compact?: boolean;
	}

	let { content, class: className = '', compact = false }: MarkdownRendererProps = $props();

	let processedContent = $derived.by(() => {
		if (!content || typeof content !== 'string') return '';
		const trimmed = content.trim();
		if (!trimmed) return '';
		return trimmed;
	});

	let rendered = $derived(processedContent ? marked.parse(processedContent, { breaks: true, gfm: true }) : '');

	let containerClass = $derived(compact ? 'prose-excelsior-compact max-w-none' : 'prose-excelsior max-w-none');
</script>

<article class={cn(containerClass, className)}>
	{@html rendered}
</article>

<style>
	:global(.prose-excelsior),
	:global(.prose-excelsior-compact) {
		overflow-wrap: break-word;
		word-wrap: break-word;
	}

	:global(.prose-excelsior > *),
	:global(.prose-excelsior-compact > *) {
		overflow-wrap: break-word;
		word-wrap: break-word;
	}

	:global(.prose-excelsior) {
		--tw-prose-body: var(--prose-body);
		--tw-prose-headings: var(--prose-headings);
		--tw-prose-links: var(--prose-links);
		--tw-prose-bold: var(--foreground);
		--tw-prose-counters: var(--primary);
		--tw-prose-bullets: var(--muted-foreground);
		--tw-prose-hr: var(--border);
		--tw-prose-quotes: var(--foreground);
		--tw-prose-quote-borders: var(--primary);
		--tw-prose-captions: var(--muted-foreground);
		--tw-prose-code: var(--prose-code);
		--tw-prose-pre-code: var(--foreground);
		--tw-prose-pre-bg: var(--prose-pre-bg);
		--tw-prose-th-borders: var(--border);
		--tw-prose-td-borders: var(--border);
		color-scheme: dark;
	}

	:global(.prose-excelsior h1),
	:global(.prose-excelsior h2),
	:global(.prose-excelsior h3) {
		font-family: var(--font-display);
		letter-spacing: -0.05em;
		text-transform: uppercase;
		font-weight: 800;
		margin-top: 2em;
		margin-bottom: 0.75em;
		line-height: 1.1;
		color: var(--prose-headings);
	}

	:global(.prose-excelsior h1) {
		font-size: 2.5rem;
	}

	:global(.prose-excelsior h2) {
		font-size: 1.75rem;
	}

	:global(.prose-excelsior h3) {
		font-size: 1.25rem;
	}

	:global(.prose-excelsior p) {
		font-family: var(--font-sans);
		font-size: 1.125rem;
		line-height: 1.8;
		margin-top: 1em;
		margin-bottom: 1em;
		color: var(--prose-body);
	}

	:global(.prose-excelsior strong) {
		color: var(--foreground);
		font-weight: 700;
	}

	:global(.prose-excelsior a) {
		color: var(--primary);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 3px;
	}

	:global(.prose-excelsior a:hover) {
		color: var(--primary);
		opacity: 0.8;
	}

	:global(.prose-excelsior blockquote) {
		border-left: 4px solid var(--primary);
		background: linear-gradient(135deg, var(--primary) 0%, transparent 100%);
		padding: 1.5rem 2rem;
		border-radius: 0 1.5rem 1.5rem 0;
		margin: 2rem 0;
		font-style: italic;
		color: var(--prose-blockquote);
	}

	:global(.prose-excelsior blockquote p) {
		margin: 0;
	}

	:global(.prose-excelsior pre) {
		background: var(--prose-pre-bg);
		border: 1px solid var(--border);
		padding: 1.5rem;
		border-radius: 1rem;
		margin: 2rem 0;
		overflow-x: auto;
		box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
	}

	:global(.prose-excelsior code) {
		font-family: 'JetBrains Mono', 'Fira Code', monospace;
		padding: 0.2rem 0.4rem;
		border-radius: 0.4rem;
		font-size: 0.875em;
		color: var(--prose-code);
		background: var(--prose-code-bg);
	}

	:global(.prose-excelsior pre code) {
		background: transparent;
		padding: 0;
		color: var(--foreground);
		line-height: 1.6;
		font-size: 0.875rem;
	}

	:global(.prose-excelsior ul),
	:global(.prose-excelsior ol) {
		margin-top: 1.5em;
		margin-bottom: 1.5em;
		padding-left: 1.5em;
	}

	:global(.prose-excelsior ul) {
		list-style-type: disc;
	}

	:global(.prose-excelsior ol) {
		list-style-type: decimal;
	}

	:global(.prose-excelsior li) {
		margin-top: 0.5em;
		margin-bottom: 0.5em;
		font-family: var(--font-sans);
		font-size: 1.125rem;
		line-height: 1.7;
		color: var(--prose-body);
	}

	:global(.prose-excelsior li::marker) {
		color: var(--primary);
	}

	:global(.prose-excelsior table) {
		width: 100%;
		border-collapse: separate;
		border-spacing: 0;
		margin: 2rem 0;
		border-radius: 1rem;
		overflow: hidden;
		border: 1px solid var(--border);
	}

	:global(.prose-excelsior thead) {
		background: var(--muted);
	}

	:global(.prose-excelsior th) {
		padding: 1rem 1.25rem;
		text-align: left;
		font-family: var(--font-display);
		font-weight: 700;
		font-size: 0.75rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--foreground);
		border-bottom: 2px solid var(--border);
		background: var(--primary);
	}

	:global(.prose-excelsior td) {
		padding: 1rem 1.25rem;
		font-family: var(--font-sans);
		font-size: 1rem;
		color: var(--prose-body);
		border-bottom: 1px solid var(--border);
	}

	:global(.prose-excelsior tr:last-child td) {
		border-bottom: none;
	}

	:global(.prose-excelsior tbody tr:hover) {
		background: var(--muted);
	}

	:global(.prose-excelsior hr) {
		border: none;
		height: 1px;
		background: linear-gradient(90deg, transparent, var(--border), transparent);
		margin: 3rem 0;
	}

	:global(.prose-excelsior img) {
		max-width: 100%;
		height: auto;
		border-radius: 1rem;
		margin: 1.5rem 0;
	}

	:global(.katex-display) {
		overflow-x: auto;
		padding: 1rem 0;
	}

	/* Compact variant for flashcards and small contexts */
	:global(.prose-excelsior-compact) {
		--tw-prose-body: var(--prose-body);
		--tw-prose-headings: var(--prose-headings);
		--tw-prose-links: var(--prose-links);
		--tw-prose-bold: var(--foreground);
		--tw-prose-counters: var(--primary);
		--tw-prose-bullets: var(--muted-foreground);
		--tw-prose-hr: var(--border);
		--tw-prose-quotes: var(--foreground);
		--tw-prose-quote-borders: var(--primary);
		--tw-prose-captions: var(--muted-foreground);
		--tw-prose-code: var(--prose-code);
		--tw-prose-pre-code: var(--foreground);
		--tw-prose-pre-bg: var(--prose-pre-bg);
		--tw-prose-th-borders: var(--border);
		--tw-prose-td-borders: var(--border);
		color-scheme: dark;
	}

	:global(.prose-excelsior-compact p) {
		font-family: var(--font-sans);
		font-size: 1rem;
		line-height: 1.6;
		margin-top: 0.5em;
		margin-bottom: 0.5em;
		color: var(--prose-body);
	}

	:global(.prose-excelsior-compact h1),
	:global(.prose-excelsior-compact h2),
	:global(.prose-excelsior-compact h3) {
		font-family: var(--font-display);
		font-weight: 700;
		margin-top: 1em;
		margin-bottom: 0.5em;
		color: var(--prose-headings);
	}

	:global(.prose-excelsior-compact strong) {
		color: var(--foreground);
		font-weight: 700;
	}

	:global(.prose-excelsior-compact a) {
		color: var(--primary);
		text-decoration: underline;
	}

	:global(.prose-excelsior-compact blockquote) {
		border-left: 3px solid var(--primary);
		padding-left: 1rem;
		margin: 1rem 0;
		font-style: italic;
		color: var(--prose-blockquote);
	}

	:global(.prose-excelsior-compact pre) {
		background: var(--prose-pre-bg);
		border: 1px solid var(--border);
		padding: 1rem;
		border-radius: 0.75rem;
		margin: 1rem 0;
		overflow-x: auto;
	}

	:global(.prose-excelsior-compact code) {
		font-family: 'JetBrains Mono', 'Fira Code', monospace;
		padding: 0.15rem 0.3rem;
		border-radius: 0.25rem;
		font-size: 0.85em;
		color: var(--prose-code);
		background: var(--prose-code-bg);
	}

	:global(.prose-excelsior-compact pre code) {
		background: transparent;
		padding: 0;
		color: var(--foreground);
		font-size: 0.8rem;
	}

	:global(.prose-excelsior-compact ul),
	:global(.prose-excelsior-compact ol) {
		margin-top: 0.5em;
		margin-bottom: 0.5em;
		padding-left: 1.25em;
	}

	:global(.prose-excelsior-compact li) {
		margin-top: 0.25em;
		margin-bottom: 0.25em;
		font-size: 1rem;
		line-height: 1.5;
		color: var(--prose-body);
	}

	:global(.prose-excelsior-compact table) {
		width: 100%;
		border-collapse: collapse;
		margin: 1rem 0;
		font-size: 0.875rem;
	}

	:global(.prose-excelsior-compact th),
	:global(.prose-excelsior-compact td) {
		padding: 0.5rem 0.75rem;
		border: 1px solid var(--border);
	}

	:global(.prose-excelsior-compact th) {
		background: var(--muted);
		font-weight: 600;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	:global(.prose-excelsior-compact hr) {
		margin: 1.5rem 0;
	}
</style>