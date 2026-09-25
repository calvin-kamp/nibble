import type { RouteRecordRaw } from 'vue-router'

export const recipeRoutes: RouteRecordRaw[] = [
  {
    path: 'rezepte',
    name: 'recipe-list',
    meta: { title: 'Rezepte' },
    component: () => import('./views/RecipeListView.vue'),
  },
  {
    path: 'rezepte/neu',
    name: 'recipe-create',
    meta: { title: 'Rezept erstellen', requiresAuth: true },
    component: () => import('./views/RecipeCreateView.vue'),
  },
  {
    path: 'rezepte/:id(\\d+)/bearbeiten',
    name: 'recipe-edit',
    meta: { title: 'Rezept bearbeiten', requiresAuth: true },
    component: () => import('./views/RecipeEditView.vue'),
  },
  {
    // The slug comes from the API as "<id>-<name>", the id stays the lookup key.
    path: 'rezepte/:id(\\d+)-:name',
    name: 'recipe-detail',
    meta: { title: 'Rezept' },
    component: () => import('./views/RecipeDetailView.vue'),
  },
]
