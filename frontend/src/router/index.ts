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

router.beforeEach((to, from, next) => {
  const uiStore = useUIStore();
  uiStore.startLoading();

  const authToken = useAuthStore().refreshToken()

  if (to.meta.requiresAuth && !authToken){
    return { name: 'login' };
  }

  next();


});

router.afterEach(() => {
  const uiStore = useUIStore();
  uiStore.stopLoading();
});

export default router;
