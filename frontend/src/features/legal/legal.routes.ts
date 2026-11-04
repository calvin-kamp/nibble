import type { RouteRecordRaw } from 'vue-router'

export const legalRoutes: RouteRecordRaw[] = [
	{
		path: '/impressum',
		name: 'legal-notice',
		component: () => import('@features/legal/views/LegalNoticeView.vue'),
		meta: { title: 'Impressum', description: 'Impressum von nibble: Anbieter und Kontakt.' },
	},
	{
		path: '/datenschutz',
		name: 'legal-privacy',
		component: () => import('@features/legal/views/PrivacyPolicyView.vue'),
		meta: {
			title: 'Datenschutz',
			description:
				'Welche Daten nibble verarbeitet, wofür, wie lange und welche Rechte du hast.',
		},
	},
	{
		path: '/agb',
		name: 'legal-tos',
		component: () => import('@features/legal/views/TermsView.vue'),
		meta: {
			title: 'AGB',
			description: 'Allgemeine Geschäftsbedingungen für die Nutzung von nibble.',
		},
	},
]
