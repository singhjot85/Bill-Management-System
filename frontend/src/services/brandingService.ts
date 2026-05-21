import api from './api';
import { ENDPOINTS, getEndpoint } from './endpoints';
import { useTenantStore } from '@/stores/tenantStore';

export const brandingService = {
  async getBranding() {
    const tenantStore = useTenantStore();
    const queryParams = {tenant: tenantStore.tenantName}
    const endpoint = getEndpoint(ENDPOINTS.BRANDING, tenantStore.tenantName, queryParams);

    try {
      const response = await api.get(endpoint);
      return response.data;
    } catch (error) {
      console.warn('Branding fetch failed, using defaults');
      return {
        contact_info: 'support@example.com'
      };
    }
  }
};
