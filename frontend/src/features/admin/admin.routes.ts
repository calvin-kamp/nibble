import type { RouteRecordRaw } from 'vue-router'

export const adminRoutes: RouteRecordRaw[] = [
	{ path: '/admin', redirect: { name: 'admin' } },
	// Old address of the recipe moderation, e.g. in bookmarks
	{ path: '/verwaltung', redirect: { name: 'admin' } },
	{
		path: '/verwaltung/einreichungen/:id(\\d+)',
		redirect: (to) => ({ name: 'admin-submission', params: to.params }),
	},
	{
		path: '/admin/rezepte',
		name: 'admin',
		component: () => import('@features/admin/views/AdminView.vue'),
		meta: {
			title: 'Rezepte prüfen',
			requiresAuth: true,
			requiresStaff: true,
		},
	},
	{
		path: '/admin/rezepte/einreichungen/:id(\\d+)',
		name: 'admin-submission',
		component: () => import('@features/admin/views/AdminSubmissionView.vue'),
		props: true,
		meta: {
			title: 'Einreichung',
			requiresAuth: true,
			requiresStaff: true,
		},
	},
	{
		path: '/admin/lebensmittel',
		name: 'admin-foods',
		component: () => import('@features/admin/views/AdminFoodsView.vue'),
		meta: {
			title: 'Lebensmittel',
			requiresAuth: true,
			requiresStaff: true,
		},
	},
	{
		path: '/admin/lebensmittel/neu',
		name: 'admin-food-generic',
		component: () => import('@features/admin/views/AdminGenericFoodView.vue'),
		meta: {
			title: 'Lebensmittel ohne Barcode',
			requiresAuth: true,
			requiresStaff: true,
		},
	},
	{
		path: '/admin/lebensmittel/korrigieren/:code([0-9]{8,14}|n[0-9]{5})',
		name: 'admin-food-correct',
		component: () => import('@features/admin/views/AdminFoodCorrectView.vue'),
		props: true,
		meta: {
			title: 'Lebensmittel korrigieren',
			requiresAuth: true,
			requiresStaff: true,
		},
	},
	{
		path: '/admin/lebensmittel/:code(\\d{8,14})',
		name: 'admin-food',
		component: () => import('@features/admin/views/AdminFoodView.vue'),
		props: true,
		meta: {
			title: 'Lebensmittel anlegen',
			requiresAuth: true,
			requiresStaff: true,
		},
	},
]
