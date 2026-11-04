import type { RouteRecordRaw } from 'vue-router'

export const landingRoutes: RouteRecordRaw[] = [
	{
		path: '/',
		name: 'home',
		component: () => import('@features/landing/views/HomeView.vue'),
		// No title of its own: the start page carries the full name, see page-title.ts
		meta: {},
	},
]
