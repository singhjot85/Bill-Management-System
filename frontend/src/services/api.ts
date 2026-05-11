import axios from 'axios';
import { useUIStore } from '@/stores/uiStore';

const api = axios.create({
  // Using relative path so the Vite proxy handles it
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptors to handle global loading overlay
api.interceptors.request.use((config) => {
  // Only show loading if not explicitly disabled in config
  if ((config as any).showLoading !== false) {
    const uiStore = useUIStore();
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
  return Promise.reject(error);
});

export default api;
