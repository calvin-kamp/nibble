import { calorieCalculatorRoutes } from '@/features/calorie-calculator/calorie-calculator.routes'
import { recipeRoutes } from '@/features/recipes/recipes.routes'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [...calorieCalculatorRoutes, ...recipeRoutes],
})

export default router
