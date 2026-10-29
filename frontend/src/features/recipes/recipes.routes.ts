import type { RouteRecordRaw } from 'vue-router'

export const recipesRoutes: RouteRecordRaw[] = [
	{
		path: '/rezepte',
		name: 'recipe-list',
		component: () => import('@features/recipes/views/RecipeListView.vue'),
		meta: { title: 'Rezepte' },
	},
	{
		path: '/rezepte/neu',
		name: 'recipe-create',
		component: () => import('@features/recipes/views/RecipeCreateView.vue'),
		meta: { title: 'Rezept anlegen', requiresAuth: true },
	},
	// ID and name, e.g. /rezepte/3-linsen-bowl-mit-joghurtdip. The view only receives the ID;
	// an outdated name in the path is corrected there.
	{
		path: '/rezepte/:id(\\d+)-:slug',
		name: 'recipe-detail',
		component: () => import('@features/recipes/views/RecipeDetailView.vue'),
		props: (route) => ({ id: route.params.id }),
		meta: { title: 'Rezept' },
	},
	{
		path: '/rezepte/:id(\\d+)-:slug/bearbeiten',
		name: 'recipe-edit',
		component: () => import('@features/recipes/views/RecipeEditView.vue'),
		props: (route) => ({ id: route.params.id }),
		meta: { title: 'Rezept bearbeiten', requiresAuth: true },
	},
]
