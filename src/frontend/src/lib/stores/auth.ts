import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface User {
	username: string;
	email: string;
	id: number;
}

function createAuth() {
	const { subscribe, set, update } = writable<{
		token: string | null;
		user: User | null;
		isAuthenticated: boolean;
	}>({
		token: browser ? localStorage.getItem('access_token') : null,
		user: null,
		isAuthenticated: false
	});

	return {
		subscribe,
		login: (token: string, user: User) => {
			if (browser) {
				localStorage.setItem('access_token', token);
			}
			set({ token, user, isAuthenticated: true });
		},
		logout: () => {
			if (browser) {
				localStorage.removeItem('access_token');
			}
			set({ token: null, user: null, isAuthenticated: false });
		},
		setUser: (user: User) => {
			update((state) => ({ ...state, user, isAuthenticated: true }));
		}
	};
}

export const auth = createAuth();
