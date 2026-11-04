import type { RouteRecordRaw } from 'vue-router'

export const helpRoutes: RouteRecordRaw[] = [
	{
		path: '/hilfe',
		name: 'help',
		component: () => import('@features/help/views/HelpView.vue'),
		meta: {
			title: 'Hilfe',
			description: 'Anleitung, häufige Fragen und Kontakt: So kommst du mit nibble zurecht.',
		},
	},
	{
		path: '/hilfe/anleitung',
		name: 'help-guide',
		component: () => import('@features/help/views/HelpGuideView.vue'),
		meta: {
			title: 'So nutzt du nibble',
			description:
				'Schritt für Schritt: Essen eintragen, Barcode scannen, Gewicht verfolgen und eigene Rezepte einreichen.',
		},
	},
	{
		path: '/hilfe/faq',
		name: 'help-faq',
		component: () => import('@features/help/views/HelpFaqView.vue'),
		meta: {
			title: 'Häufige Fragen',
			description:
				'Antworten zu Tagebuch, Rezepten, Kalorienrechner, Datenschutz und deinem Konto bei nibble.',
		},
	},
	{
		path: '/hilfe/barrierefreiheit',
		name: 'help-accessibility',
		component: () => import('@features/help/views/HelpAccessibilityView.vue'),
		meta: {
			title: 'Barrierefreiheit',
			description: 'Wie barrierefrei nibble ist und wie du uns Barrieren meldest.',
		},
	},
]
