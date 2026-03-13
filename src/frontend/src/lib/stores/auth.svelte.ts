import { browser } from '$app/environment';

export interface User {
	id: number;
	username: string;
	email: string;
}

class AuthStore {
	token = $state<string | null>(browser ? localStorage.getItem('access_token') : null);
	user = $state<User | null>(null);
	isAuthenticated = $derived(!!this.token);
	isLoaded = $state(false);

	constructor() {
		// No need for initial sync here if we handle it in layout
	}

	login(token: string, user: User) {
		this.token = token;
		this.user = user;
		this.isLoaded = true;
		if (browser) {
			localStorage.setItem('access_token', token);
		}
	}

	logout() {
		this.token = null;
		this.user = null;
		this.isLoaded = false;
		if (browser) {
			localStorage.removeItem('access_token');
		}
	}

	setUser(user: User) {
		this.user = user;
		this.isLoaded = true;
	}
}

export const auth = new AuthStore();
export type { User as AuthUser };
