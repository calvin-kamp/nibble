import type { RouteRecordRaw } from 'vue-router'

export const authRoutes: RouteRecordRaw[] = [
	{
		path: '/anmeldung',
		name: 'auth-login',
		component: () => import('@features/auth/views/LoginView.vue'),
		meta: { title: 'Anmelden', navigation: 'header' },
	},
	{
		path: '/registrieren',
		name: 'auth-register',
		component: () => import('@features/auth/views/RegisterView.vue'),
		meta: { title: 'Registrieren', navigation: 'header' },
	},
	// Link from the confirmation email; the backend builds it as /verify-email?token=...
	{
		path: '/email-bestaetigen',
		alias: '/verify-email',
		name: 'auth-verify-email',
		component: () => import('@features/auth/views/EmailVerifyView.vue'),
		meta: { title: 'E-Mail bestätigen', navigation: 'header' },
	},
	{
		path: '/passwort-vergessen',
		name: 'auth-password-forgot',
		component: () => import('@features/auth/views/PasswordForgotView.vue'),
		meta: { title: 'Passwort vergessen', navigation: 'header' },
	},
	// Link from the reset email; the backend builds it as /reset-password?token=...
	{
		path: '/passwort-zuruecksetzen',
		alias: '/reset-password',
		name: 'auth-password-reset',
		component: () => import('@features/auth/views/PasswordResetView.vue'),
		meta: { title: 'Neues Passwort', navigation: 'header' },
	},
]
