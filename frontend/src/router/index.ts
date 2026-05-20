import { createRouter, createWebHashHistory } from 'vue-router';
import { publicRoutes } from './public';
import { privateRoutes } from './private';
import { useUIStore } from '@/stores/uiStore';
import { useAuthStore } from '@/stores/authStore';
import { useTenantStore } from '@/stores/tenantStore';

const router = createRouter({
  history: createWebHashHistory(),
  routes: [], // Start with empty routes
});

/**
 * Dynamically configures routes based on tenant context.
 */
export function setupRoutes() {
  const tenantStore = useTenantStore();
  const tenantName = tenantStore.resolveTenant();

  let routesToLoad = []
  if (tenantName !== "public"){
    // TODO: Change route names, this is confusing, but right now way too tired to fix this.
    routesToLoad = [...publicRoutes];
  }
  else{
    routesToLoad = [...privateRoutes];
  }

  routesToLoad.forEach(route => {
    router.addRoute(route);
  });

  console.log(`[Router] Loaded routes for tenant: ${tenantName}`);
  console.log({routesToLoad})
}

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  const uiStore = useUIStore();
  const tenantStore = useTenantStore();

  // Ensure tenant is resolved
  if (!tenantStore.tenantName) {
    tenantStore.resolveTenant();
  }

  uiStore.startLoading();

  // If not authenticated, try to refresh from cookie
  if (!authStore.isAuthenticated) {
    await authStore.refreshToken();
  }

  // Handle Auth Guards
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

router.afterEach(() => {
  const uiStore = useUIStore();
  uiStore.stopLoading();
});

export default router;
