import type { RouteRecordRaw } from 'vue-router'

export const accountRoutes: RouteRecordRaw[] = [
	// /konto leads to the first area; areas are switched via the select or the list
	{
		path: '/konto',
		component: () => import('@features/account/views/AccountView.vue'),
		meta: { title: 'Einstellungen', requiresAuth: true },
		children: [
			{ path: '', name: 'account', redirect: { name: 'account-profile' } },
			{
				path: 'profil',
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
	// Link from the email to the new address after a change in the account
	{
		path: '/email-aendern',
		name: 'auth-email-change',
		component: () => import('@features/account/views/EmailChangeConfirmView.vue'),
		meta: { title: 'E-Mail-Adresse ändern', navigation: 'header' },
	},
]
