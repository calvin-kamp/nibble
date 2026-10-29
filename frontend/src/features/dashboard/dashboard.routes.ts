import type { RouteRecordRaw } from 'vue-router'

export const dashboardRoutes: RouteRecordRaw[] = [
	{
		path: '/uebersicht',
		name: 'dashboard',
		component: () => import('@features/dashboard/views/DashboardView.vue'),
		meta: { title: 'Übersicht', requiresAuth: true },
	},
]
