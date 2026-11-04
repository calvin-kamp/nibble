import { createRouter, createWebHistory } from 'vue-router'

import {
	announcePage,
	setPageAddress,
	setPageDescription,
	setPageTitle,
} from '@shared/composables/page-title'

import { accountRoutes } from '@features/account/account.routes'
import { adminRoutes } from '@features/admin/admin.routes'
import { authRoutes } from '@features/auth/auth.routes'
import { useAuthStore } from '@features/auth/auth.store'
import { calorieCalculatorRoutes } from '@features/calorie-calculator/calorie-calculator.routes'
import { dashboardRoutes } from '@features/dashboard/dashboard.routes'
import { helpRoutes } from '@features/help/help.routes'
import { landingRoutes } from '@features/landing/landing.routes'
import { legalRoutes } from '@features/legal/legal.routes'
import { mealsRoutes } from '@features/meals/meals.routes'
import { onboardingRoutes } from '@features/onboarding/onboarding.routes'
import { recipesRoutes } from '@features/recipes/recipes.routes'
import { trackingRoutes } from '@features/tracking/tracking.routes'
import { jumpMarkOffset, scrollToJumpMark } from '@shared/utils/scroll'

declare module 'vue-router' {
	interface RouteMeta {
		/**
		 * Which navigation the page has. full (default): sidebar, header and bottom bar.
		 * header: only the header with the menu, e.g. on sign-in. none: no navigation, e.g. in onboarding.
		 */
		navigation?: 'full' | 'header' | 'none'
		title?: string
		/** Text for search results and link previews; without one the general one applies */
		description?: string
		/** Kept out of search results even without login, e.g. sign-in */
		noindex?: boolean
		requiresAuth?: boolean
		requiresConsent?: boolean
		requiresStaff?: boolean
		/** Reachable before onboarding is completed, e.g. to delete the account halfway */
		allowedDuringOnboarding?: boolean
	}
}

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	scrollBehavior: (to, from, savedPosition) => {
		if (savedPosition) return savedPosition

		if (to.hash) {
			const id = decodeURIComponent(to.hash.slice(1))

			// On the same page, wait for a closing select or menu: it returns focus to its
			// trigger, which would scroll back up and cut the jump short.
			if (to.path === from.path) {
				window.setTimeout(() => scrollToJumpMark(id), 200)

				return false
			}

			const target = document.getElementById(id)

			if (target) return { el: target, top: jumpMarkOffset(target) }

			// The page is still loading: jump once it is there
			window.setTimeout(() => scrollToJumpMark(id, false), 300)
		}

		return { top: 0 }
	},
	routes: [
		...landingRoutes,
		...dashboardRoutes,
		...trackingRoutes,
		...recipesRoutes,
		...mealsRoutes,
		...calorieCalculatorRoutes,
		...onboardingRoutes,
		...authRoutes,
		...accountRoutes,
		...adminRoutes,
		...helpRoutes,
		...legalRoutes,
		{
			path: '/:pathMatch(.*)*',
			name: 'not-found',
			component: () => import('../views/NotFoundView.vue'),
			meta: { title: 'Seite nicht gefunden', noindex: true },
		},
	],
})

// Wait until it is known who is signed in. On app start the guard runs before that.
router.beforeEach(async (to) => {
	const auth = useAuthStore()

	await auth.whenReady()

	if (to.meta.requiresAuth && !auth.isLoggedIn) {
		return { name: 'auth-login', query: { weiter: to.fullPath } }
	}

	// Someone who left onboarding halfway continues there, only the settings stay open, so the
	// account can be deleted or the consent revoked. Staff accounts have no onboarding.
	if (
		to.meta.requiresAuth &&
		to.name !== 'onboarding' &&
		!to.meta.allowedDuringOnboarding &&
		!auth.hasCompletedOnboarding &&
		!auth.isStaff
	) {
		return { name: 'onboarding' }
	}

	// Finished accounts have nothing left to set up. The flow would start with empty data and its
	// last step would complete the onboarding a second time.
	if (
		to.name === 'onboarding' &&
		auth.isLoggedIn &&
		(auth.hasCompletedOnboarding || auth.isStaff)
	) {
		return { name: 'dashboard' }
	}

	if (to.meta.requiresStaff && !auth.isStaff) return { name: 'dashboard' }

	if (to.meta.requiresConsent && !auth.hasDataConsent) return { name: 'dashboard' }
})

router.afterEach((to, from) => {
	setPageTitle(to.meta.title)
	setPageDescription(to.meta.description)
	setPageAddress(to.path, !to.meta.requiresAuth && !to.meta.noindex)

	// Screen readers do not notice a client-side page change, so announce the new page. Not on
	// the first load and not when only the query changes, e.g. a filter or a form step.
	if (from.matched.length && to.path !== from.path) announcePage(to.meta.title)
})

export default router
