<script setup lang="ts">
import type { NavItem } from '@layouts/navigation'

import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AppLogo from '@layouts/AppLogo.vue'
import { BaseLink } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'
import { OPERATOR } from '@features/legal/legal.constants'
import {
	FOOTER_APP_NAV,
	HELP_TOPICS_NAV,
	isNavItemActive,
	LEGAL_NAV,
	useNavVisibility,
} from '@layouts/navigation'

const route = useRoute()
const auth = useAuthStore()
const isVisible = useNavVisibility()

const groups = computed<{ id: string; label: string; items: NavItem[] }[]>(() => [
	{ id: 'footer-app', label: 'App', items: FOOTER_APP_NAV.filter(isVisible) },
	{ id: 'footer-help', label: 'Hilfe', items: HELP_TOPICS_NAV },
	{ id: 'footer-legal', label: 'Rechtliches', items: LEGAL_NAV },
])

const year = new Date().getFullYear()
</script>

<template>
	<footer class="site-footer on-forest">
		<div class="site-footer__inner">
			<div class="site-footer__brand">
				<AppLogo
					class="site-footer__logo"
					size="lg"
					:route-name="auth.isLoggedIn ? 'dashboard' : 'home'"
				/>

				<p class="site-footer__tagline">
					Iss gut. <br />Wir rechnen mit.
				</p>

				<p class="site-footer__note">
					Ernährungstagebuch und Rezeptsammlung. Deine Gesundheitsdaten speichern wir nur
					mit deiner Einwilligung, jederzeit widerrufbar.
				</p>
			</div>

			<div class="site-footer__nav">
				<nav
					v-for="group in groups"
					:key="group.id"
					:aria-labelledby="`${group.id}-title`"
				>
					<h2
						:id="`${group.id}-title`"
						class="site-footer__heading"
					>
						{{ group.label }}
					</h2>

					<ul class="flex flex-col">
						<li
							v-for="item in group.items"
							:key="`${item.label}${item.hash ?? ''}`"
						>
							<BaseLink
								variant="nav"
								class="site-footer__link"
								:route-name="item.routeName"
								:query="item.query"
								:hash="item.hash"
								:aria-current="
									!item.hash && isNavItemActive(item, route) ? 'page' : 'false'
								"
							>
								{{ item.label }}
							</BaseLink>
						</li>
					</ul>
				</nav>
			</div>
		</div>

		<div class="site-footer__bottom">
			<p>
				© {{ year }} {{ OPERATOR.name }}
			</p>

			<p class="site-footer__credit">
				Lebensmitteldaten von

				<BaseLink
					href="https://world.openfoodfacts.org"
					class="text-highlight"
				>
					Open Food Facts
				</BaseLink>, verfügbar unter der

				<BaseLink
					href="https://opendatacommons.org/licenses/odbl/1-0/"
					class="text-highlight"
					lang="en"
				>
					Open Database License
				</BaseLink>
			</p>
		</div>
	</footer>
</template>
