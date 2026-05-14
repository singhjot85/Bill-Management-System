import { defineStore } from 'pinia';
import { brandingService } from '@/services/brandingService';
import { useTenantStore } from '@/stores/tenantStore';
import defaultLogo from '@/assets/img/bill-invoice.svg';

export const useBrandingStore = defineStore('branding', {
  state: () => ({
    displayName: 'Invoice Management',
    logoUrl: defaultLogo,
    contactInfo: '',
    isLoaded: false,
    theme: localStorage.getItem('user-theme') || 'light',
  }),
  getters: {
    isPrivateFlow: () => {
      const tenantStore = useTenantStore();
      return !tenantStore.isPublic;
    }
  },
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
      const data = await brandingService.getBranding();
      this.displayName = data.tenant_name;
      this.logoUrl = data.logo_url;
      this.contactInfo = data.contact_info;
      this.isLoaded = true;
    }
  }
});
