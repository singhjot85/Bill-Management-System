import { type RouteRecordRaw } from 'vue-router';

export const privateRoutes: RouteRecordRaw[] = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardPage.vue'), // Assuming this exists or will exist
    meta: { requiresAuth: true }
  },
];
