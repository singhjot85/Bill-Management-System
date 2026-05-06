import { type RouteRecordRaw } from 'vue-router';

export const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/TenantLayout.vue'),
    children: [
      {
        path: '',
        name: 'PublicHome',
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
];
