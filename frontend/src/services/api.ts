import axios from 'axios';

const api = axios.create({
  // Using relative path so the Vite proxy handles it
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
