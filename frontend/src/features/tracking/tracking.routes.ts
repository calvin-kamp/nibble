import type { RouteRecordRaw } from 'vue-router'

import { weekSlug, weekStart, weekStartFromSlug } from '@features/tracking/tracking.utils'
import { parseIsoDate, toIsoDate } from '@shared/utils/date'

export const trackingRoutes: RouteRecordRaw[] = [
	{ path: '/tagebuch', redirect: { name: 'diary-food' } },
	// Old address, e.g. from bookmarks
	{
		path: '/tagebuch/ernaehrung/:rest(.*)?',
		redirect: (to) => `/tagebuch/essen/${String(to.params.rest ?? '')}`,
	},
	{
		path: '/tagebuch/essen',
		name: 'diary-food',
		component: () => import('@features/tracking/views/DiaryFoodView.vue'),
		meta: { title: 'Essen', requiresAuth: true, requiresConsent: true },
	},
	{
		path: '/tagebuch/essen/:date(\\d{4}-\\d{2}-\\d{2})',
		name: 'diary-food-day',
		component: () => import('@features/tracking/views/DiaryDayView.vue'),
		props: true,
		meta: { title: 'Essen', requiresAuth: true, requiresConsent: true },
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
	{
		// The calendar week in the address, e.g. /tagebuch/gewicht/2026-kw-1
		path: '/tagebuch/gewicht/:week(\\d{4}-kw-\\d{1,2})',
		name: 'diary-weight-week',
		component: () => import('@features/tracking/views/WeightWeekView.vue'),
		props: (to) => ({ start: weekStartFromSlug(String(to.params.week)) }),
		meta: { title: 'Gewicht', requiresAuth: true, requiresConsent: true },
		beforeEnter: (to) => {
			const start = weekStartFromSlug(String(to.params.week))

			if (!start || start > weekStart(toIsoDate())) return { name: 'diary-weight' }
		},
	},
	// Older links named the week by its Monday
	{
		path: '/tagebuch/gewicht/woche/:start(\\d{4}-\\d{2}-\\d{2})',
		redirect: (to) => {
			const start = String(to.params.start)

			return parseIsoDate(start)
				? { name: 'diary-weight-week', params: { week: weekSlug(weekStart(start)) } }
				: { name: 'diary-weight' }
		},
	},
	{ path: '/gewicht', redirect: { name: 'diary-weight' } },
]
