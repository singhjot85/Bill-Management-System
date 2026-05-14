import api from './api';
import { ENDPOINTS, getEndpoint } from './endpoints';

export const authService = {
  async login(credentials: any) {
    const apiEndpoint = getEndpoint(ENDPOINTS.LOGIN)
    const response = await api.post(apiEndpoint, credentials);
    return response.data;
  },

  async logout() {
    await api.post('/auth/logout/');
  },

  async me() {
    const response = await api.get('/auth/me/');
    return response.data;
  }
};
