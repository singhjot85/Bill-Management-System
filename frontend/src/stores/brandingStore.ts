import { defineStore } from 'pinia';
import { brandingService } from '@/services/brandingService';
import defaultLogo from '@/assets/defaultAssets/bill-invoice.svg';

export const useBrandingStore = defineStore('branding', {
  state: () => ({
    tenantName: 'Invoice Management',
    logoUrl: defaultLogo,
    contactInfo: '',
    isLoaded: false,
    isPrivateFlow: false,
    theme: localStorage.getItem('user-theme') || 'light',
  }),
  actions: {
    setTheme(newTheme: 'light' | 'dark') {
      this.theme = newTheme;
      localStorage.setItem('user-theme', newTheme);
    },
    toggleTheme() {
      const nextTheme = this.theme === 'light' ? 'dark' : 'light';
      this.setTheme(nextTheme);
    },
    async fetchBranding() {
      // Check if we are on a subdomain (simple check for demo)
      const host = window.location.hostname;
      const parts = host.split('.');
      // If we have more than 2 parts (e.g. tenant.localhost)
      this.isPrivateFlow = parts.length > (host.includes('localhost') ? 1 : 2);

      const data = await brandingService.getBranding();
      this.tenantName = data.tenant_name;
      this.logoUrl = data.logo_url;
      this.contactInfo = data.contact_info;
      this.isLoaded = true;
    }
  }
});
