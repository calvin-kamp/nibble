<script setup lang="ts">
import type { NavItem } from '@layouts/navigation'

import { PlusIcon } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import AppLogo from '@layouts/AppLogo.vue'
import AppNavGroup from '@layouts/AppNavGroup.vue'
import { BaseButton, BaseIcon, BaseLink } from '@shared/ui'

import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'

import { useAuthStore } from '@features/auth/auth.store'
import {
	ADMIN_NAV,
	DISCOVER_NAV,
	LEGAL_NAV,
	MAIN_NAV,
	TRACKING_NAV,
	navItemLocation,
	useNavVisibility,
} from '@layouts/navigation'

const route = useRoute()
const auth = useAuthStore()
const { openChooser } = useTrackingDialogs()
const isVisible = useNavVisibility()

const legalItems = computed<NavItem[]>(() => LEGAL_NAV.filter(isVisible))
</script>

<template>
	<!-- From desktop up. Below that, the header menu and bottom navigation take over. -->
	<aside
		class="sidebar"
		aria-label="Seitenleiste"
	>
		<AppLogo :route-name="auth.isLoggedIn ? 'dashboard' : 'home'" />

		<BaseButton
			v-if="auth.isLoggedIn && auth.hasDataConsent"
			class="w-full"
			@click="openChooser"
		>
			<BaseIcon :icon="PlusIcon" />
			Eintrag hinzufügen
		</BaseButton>

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
		</nav>

		<div class="flex flex-col gap-8 mt-auto">
			<section
				v-if="!auth.isLoggedIn"
				class="flex flex-col gap-4"
				aria-label="Konto anlegen"
			>
				<div class="flex flex-col gap-1">
					<p class="text-xl font-bold">Tagebuch, Ziele, Gewicht</p>

					<p class="text-sm text-muted">Mit einem kostenlosen Konto.</p>
				</div>

				<div class="flex flex-col gap-3">
					<BaseButton
						class="w-full rounded-full"
						route-name="auth-register"
						>Konto anlegen</BaseButton
					>

					<!-- There is no sign-in button in the header any more; on desktop it lives here -->
					<p class="text-sm text-center text-ink-soft">
						Schon ein Konto?
						<BaseLink
							route-name="auth-login"
							:query="{ weiter: route.fullPath }"
							variant="inline"
						>
							Anmelden
						</BaseLink>
					</p>
				</div>
			</section>

			<nav
				class="flex flex-col gap-1"
				aria-labelledby="sidebar-legal-title"
			>
				<h2
					id="sidebar-legal-title"
					class="sidebar__heading"
				>
					Rechtliches
				</h2>

				<ul class="flex flex-col items-start px-3">
					<li
						v-for="item in legalItems"
						:key="item.label"
					>
						<RouterLink
							:to="navItemLocation(item)"
							class="sidebar__legal-link"
							>{{ item.label }}</RouterLink
						>
					</li>
				</ul>
			</nav>
		</div>
	</aside>
</template>
