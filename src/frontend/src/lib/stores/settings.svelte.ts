import { browser } from '$app/environment';

class SettingsStore {
	selectedProviderId = $state<number | null>(
		browser
			? localStorage.getItem('selected_provider_id')
				? Number(localStorage.getItem('selected_provider_id'))
				: null
			: null
	);

	setProvider(id: number) {
		this.selectedProviderId = id;
		if (browser) {
			localStorage.setItem('selected_provider_id', id.toString());
		}
	}
}

export const settings = new SettingsStore();
