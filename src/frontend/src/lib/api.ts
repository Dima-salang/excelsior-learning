import { browser } from '$app/environment';

export const API_BASE_URL = 'http://localhost:8000';

export async function apiFetch(path: string, options: RequestInit = {}) {
	const token = browser ? localStorage.getItem('access_token') : null;

	const headers = {
		...options.headers
	} as Record<string, string>;

	// Only set application/json if not using URLSearchParams and not already set
	if (!(options.body instanceof URLSearchParams) && !headers['Content-Type'] && options.body) {
		headers['Content-Type'] = 'application/json';
	}

	if (token && !headers['Authorization']) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	const response = await fetch(`${API_BASE_URL}${path}`, {
		...options,
		headers
	});

	if (!response.ok) {
		let errorData = {} as any;
		try {
			errorData = await response.json();
		} catch (e) {
			errorData = { detail: response.statusText };
		}
		throw new Error(errorData.detail || 'API request failed');
	}

	if (response.status === 204) return null;
	return response.json();
}
