import type { RouteRecordRaw } from 'vue-router'

export const legalRoutes: RouteRecordRaw[] = [
	{
		path: '/impressum',
		name: 'legal-notice',
		component: () => import('@features/legal/views/LegalNoticeView.vue'),
		meta: { title: 'Impressum' },
	},
	{
		path: '/datenschutz',
		name: 'legal-privacy',
		component: () => import('@features/legal/views/PrivacyPolicyView.vue'),
		meta: { title: 'Datenschutz' },
	},
	{
		path: '/agb',
		name: 'legal-tos',
		component: () => import('@features/legal/views/TermsView.vue'),
		meta: { title: 'AGB' },
	},
]
