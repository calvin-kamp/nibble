<script setup lang="ts">
import { LogInIcon, MenuIcon, UserPlusIcon } from '@lucide/vue'
import { Separator } from 'reka-ui'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import AppLogo from '@layouts/AppLogo.vue'
import AppNavGroup from '@layouts/AppNavGroup.vue'
import { BaseButton, BaseIcon, BaseSheet } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'
import {
	ADMIN_NAV,
	DISCOVER_NAV,
	HELP_NAV,
	LEGAL_NAV,
	MAIN_NAV,
	TRACKING_NAV,
} from '@layouts/navigation'

const route = useRoute()
const auth = useAuthStore()

const open = ref<boolean>(false)

const loginQuery = computed(() =>
	route.meta.navigation === 'header' ? undefined : { weiter: route.fullPath },
)

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
		side="right"
		title="Menü"
		title-hidden
	>
		<template #header>
			<AppLogo :route-name="auth.isLoggedIn ? 'dashboard' : 'home'" />
		</template>

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

				<AppNavGroup :items="HELP_NAV" />

				<AppNavGroup
					label="Rechtliches"
					:items="LEGAL_NAV"
				/>
			</nav>

			<template v-if="!auth.isLoggedIn">
				<Separator
					class="h-px bg-divider"
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
