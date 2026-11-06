<script setup lang="ts">
import { PlusIcon } from '@lucide/vue'
import { useRoute } from 'vue-router'

import AccountMenu from '@features/account/components/AccountMenu.vue'
import AppLogo from '@layouts/AppLogo.vue'
import AppNavGroup from '@layouts/AppNavGroup.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'

import { useAuthStore } from '@features/auth/auth.store'
import { ADMIN_NAV, DISCOVER_NAV, HELP_NAV, MAIN_NAV, TRACKING_NAV } from '@layouts/navigation'

const route = useRoute()
const auth = useAuthStore()
const { openChooser } = useTrackingDialogs()
</script>

<template>
	<aside
		class="sidebar"
		aria-label="Seitenleiste"
	>
		<div class="sidebar__brand">
			<AppLogo :route-name="auth.isLoggedIn ? 'dashboard' : 'home'" />
		</div>

		<BaseButton
			v-if="auth.isLoggedIn && auth.hasDataConsent"
			class="w-full"
			aria-haspopup="dialog"
			@click="openChooser"
		>
			<BaseIcon :icon="PlusIcon" />

			Eintrag hinzufügen
		</BaseButton>

		<nav
			class="flex flex-col gap-7"
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
				label="Admin"
				:items="ADMIN_NAV"
			/>
		</nav>

		<div class="flex flex-col gap-4 mt-auto">
			<nav aria-label="Hilfe">
				<AppNavGroup :items="HELP_NAV" />
			</nav>

			<div class="sidebar__account">
				<AccountMenu v-if="auth.isLoggedIn" />

				<template v-else>
					<BaseButton
						class="w-full"
						route-name="auth-register"
					>
						Registrieren
					</BaseButton>

					<BaseButton
						class="w-full"
						variant="outline"
						route-name="auth-login"
						:query="{ weiter: route.fullPath }"
					>
						Anmelden
					</BaseButton>
				</template>
			</div>
		</div>
	</aside>
</template>
