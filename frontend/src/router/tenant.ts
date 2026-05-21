import { type RouteRecordRaw } from 'vue-router';

export const tenantRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/layouts/TenantLayout.vue'),
    children: [
      {
        path: '',
        name: 'TenantHome',
        component: () => import('@/views/HomeView.vue'),
      },
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/AuthView.vue'),
      },
      {
        path: 'signup',
        name: 'Signup',
        component: () => import('@/views/AuthView.vue'),
      },
      {
        path: 'donate',
        name: 'Donate',
        component: () => import('@/views/DonateView.vue'),
      },
    ],
  },
  {
    path: '/client-dashboard',
    name: 'Dashboard',
    component: () => import('@/views/ClientDashboard.vue'),
    meta: { requiresAuth: true }
  },
];
