import { createRouter, createWebHashHistory } from 'vue-router';
import { publicRoutes } from './public';
import { privateRoutes } from './private';
import { useUIStore } from '@/stores/uiStore';
import { useAuthStore } from '@/stores/authStore';

const routes = [
  ...publicRoutes,
  ...privateRoutes,
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach(async (to, _from, next) => {
  const uiStore = useUIStore();
  const authStore = useAuthStore();
  uiStore.startLoading();

  // If not authenticated, try to refresh from cookie
  if (!authStore.isAuthenticated) {
    await authStore.refreshToken();
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' });
  } else {
    next();
  }
});

router.afterEach(() => {
  const uiStore = useUIStore();
  uiStore.stopLoading();
});

export default router;
