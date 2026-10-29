import type { RouteRecordRaw } from 'vue-router'

export const calorieCalculatorRoutes: RouteRecordRaw[] = [
	{
		path: '/kalorienrechner',
		name: 'calorie-calculator',
		component: () => import('@features/calorie-calculator/views/CalorieCalculatorView.vue'),
		meta: { title: 'Kalorienrechner' },
	},
]
