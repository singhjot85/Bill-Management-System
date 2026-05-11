import api from './api';

export const authService = {
  async login(credentials: any) {
    const response = await api.post('/auth/login/', credentials);
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
