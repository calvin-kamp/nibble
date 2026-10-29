import type { RouteRecordRaw } from 'vue-router'

// Saved meals: list, detail page, create and edit
export const mealsRoutes: RouteRecordRaw[] = [
	{
		path: '/mahlzeiten',
		name: 'own-meals',
		component: () => import('@features/meals/views/MealListView.vue'),
		meta: { title: 'Meine Mahlzeiten', requiresAuth: true, requiresConsent: true },
	},
	{
		path: '/mahlzeiten/neu',
		name: 'meal-create',
		component: () => import('@features/meals/views/MealCreateView.vue'),
		meta: { title: 'Mahlzeit anlegen', requiresAuth: true, requiresConsent: true },
	},
	{
		path: '/mahlzeiten/:id(\\d+)',
		name: 'meal-detail',
		component: () => import('@features/meals/views/MealDetailView.vue'),
		props: true,
		meta: { title: 'Mahlzeit', requiresAuth: true, requiresConsent: true },
	},
	{
		path: '/mahlzeiten/:id(\\d+)/bearbeiten',
		name: 'meal-edit',
		component: () => import('@features/meals/views/MealEditView.vue'),
		props: true,
		meta: { title: 'Mahlzeit bearbeiten', requiresAuth: true, requiresConsent: true },
	},
]
