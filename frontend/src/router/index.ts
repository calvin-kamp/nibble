import type { RouteRecordRaw } from 'vue-router'

import { createRouter, createWebHistory } from 'vue-router'
import { DefaultLayout } from '@components/layout'
import { authRoutes } from '@features/auth/auth.routes'
import { calorieCalculatorRoutes } from '@features/calorie-calculator/calorie-calculator.routes'
import { recipeRoutes } from '@features/recipes/recipes.routes'
import { useAuthStore } from '@stores/auth.store'
import { accountRoutes, dashboardRoutes, legalRoutes, trackingRoutes } from './routes'

const APP_NAME = 'Nibble'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: DefaultLayout,
    children: [
      ...accountRoutes,
      ...calorieCalculatorRoutes,
      ...dashboardRoutes,
      ...legalRoutes,
      ...recipeRoutes,
      ...trackingRoutes,

      {
        path: '',
        name: 'public-landing',
        component: () => import('@views/LandingView.vue'),
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'not-found',
        component: () => import('@views/NotFoundView.vue'),
        meta: { title: 'Seite nicht gefunden' },
      },
    ],
  },
  ...authRoutes,
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'auth-login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && auth.isLoggedIn) {
    return { name: 'dashboard' }
  }
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - ${APP_NAME}` : APP_NAME
})

export default router
