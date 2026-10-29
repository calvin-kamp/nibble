<script setup lang="ts">
import {
	CalculatorIcon,
	ChefHatIcon,
	HomeIcon,
	LayoutDashboardIcon,
	PlusIcon,
	UserRoundIcon,
} from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import AccountDrawer from '@features/account/components/AccountDrawer.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'

import { useAuthStore } from '@features/auth/auth.store'

const auth = useAuthStore()
const { openChooser } = useTrackingDialogs()

const mainNavigation = [
	{
		routeName: 'dashboard',
		label: 'Übersicht',
		icon: LayoutDashboardIcon,
		visibility: 'user',
	},
	{
		routeName: 'home',
		label: 'Start',
		icon: HomeIcon,
		visibility: 'guest',
	},
	{
		routeName: 'recipe-list',
		label: 'Rezepte',
		icon: ChefHatIcon,
		visibility: 'always',
	},
	{
		routeName: 'calorie-calculator',
		label: 'Rechner',
		icon: CalculatorIcon,
		visibility: 'always',
	},
	{
		routeName: 'auth-login',
		label: 'Anmelden',
		icon: UserRoundIcon,
		visibility: 'guest',
	},
]

const filteredNavigation = computed(() =>
	mainNavigation.filter(
		(item) =>
			item.visibility === 'always' ||
			item.visibility === (auth.isLoggedIn ? 'user' : 'guest'),
	),
)

// The tracking button sits in the middle of the bar
const splitIndex = computed<number>(() => Math.ceil(filteredNavigation.value.length / 2))
</script>

<template>
	<nav
		aria-label="Hauptnavigation"
		class="fixed inset-x-0 bottom-0 z-30 pb-[env(safe-area-inset-bottom)] border-t border-line bg-surface xl:hidden"
	>
		<ul class="flex max-w-xl py-2 mx-auto">
			<template
				v-for="(navItem, index) in filteredNavigation"
				:key="navItem.routeName"
			>
				<li
					v-if="index === splitIndex && auth.isLoggedIn && auth.hasDataConsent"
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
					<RouterLink
						:to="{ name: navItem.routeName }"
						class="nav-item"
						active-class="nav-item--active"
					>
						<BaseIcon
							:icon="navItem.icon"
							:size="24"
						/>

						<span class="sr-only md:not-sr-only">{{ navItem.label }}</span>
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
