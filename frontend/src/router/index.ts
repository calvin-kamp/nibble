import { createRouter, createWebHistory } from 'vue-router'

import { announcePage, setPageTitle } from '@shared/composables/page-title'

import { accountRoutes } from '@features/account/account.routes'
import { adminRoutes } from '@features/admin/admin.routes'
import { authRoutes } from '@features/auth/auth.routes'
import { useAuthStore } from '@features/auth/auth.store'
import { calorieCalculatorRoutes } from '@features/calorie-calculator/calorie-calculator.routes'
import { dashboardRoutes } from '@features/dashboard/dashboard.routes'
import { landingRoutes } from '@features/landing/landing.routes'
import { legalRoutes } from '@features/legal/legal.routes'
import { mealsRoutes } from '@features/meals/meals.routes'
import { onboardingRoutes } from '@features/onboarding/onboarding.routes'
import { recipesRoutes } from '@features/recipes/recipes.routes'
import { trackingRoutes } from '@features/tracking/tracking.routes'

declare module 'vue-router' {
	interface RouteMeta {
		/**
		 * Which navigation the page has. full (default): sidebar, header and bottom bar.
		 * header: only the header with the menu, e.g. on sign-in. none: no navigation, e.g. in onboarding.
		 */
		navigation?: 'full' | 'header' | 'none'
		/** Page name for the document title, e.g. "Rezepte" becomes "Rezepte · nibble" */
		title?: string
		/** Signed-in users only, otherwise redirect to sign-in and back afterwards */
		requiresAuth?: boolean
		/** Only with tracking consent, otherwise redirect to the dashboard, which explains why */
		requiresConsent?: boolean
		/** Staff only, everyone else lands on the dashboard */
		requiresStaff?: boolean
	}
}

// The router scrolls by coordinates, which ignores scroll-padding and scroll-margin. So a jump
// mark keeps clear of the fixed header (hidden: height 0) and its own scroll-margin here.
function jumpMarkOffset(hash: string): number {
	const header = document.querySelector<HTMLElement>('.site-header')
	const target = document.getElementById(decodeURIComponent(hash.slice(1)))
	const margin = target ? parseFloat(getComputedStyle(target).scrollMarginTop) : 0

	return (header?.offsetHeight ?? 0) + margin
}

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	// New pages start at the top, jump marks at their section; Back restores the previous position
	scrollBehavior: (to, _from, savedPosition) => {
		if (savedPosition) return savedPosition
		if (to.hash) return { el: to.hash, top: jumpMarkOffset(to.hash) }

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
		...legalRoutes,
	],
})

// Wait until it is known who is signed in. On app start the guard runs before that.
router.beforeEach(async (to) => {
	const auth = useAuthStore()

	await auth.whenReady()

	if (to.meta.requiresAuth && !auth.isLoggedIn) {
		return { name: 'auth-login', query: { weiter: to.fullPath } }
	}

	if (to.meta.requiresStaff && !auth.isStaff) return { name: 'dashboard' }

	// The dashboard explains why there is no tracking without consent
	if (to.meta.requiresConsent && !auth.hasDataConsent) return { name: 'dashboard' }
})

router.afterEach((to, from) => {
	setPageTitle(to.meta.title)

	// Screen readers do not notice a client-side page change, so announce the new page. Not on
	// the first load and not when only the query changes, e.g. a filter or a form step.
	if (from.matched.length && to.path !== from.path) announcePage(to.meta.title)
})

export default router
