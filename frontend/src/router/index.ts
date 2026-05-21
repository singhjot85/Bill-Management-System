import { createRouter, createWebHashHistory } from 'vue-router';
import { tenantRoutes } from './tenant';
import { publicRoutes } from './public';
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

  const routesToLoad = tenantName !== 'public' ? tenantRoutes : publicRoutes;

  routesToLoad.forEach((route) => {
    router.addRoute(route);
  });

  console.log(`[Router] Loaded routes for tenant: ${tenantName}`);
}

/**
 * Before each route:
 * - Resolve tenant name, if not already resolved.
 * - Show the loading spinner.
 * - Check if auth required for route: re-route to login page.
 * - Redirect authenticated users away from guest-only pages (Login, Signup, Tenant Landing).
 */
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  const uiStore = useUIStore();
  const tenantStore = useTenantStore();

  // Ensure tenant is resolved (if for some reason it wasn't in main.ts)
  if (!tenantStore.tenantName) {
    tenantStore.resolveTenant();
  }
  uiStore.startLoading();

  const isAuthenticated = authStore.isAuthenticated || !!authStore.accessToken;

  // 1. Handle routes that require authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log(`[Router] Auth required but user not logged in. Redirecting to Login.`);
    if (tenantStore.tenantName === 'public') return next({ name: 'Login' });
    return next({ name: 'TenantHome' })
  }

  // 2. Redirect authenticated users away from guest-only pages
  if (isAuthenticated) {
    const guestOnlyRoutes = ['Login', 'Signup'];
    const isTenantLanding = tenantStore.tenantName !== 'public' && (to.path === '/' || to.name === 'TenantHome');

    if (guestOnlyRoutes.includes(to.name as string) || isTenantLanding) {
      console.log(`[Router] Authenticated user on guest route ${String(to.name)}. Redirecting to Dashboard.`);
      return next({ name: 'Dashboard' });
    }
  }

  return next();
});

router.afterEach(() => {
  const uiStore = useUIStore();
  uiStore.stopLoading();
});

export default router;
