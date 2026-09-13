import type { RouteRecordRaw } from 'vue-router'

export const calorieCalculatorRoutes: RouteRecordRaw[] = [
  {
    path: '/kalorienrechner',
    name: 'calorie-calculator',
    component: () => import('./views/CalorieCalculatorView.vue'),
  },
]
