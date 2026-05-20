import { defineStore } from "pinia";
import { authService } from '@/services/authService';

const AUTH_TOKEN_KEY = 'auth_token';

const getCookie = (name: string) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift();
    return null;
};

const setCookie = (name: string, value: string, days = 7) => {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = `; expires=${date.toUTCString()}`;
    document.cookie = `${name}=${value || ""}${expires}; path=/; SameSite=Lax`;
};

const deleteCookie = (name: string) => {
    document.cookie = `${name}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
};

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isAuthenticated: false,
        accessToken: getCookie(AUTH_TOKEN_KEY) || null,
        user: null as any,
        loading: false,
    }),
    actions: {
        async refreshToken() {
            // Refresh state from token in cookie
            if (this.accessToken) {
                try {
                    await this.fetchUser();
                } catch (e) {
                    this.destroyToken();
                }
            }
        },
        async login(credentials: any) {
            this.loading = true;
            try {
                const response = await authService.login(credentials);
                // Backend returns { access: '...', refresh: '...' } or similar
                // We use 'access' as the primary token
                this.accessToken = response.access || response.token;
                if (this.accessToken) {
                    setCookie(AUTH_TOKEN_KEY, this.accessToken);
                    await this.fetchUser();
                }
            } finally {
                this.loading = false;
            }
        },
        async fetchUser() {
            if (!this.accessToken) return;
            try {
                const userData = await authService.userDetails();
                this.user = userData;
                this.isAuthenticated = true;
            } catch (e) {
                this.destroyToken();
                throw e;
            }
        },
        async logout() {
            try {
                await authService.logout();
            } finally {
                this.destroyToken();
            }
        },
        destroyToken() {
            this.isAuthenticated = false;
            this.accessToken = null;
            this.user = null;
            deleteCookie(AUTH_TOKEN_KEY);
        }
    }
})
