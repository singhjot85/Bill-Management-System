import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useTenantStore = defineStore('tenant', () => {
  const tenantName = ref('public');
  const isPublic = computed(() => tenantName.value === 'public');

  /**
   * Resolves the tenant name from the current hostname.
   * Logic:
   * 1. Get hostname.
   * 2. If it's a subdomain of the base domain, that's the tenant name.
   * 3. Otherwise, it's 'public'.
   */
  function resolveTenant() {
    const hostname = window.location.hostname;
    const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'localhost';

    // Handle localhost and production domains
    if (hostname === baseDomain || hostname === 'localhost' || hostname === '127.0.0.1') {
      tenantName.value = 'public';
    } else if (hostname.endsWith(`.${baseDomain}`)) {
      tenantName.value = hostname.replace(`.${baseDomain}`, '');
    } else {
      // Fallback for cases where it might be a direct IP or unknown domain
      // In a real prod env, this might need more robust handling
      tenantName.value = 'public';
    }

    console.log(`[TenantStore] Resolved tenant: ${tenantName.value}`);
    return tenantName.value;
  }

  return {
    tenantName,
    isPublic,
    resolveTenant
  };
});
