import type { RouteRecordRaw } from 'vue-router'

export const recipeRoutes: RouteRecordRaw[] = [
  {
    path: 'rezepte',
    name: 'recipe-list',
    component: () => import('./views/RecipeListView.vue'),
  },
  {
    path: 'rezepte/:id(\\d+)-:name',
    name: 'recipe-detail',
    component: () => import('./views/RecipeDetailView.vue'),
  },
]
