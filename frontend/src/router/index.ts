import { createRouter, createWebHashHistory } from 'vue-router';
import { useBrandingStore } from '@/stores/brandingStore';

const routes = [
  {
    path: '/',
    name: 'Root',
    // Dynamic component or redirect based on schema
    component: () => import('@/views/TenantHomePage.vue'),
    beforeEnter: (to) => {
      const brandingStore = useBrandingStore();
      // If it's the public schema (not a subdomain), redirect to login
      if (!brandingStore.isPrivateFlow) {
        return '/login';
      }
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginPage.vue'),
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('@/views/auth/SignupPage.vue'),
  },
  {
    path: '/donate',
    name: 'Donate',
    component: () => import('@/views/DonatePage.vue'),
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
