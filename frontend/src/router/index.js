import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue'; // Keep Login static for faster initial render
import { useAuthStore } from '../stores/auth';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks',
    name: 'TaskManage',
    component: () => import('../views/TaskManage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  
  // Wait specifically if we have a token but no user loaded yet (page refresh case)
  if (authStore.token && !authStore.user) {
    try {
        await authStore.fetchUser();
    } catch (e) {
        // Token invalid
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } else if (to.meta.requiresAdmin && (!authStore.user || !authStore.user.is_admin)) {
    // If trying to access admin but not admin, redirect to user dashboard
    next('/');
  } else {
    next();
  }
});

export default router;
