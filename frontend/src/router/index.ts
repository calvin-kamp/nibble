import type { RouteRecordRaw } from 'vue-router'

import { DefaultLayout } from '@components/layout'
import { createRouter, createWebHistory } from 'vue-router'

import { accountRoutes, authRoutes, dashboardRoutes, legalRoutes, trackingRoutes } from './routes'
import { calorieCalculatorRoutes } from '@features/calorie-calculator/calorie-calculator.routes'
import { recipeRoutes } from '@features/recipes/recipes.routes'

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
      },
    ],
  },
  ...authRoutes,
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
