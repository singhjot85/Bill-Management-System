import { type RouteRecordRaw } from 'vue-router';

export const privateRoutes: RouteRecordRaw[] = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'), // Assuming this exists or will exist
    meta: { requiresAuth: true }
  },
];
