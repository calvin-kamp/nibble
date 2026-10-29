import type { Component } from 'vue'
import type { LocationQueryRaw, RouteLocationNormalizedLoaded } from 'vue-router'

import {
	AppleIcon,
	BookOpenIcon,
	ChefHatIcon,
	CalculatorIcon,
	ClipboardCheckIcon,
	HouseIcon,
	LayoutDashboardIcon,
	UtensilsIcon,
	WeightIcon,
} from '@lucide/vue'

import { useAuthStore } from '@features/auth/auth.store'

export type NavVisibility = 'always' | 'guest' | 'user' | 'consent' | 'staff'

export interface NavItem {
	routeName: string
	label: string
	icon?: Component
	hash?: string
	/** E.g. a tab of the recipe list. The item is only active when the query matches. */
	query?: Record<string, string>
	/** Subpages on which the item is active as well, e.g. a day in the diary */
	activeOn?: string[]
	visibility: NavVisibility
}

// Navigation for the sidebar (desktop) and menu (phone, tablet). The bottom bar on phones
// only shows the most important items.
export const MAIN_NAV: NavItem[] = [
	{ routeName: 'home', label: 'Start', icon: HouseIcon, visibility: 'guest' },
	{ routeName: 'dashboard', label: 'Übersicht', icon: LayoutDashboardIcon, visibility: 'user' },
	{
		routeName: 'own-meals',
		label: 'Meine Mahlzeiten',
		icon: UtensilsIcon,
		activeOn: ['meal-detail', 'meal-create', 'meal-edit'],
		visibility: 'consent',
	},
	{
		routeName: 'recipe-list',
		query: { ansicht: 'eigene' },
		label: 'Meine Rezepte',
		icon: ChefHatIcon,
		visibility: 'user',
	},
]

// Tracking. Without consent these pages do not exist, so the group is dropped.
export const TRACKING_NAV: NavItem[] = [
	{
		routeName: 'diary-food',
		label: 'Ernährung',
		icon: AppleIcon,
		activeOn: ['diary-food-day'],
		visibility: 'consent',
	},
	{ routeName: 'diary-weight', label: 'Gewicht', icon: WeightIcon, visibility: 'consent' },
]

export const DISCOVER_NAV: NavItem[] = [
	{ routeName: 'recipe-list', label: 'Rezepte', icon: BookOpenIcon, visibility: 'always' },
	{
		routeName: 'calorie-calculator',
		label: 'Kalorienrechner',
		icon: CalculatorIcon,
		visibility: 'always',
	},
]

// Moderation. For everyone without staff status the group is dropped.
export const ADMIN_NAV: NavItem[] = [
	{
		routeName: 'admin',
		label: 'Verwaltung',
		icon: ClipboardCheckIcon,
		activeOn: ['admin-submission'],
		visibility: 'staff',
	},
]

export const LEGAL_NAV: NavItem[] = [
	{ routeName: 'legal-tos', label: 'AGB', visibility: 'always' },
	{ routeName: 'legal-privacy', label: 'Datenschutz', visibility: 'always' },
	{ routeName: 'legal-notice', label: 'Impressum', visibility: 'always' },
]

const ALL_NAV: NavItem[] = [
	...MAIN_NAV,
	...TRACKING_NAV,
	...DISCOVER_NAV,
	...ADMIN_NAV,
	...LEGAL_NAV,
]

function matchesQuery(item: NavItem, route: RouteLocationNormalizedLoaded): boolean {
	return Object.entries(item.query ?? {}).every(([key, value]) => route.query[key] === value)
}

/**
 * Whether an item belongs to the current page. RouterLink only compares the route, which would
 * make "Rezepte" and "Meine Rezepte" active at the same time. Here the item whose query matches wins.
 */
export function isNavItemActive(item: NavItem, route: RouteLocationNormalizedLoaded): boolean {
	if (item.activeOn?.includes(String(route.name))) return true
	if (route.name !== item.routeName || !matchesQuery(item, route)) return false
	if (item.query) return true

	return !ALL_NAV.some(
		(other) =>
			other !== item &&
			other.routeName === item.routeName &&
			other.query &&
			matchesQuery(other, route),
	)
}

export function navItemLocation(item: NavItem): {
	name: string
	query?: LocationQueryRaw
	hash?: string
} {
	return { name: item.routeName, query: item.query, hash: item.hash }
}

/** Filters items by sign-in and consent */
export function useNavVisibility(): (item: NavItem) => boolean {
	const auth = useAuthStore()

	return (item) => {
		if (item.visibility === 'guest') return !auth.isLoggedIn
		if (item.visibility === 'user') return auth.isLoggedIn
		if (item.visibility === 'consent') return auth.isLoggedIn && auth.hasDataConsent
		if (item.visibility === 'staff') return auth.isStaff

		return true
	}
}
