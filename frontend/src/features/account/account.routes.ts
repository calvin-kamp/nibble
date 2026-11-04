import type { RouteRecordRaw } from 'vue-router'

export const accountRoutes: RouteRecordRaw[] = [
	{
		path: '/einstellungen',
		component: () => import('@features/account/views/AccountView.vue'),
		meta: { title: 'Einstellungen', requiresAuth: true, allowedDuringOnboarding: true },
		children: [
			{ path: '', name: 'account', redirect: { name: 'account-profile' } },
			{
				path: 'anmeldedaten',
				name: 'account-profile',
				component: () => import('@features/account/components/AccountProfilePanel.vue'),
			},
			{
				path: 'persoenlich',
				name: 'account-personal',
				component: () => import('@features/account/components/AccountPersonalPanel.vue'),
			},
			{
				path: 'ernaehrung',
				name: 'account-nutrition',
				component: () => import('@features/account/components/AccountNutritionPanel.vue'),
			},
			{
				path: 'datenschutz',
				name: 'account-privacy',
				component: () => import('@features/account/components/AccountPrivacyPanel.vue'),
			},
			{
				path: 'loeschen',
				name: 'account-delete',
				component: () => import('@features/account/components/AccountDeletePanel.vue'),
			},
		],
	},
	// Old address, e.g. from bookmarks
	{
		path: '/konto/:rest(.*)?',
		redirect: (to) => {
			const rest = String(to.params.rest ?? '')

			return `/einstellungen/${rest === 'profil' ? 'anmeldedaten' : rest}`
		},
	},
	{
		path: '/email-aendern',
		name: 'auth-email-change',
		component: () => import('@features/account/views/EmailChangeConfirmView.vue'),
		meta: { title: 'E-Mail-Adresse ändern', navigation: 'header', noindex: true },
	},
]
