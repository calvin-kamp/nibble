import type { RouteRecordRaw } from 'vue-router'

// Staff only: new recipes and changes waiting for approval
export const adminRoutes: RouteRecordRaw[] = [
	{
		path: '/verwaltung',
		name: 'admin',
		component: () => import('@features/admin/views/AdminView.vue'),
		meta: {
			title: 'Verwaltung',
			requiresAuth: true,
			requiresStaff: true,
		},
	},
	{
		path: '/verwaltung/einreichungen/:id(\\d+)',
		name: 'admin-submission',
		component: () => import('@features/admin/views/AdminSubmissionView.vue'),
		props: true,
		meta: {
			title: 'Einreichung',
			requiresAuth: true,
			requiresStaff: true,
		},
	},
]
