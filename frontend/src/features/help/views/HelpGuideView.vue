<script setup lang="ts">
import HelpContact from '@features/help/components/HelpContact.vue'
import HelpTopicNav from '@features/help/components/HelpTopicNav.vue'
import { BaseBreadcrumb, BaseLink } from '@shared/ui'

import { HELP_GUIDES } from '@features/help/help.guides'
</script>

<template>
	<main class="page page--compact">
		<BaseBreadcrumb
			:items="[{ label: 'Hilfe', routeName: 'help' }]"
			current="So nutzt du nibble"
		/>

		<div class="page__header">
			<div class="page__intro">
				<h1>
					So nutzt du nibble
				</h1>

				<p class="page__lead">
					Die wichtigsten Aufgaben Schritt für Schritt: vom Konto über das Tagebuch bis zu
					deinen Rezepten.
				</p>
			</div>
		</div>

		<div class="help">
			<HelpTopicNav
				route-name="help-guide"
				:topics="HELP_GUIDES"
			/>

			<div class="help__content">
				<section
					v-for="guide in HELP_GUIDES"
					:key="guide.id"
					class="help__topic"
					:aria-labelledby="guide.id"
				>
					<div class="section__intro">
						<h2
							:id="guide.id"
							class="help__heading"
							tabindex="-1"
						>
							{{ guide.title }}
						</h2>

						<p class="section__lead">
							{{ guide.lead }}
						</p>
					</div>

					<ol class="guide-steps">
						<li
							v-for="step in guide.steps"
							:key="step"
							class="guide-steps__item"
						>
							{{ step }}
						</li>
					</ol>

					<ul
						v-if="guide.links?.length"
						class="faq__links"
					>
						<li
							v-for="link in guide.links"
							:key="link.label"
						>
							<BaseLink :route-name="link.routeName">
								{{ link.label }}
							</BaseLink>
						</li>
					</ul>
				</section>

				<HelpContact />
			</div>
		</div>
	</main>
</template>
