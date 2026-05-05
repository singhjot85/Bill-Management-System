import { createRouter, createWebHashHistory } from 'vue-router';
import { publicRoutes } from './public';
import { privateRoutes } from './private';

const routes = [
  ...publicRoutes,
  ...privateRoutes,
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
