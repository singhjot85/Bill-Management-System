import { type RouteRecordRaw } from 'vue-router';

export const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/views/TenantHomePage.vue'),
    children: [
      {
        path: '',
        name: 'PublicHome',
        component: () => import('@/components/smart/HomePage.vue'),
      },
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/AuthPage.vue'),
      },
      {
        path: 'signup',
        name: 'Signup',
        component: () => import('@/views/AuthPage.vue'),
      },
      {
        path: 'donate',
        name: 'Donate',
        component: () => import('@/components/smart/DonatePage.vue'),
      },
    ],
  },
];
