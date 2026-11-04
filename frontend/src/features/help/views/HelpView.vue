<script setup lang="ts">
import { ArrowRightIcon, AccessibilityIcon, CircleHelpIcon, RouteIcon } from '@lucide/vue'
import { RouterLink } from 'vue-router'

import HelpContact from '@features/help/components/HelpContact.vue'
import { BaseIcon } from '@shared/ui'

const PAGES = [
	{
		routeName: 'help-guide',
		icon: RouteIcon,
		title: 'So nutzt du nibble',
		text: 'Die wichtigsten Aufgaben Schritt für Schritt: einrichten, eintragen, Rezepte teilen.',
	},
	{
		routeName: 'help-faq',
		icon: CircleHelpIcon,
		title: 'Häufige Fragen',
		text: 'Antworten zu Tagebuch, Scanner, Rezepten, Einwilligung und deinem Konto.',
	},
	{
		routeName: 'help-accessibility',
		icon: AccessibilityIcon,
		title: 'Barrierefreiheit',
		text: 'Was nibble für Tastatur, Screenreader und Lesbarkeit tut und wo es noch Grenzen gibt.',
	},
]
</script>

<template>
	<main class="page">
		<div class="page__header">
			<div class="page__intro">
				<h1>
					Hilfe
				</h1>

				<p class="page__lead">
					Anleitungen, Antworten und alles zur Barrierefreiheit. Findest du nicht, was du
					suchst, schreib uns.
				</p>
			</div>
		</div>

		<ul class="help-hub">
			<li
				v-for="item in PAGES"
				:key="item.routeName"
				class="help-hub__card"
			>
				<span
					class="help-hub__icon"
					aria-hidden="true"
				>
					<BaseIcon
						:icon="item.icon"
						:size="24"
					/>
				</span>

				<h2 class="help-hub__title">
					<RouterLink
						:to="{ name: item.routeName }"
						class="help-hub__link"
					>
						{{ item.title }}
					</RouterLink>
				</h2>

				<p class="text-foreground/80">
					{{ item.text }}
				</p>

				<span
					class="help-hub__more"
					aria-hidden="true"
				>
					Öffnen

					<BaseIcon
						:icon="ArrowRightIcon"
						:size="18"
					/>
				</span>
			</li>
		</ul>

		<HelpContact />
	</main>
</template>
