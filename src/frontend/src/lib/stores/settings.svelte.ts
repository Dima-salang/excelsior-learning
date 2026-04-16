import { browser } from '$app/environment';

export type Theme = 'dark' | 'light' | 'system';

class SettingsStore {
	selectedProviderId = $state<number | null>(
		browser
			? localStorage.getItem('selected_provider_id')
				? Number(localStorage.getItem('selected_provider_id'))
				: null
			: null
	);

	theme = $state<Theme>(
		browser
			? (localStorage.getItem('theme') as Theme) || 'dark'
			: 'dark'
	);

	setProvider(id: number) {
		this.selectedProviderId = id;
		if (browser) {
			localStorage.setItem('selected_provider_id', id.toString());
		}
	}

	setTheme(newTheme: Theme) {
		this.theme = newTheme;
		if (browser) {
			localStorage.setItem('theme', newTheme);
			this.applyTheme(newTheme);
		}
	}

	applyTheme(theme: Theme) {
		if (!browser) return;

		const root = document.documentElement;
		const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

		root.classList.remove('dark');

		if (theme === 'system') {
			if (systemDark) {
				root.classList.add('dark');
			}
		} else if (theme === 'dark') {
			root.classList.add('dark');
		}
	}

	initTheme() {
		if (browser) {
			this.applyTheme(this.theme);
		}
	}
}

export const settings = new SettingsStore();
