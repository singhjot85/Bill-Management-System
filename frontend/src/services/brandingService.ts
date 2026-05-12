import api from './api';
import defaultLogo from '@/assets/img/bill-invoice.svg';

export const brandingService = {
  async getBranding() {
    // This will hit /api/branding/
    // The backend identifies the tenant by the Host header
    try {
      const response = await api.get('/branding/');
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
