import type { RouteRecordRaw } from 'vue-router'

export const calorieCalculatorRoutes: RouteRecordRaw[] = [
	{
		path: '/kalorienrechner',
		name: 'calorie-calculator',
		component: () => import('@features/calorie-calculator/views/CalorieCalculatorView.vue'),
		meta: {
			title: 'Kalorienrechner',
			description:
				'Berechne deinen Tagesbedarf an Kalorien aus Grundumsatz, Schritten und Training, mit Makro-Verteilung für dein Ziel. Kostenlos, ohne Anmeldung.',
		},
	},
]
