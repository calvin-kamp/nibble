import type { RouteRecordRaw } from 'vue-router'

import { parseIsoDate, toIsoDate } from '@shared/utils/date'

// Diary: nutrition as a list of days, each day with all its entries, plus weight
export const trackingRoutes: RouteRecordRaw[] = [
	{ path: '/tagebuch', redirect: { name: 'diary-food' } },
	{
		path: '/tagebuch/ernaehrung',
		name: 'diary-food',
		component: () => import('@features/tracking/views/DiaryFoodView.vue'),
		meta: { title: 'Ernährung', requiresAuth: true, requiresConsent: true },
	},
	{
		path: '/tagebuch/ernaehrung/:date(\\d{4}-\\d{2}-\\d{2})',
		name: 'diary-food-day',
		component: () => import('@features/tracking/views/DiaryDayView.vue'),
		props: true,
		meta: { title: 'Ernährung', requiresAuth: true, requiresConsent: true },
		// Not a real day, or one in the future: back to the list
		beforeEnter: (to) => {
			const date = String(to.params.date)

			if (!parseIsoDate(date) || date > toIsoDate()) return { name: 'diary-food' }
		},
	},
	{
		path: '/tagebuch/gewicht',
		name: 'diary-weight',
		component: () => import('@features/tracking/views/WeightView.vue'),
		meta: { title: 'Gewicht', requiresAuth: true, requiresConsent: true },
	},
	{ path: '/gewicht', redirect: { name: 'diary-weight' } },
]
