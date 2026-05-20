import api from './api';
import { ENDPOINTS, getEndpoint } from './endpoints';
import { useTenantStore } from '@/stores/tenantStore';
import defaultLogo from '@/assets/img/bill-invoice.svg';

export const brandingService = {
  async getBranding() {
    const tenantStore = useTenantStore();
    const endpoint = getEndpoint(ENDPOINTS.BRANDING, tenantStore.tenantName);

    try {
      const response = await api.get(endpoint);
      return response.data;
    } catch (error) {
      console.warn('Branding fetch failed, using defaults');
      return {
        tenant_name: 'Invoice Management',
        logo_url: defaultLogo,
        contact_info: 'support@example.com'
      };
    }
  }
};
