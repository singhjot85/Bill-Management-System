import { defineStore } from "pinia";
import { authService } from '@/services/authService';

const AUTH_DATA_KEY = 'auth_data';

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
        user: null as any,
        loading: false,
    }),
    actions: {
        async refreshToken() {
            // Refresh state from cookie
            const cookieData = getCookie(AUTH_DATA_KEY);
            if (cookieData) {
                try {
                    this.user = JSON.parse(decodeURIComponent(cookieData));
                    this.isAuthenticated = true;
                    // Optionally fetch fresh user data from backend
                    await this.fetchUser();
                } catch (e) {
                    this.destroyToken();
                }
            }
        },
        async login(credentials: any) {
            this.loading = true;
            try {
                const userData = await authService.login(credentials);
                this.user = userData;
                this.isAuthenticated = true;
                setCookie(AUTH_DATA_KEY, encodeURIComponent(JSON.stringify(userData)));
            } finally {
                this.loading = false;
            }
        },
        async fetchUser() {
            try {
                const userData = await authService.me();
                this.user = userData;
                this.isAuthenticated = true;
                setCookie(AUTH_DATA_KEY, encodeURIComponent(JSON.stringify(userData)));
            } catch (e) {
                this.destroyToken();
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
            this.user = null;
            deleteCookie(AUTH_DATA_KEY);
        }
    }
})
