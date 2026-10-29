import type { RouteRecordRaw } from 'vue-router'

export const landingRoutes: RouteRecordRaw[] = [
	{
		path: '/',
		name: 'home',
		component: () => import('@features/landing/views/HomeView.vue'),
		meta: { title: 'Start' },
	},
]
