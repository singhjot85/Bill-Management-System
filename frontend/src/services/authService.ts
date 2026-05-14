import api from './api';
import { ENDPOINTS, getEndpoint } from './endpoints';
import { useTenantStore } from '@/stores/tenantStore';

/**
 * Helper to get the current tenant name from the store.
 */
function getTenant() {
  const tenantStore = useTenantStore();
  return tenantStore.tenantName;
}

export const authService = {
  async login(credentials: any) {
    const endpoint = getEndpoint(ENDPOINTS.LOGIN, getTenant());
    const response = await api.post(endpoint, credentials);
    return response.data;
  },

  async logout() {
    const endpoint = getEndpoint(ENDPOINTS.LOGOUT, getTenant());
    if (endpoint) {
      await api.post(endpoint);
    }
  },

  async userDetails() {
    const endpoint = getEndpoint(ENDPOINTS.USER_DETAILS, getTenant());
    if (endpoint) {
      const response = await api.get(endpoint);
      return response.data;
    }
    return null;
  },

  async passwordReset(data: { email: string }) {
    const endpoint = getEndpoint(ENDPOINTS.PASSWORD_RESET, getTenant());
    const response = await api.post(endpoint, data);
    return response.data;
  },

  async passwordResetConfirm(data: any) {
    const endpoint = getEndpoint(ENDPOINTS.PASSWORD_RESET_CONFIRM, getTenant());
    const response = await api.post(endpoint, data);
    return response.data;
  },

  async passwordChange(data: any) {
    const endpoint = getEndpoint(ENDPOINTS.PASSWORD_CHANGE, getTenant());
    const response = await api.post(endpoint, data);
    return response.data;
  }
};
