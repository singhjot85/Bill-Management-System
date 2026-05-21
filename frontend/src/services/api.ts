import axios from 'axios';
import { useUIStore } from '@/stores/uiStore';
import { useAuthStore } from '@/stores/authStore';
import { useTenantStore } from '@/stores/tenantStore';
import router from '@/router';

const api = axios.create({
  // Using relative path so the Vite proxy handles it
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

// Add interceptors to handle global loading overlay and tenant context
api.interceptors.request.use((config) => {
  const tenantStore = useTenantStore();
  const uiStore = useUIStore();
  const authStore = useAuthStore();

  // Add tenant name to headers
  if (tenantStore.tenantName) {
    config.headers['X-Tenant'] = tenantStore.tenantName;
  }

  // Add Authorization header if token exists
  if (authStore.accessToken) {
    config.headers['Authorization'] = `Token ${authStore.accessToken}`;
  }

  // Only show loading if not explicitly disabled in config
  if ((config as any).showLoading !== false) {
    uiStore.startLoading();
  }
  return config;
}, (error) => {
  const uiStore = useUIStore();
  uiStore.stopLoading();
  return Promise.reject(error);
});

api.interceptors.response.use((response) => {
  const uiStore = useUIStore();
  uiStore.stopLoading();
  return response;
}, (error) => {
  const uiStore = useUIStore();
  uiStore.stopLoading();

  if (error.response && error.response.status === 401) {
    const authStore = useAuthStore();
    authStore.destroyToken();
    router.push({ name: 'Login' });
  }

  return Promise.reject(error);
});

export default api;
