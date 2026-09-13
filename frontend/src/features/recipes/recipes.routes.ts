import type { RouteRecordRaw } from 'vue-router'

export const recipeRoutes: RouteRecordRaw[] = [
  {
    path: '/rezepte',
    name: 'recipe-list',
    component: () => import('./views/RecipeListView.vue'),
  },
]
