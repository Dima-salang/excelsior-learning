<script lang="ts">
	import { marked } from 'marked';
	import markedKatex from 'marked-katex-extension';
	import { cn } from '$lib/utils';

	marked.use(markedKatex({ throwOnError: false }));

	interface MarkdownContentProps {
		content: string;
		class?: string;
	}

	let { content, class: className = '' }: MarkdownContentProps = $props();

	let rendered = $derived(content ? marked.parse(content, { breaks: true, gfm: true }) : '');
</script>

<span class={cn('markdown-content', className)}>
	{@html rendered}
</span>

<style>
	:global(.markdown-content) {
		line-height: 1.625;
	}

	:global(.markdown-content p) {
		margin-bottom: 0.5rem;
	}

	:global(.markdown-content p:last-child) {
		margin-bottom: 0;
	}

	:global(.markdown-content code) {
		font-family: 'JetBrains Mono', 'Fira Code', monospace;
		padding: 0.125rem 0.375rem;
		border-radius: 0.25rem;
		background-color: var(--prose-code-bg);
		color: var(--prose-code);
		font-size: 0.9em;
	}

	:global(.markdown-content pre) {
		padding: 1rem;
		border-radius: 0.75rem;
		background-color: var(--prose-pre-bg);
		border: 1px solid var(--border);
		margin: 1rem 0;
		overflow-x: auto;
	}

	:global(.markdown-content pre code) {
		background-color: transparent;
		padding: 0;
	}

	:global(.markdown-content ul),
	:global(.markdown-content ol) {
		margin-left: 1.25rem;
		margin-bottom: 0.5rem;
	}

	:global(.markdown-content ul) {
		list-style-type: disc;
	}

	:global(.markdown-content ol) {
		list-style-type: decimal;
	}

	:global(.markdown-content strong) {
		font-weight: 700;
		color: var(--foreground);
	}

	:global(.markdown-content em) {
		font-style: italic;
	}

	:global(.markdown-content a) {
		color: var(--primary);
		text-decoration: underline;
	}

	:global(.markdown-content blockquote) {
		border-left: 3px solid var(--primary);
		padding-left: 1rem;
		margin: 1rem 0;
		color: var(--muted-foreground);
		font-style: italic;
	}
</style>