<script setup lang="ts">
import type { NavItem } from '@layouts/navigation'

import {
	CalculatorIcon,
	ChefHatIcon,
	HomeIcon,
	LayoutDashboardIcon,
	NotebookPenIcon,
	PlusIcon,
	UserRoundIcon,
} from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import AccountDrawer from '@features/account/components/AccountDrawer.vue'
import DiaryDrawer from '@features/tracking/components/DiaryDrawer.vue'
import AppNavDrawer from '@layouts/AppNavDrawer.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { useKeyboardFocus } from '@shared/composables/keyboard-focus'

import { useAuthStore } from '@features/auth/auth.store'
import {
	isNavItemActive,
	navItemLocation,
	RECIPES_NAV,
	useNavVisibility,
} from '@layouts/navigation'

const auth = useAuthStore()
const route = useRoute()
const isVisible = useNavVisibility()
const { openChooser } = useTrackingDialogs()

// On phones the open keyboard pushes the bar over the content, so it steps aside while typing
const typing = useKeyboardFocus()

// With tracking, the diary takes the calculator's place: the calculator is a one-off tool and
// stays in the menu. Without tracking there is no diary, so the calculator stays here.
const mainNavigation: NavItem[] = [
	{ routeName: 'dashboard', label: 'Start', icon: LayoutDashboardIcon, visibility: 'user' },
	{ routeName: 'home', label: 'Start', icon: HomeIcon, visibility: 'guest' },
	{
		routeName: 'diary-food',
		label: 'Tagebuch',
		icon: NotebookPenIcon,
		activeOn: ['diary-food-day', 'diary-weight', 'diary-weight-week'],
		visibility: 'consent',
	},
	{ routeName: 'recipe-list', label: 'Kochbuch', icon: ChefHatIcon, visibility: 'always' },
	{ routeName: 'calorie-calculator', label: 'Rechner', icon: CalculatorIcon, visibility: 'always' },
	{ routeName: 'auth-login', label: 'Anmelden', icon: UserRoundIcon, visibility: 'guest' },
]

const hasTracking = computed<boolean>(() => auth.isLoggedIn && auth.hasDataConsent)

const filteredNavigation = computed<NavItem[]>(() =>
	mainNavigation.filter(
		(item) =>
			isVisible(item) && !(hasTracking.value && item.routeName === 'calorie-calculator'),
	),
)

const splitIndex = computed<number>(() => Math.ceil(filteredNavigation.value.length / 2))
</script>

<template>
	<nav
		aria-label="Hauptnavigation"
		class="fixed inset-x-0 bottom-0 z-30 pb-[env(safe-area-inset-bottom)] border-t border-border bg-surface xl:hidden"
		:class="{ 'max-md:hidden': typing }"
	>
		<ul class="flex max-w-xl py-2 mx-auto">
			<template
				v-for="(navItem, index) in filteredNavigation"
				:key="navItem.routeName"
			>
				<li
					v-if="index === splitIndex && hasTracking"
					class="flex-1 -mt-5 text-center"
				>
					<BaseButton
						size="icon-lg"
						aria-label="Eintrag hinzufügen"
						aria-haspopup="dialog"
						@click="openChooser"
					>
						<BaseIcon
							:icon="PlusIcon"
							:size="28"
						/>
					</BaseButton>
				</li>

				<li class="flex-1">
					<!-- The diary opens a choice between food and weight -->
					<DiaryDrawer v-if="navItem.routeName === 'diary-food'" />

					<!-- Cookbook, logged in: all recipes, own recipes and own meals. Guests only have the list. -->
					<AppNavDrawer
						v-else-if="navItem.routeName === 'recipe-list' && auth.isLoggedIn"
						id="recipes-drawer"
						label="Kochbuch"
						:icon="ChefHatIcon"
						:items="RECIPES_NAV"
					/>

					<RouterLink
						v-else
						:to="navItemLocation(navItem)"
						class="nav-item"
						:class="{ 'nav-item--active': isNavItemActive(navItem, route) }"
						:aria-current="isNavItemActive(navItem, route) ? 'page' : undefined"
					>
						<BaseIcon
							:icon="navItem.icon!"
							:size="24"
						/>

						<span class="text-md leading-none max-[359px]:sr-only">
							{{ navItem.label }}
						</span>
					</RouterLink>
				</li>
			</template>

			<li
				v-if="auth.isLoggedIn"
				class="flex-1"
			>
				<AccountDrawer />
			</li>
		</ul>
	</nav>
</template>
