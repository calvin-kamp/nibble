<script setup lang="ts">
import { LogInIcon, MenuIcon, UserPlusIcon } from '@lucide/vue'
import { Separator } from 'reka-ui'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import AppLogo from '@layouts/AppLogo.vue'
import AppNavGroup from '@layouts/AppNavGroup.vue'
import { BaseButton, BaseIcon, BaseSheet } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'
import { ADMIN_NAV, DISCOVER_NAV, LEGAL_NAV, MAIN_NAV, TRACKING_NAV } from '@layouts/navigation'

// Menu for phone and tablet: the same items as the desktop sidebar, in groups.
// For guests, sign in and register follow below.
const route = useRoute()
const auth = useAuthStore()

const open = ref<boolean>(false)

// Do not redirect the sign-in pages back to themselves
const loginQuery = computed(() =>
	route.meta.navigation === 'header' ? undefined : { weiter: route.fullPath },
)

// Close after a link is clicked, so the new page is visible
watch(
	() => route.fullPath,
	() => (open.value = false),
)
</script>

<template>
	<BaseButton
		variant="ghost"
		size="icon"
		aria-label="Menü öffnen"
		aria-haspopup="dialog"
		aria-controls="app-mobile-menu"
		:aria-expanded="open"
		@click="open = true"
	>
		<BaseIcon
			:icon="MenuIcon"
			:size="24"
		/>
	</BaseButton>

	<BaseSheet
		id="app-mobile-menu"
		v-model:open="open"
		title="Menü"
		title-hidden
	>
		<template #header>
			<AppLogo :route-name="auth.isLoggedIn ? 'dashboard' : 'home'" />
		</template>

		<!-- Separator and sign-in sit closer together than the sheet gap -->
		<div class="flex flex-col gap-6">
			<nav
				class="flex flex-col gap-8"
				aria-label="Hauptnavigation"
			>
				<AppNavGroup :items="MAIN_NAV" />

				<AppNavGroup
					label="Tagebuch"
					:items="TRACKING_NAV"
				/>

				<AppNavGroup
					label="Entdecken"
					:items="DISCOVER_NAV"
				/>

				<AppNavGroup
					label="Verwaltung"
					:items="ADMIN_NAV"
				/>

				<AppNavGroup
					label="Rechtliches"
					:items="LEGAL_NAV"
				/>
			</nav>

			<!-- For guests, after the last group. After signing in, the user returns to this page. -->
			<template v-if="!auth.isLoggedIn">
				<Separator
					class="h-px bg-line"
					decorative
				/>

				<div class="flex flex-col gap-3">
					<BaseButton
						route-name="auth-login"
						:query="loginQuery"
					>
						<BaseIcon :icon="LogInIcon" />
						Anmelden
					</BaseButton>

					<BaseButton
						variant="outline"
						route-name="auth-register"
					>
						<BaseIcon :icon="UserPlusIcon" />
						Registrieren
					</BaseButton>
				</div>
			</template>
		</div>
	</BaseSheet>
</template>
