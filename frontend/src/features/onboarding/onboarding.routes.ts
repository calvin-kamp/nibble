import type { RouteRecordRaw } from 'vue-router'

export const onboardingRoutes: RouteRecordRaw[] = [
	{
		path: '/einrichten',
		name: 'onboarding',
		component: () => import('@features/onboarding/views/OnboardingView.vue'),
		meta: { title: 'Einrichten', navigation: 'none', requiresAuth: true },
	},
]
