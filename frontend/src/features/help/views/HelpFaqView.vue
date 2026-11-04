<script setup lang="ts">
import { ChevronDownIcon } from '@lucide/vue'

import HelpContact from '@features/help/components/HelpContact.vue'
import HelpTopicNav from '@features/help/components/HelpTopicNav.vue'
import { BaseBreadcrumb, BaseIcon, BaseLink } from '@shared/ui'

import { HELP_TOPICS } from '@features/help/help.constants'
</script>

<template>
	<main class="page page--compact">
		<BaseBreadcrumb
			:items="[{ label: 'Hilfe', routeName: 'help' }]"
			current="Häufige Fragen"
		/>

		<div class="page__header">
			<div class="page__intro">
				<h1>
					Häufige Fragen
				</h1>

				<p class="page__lead">
					Antworten zu Tagebuch, Rezepten und deinen Daten. Findest du deine Frage nicht,
					schreib uns.
				</p>
			</div>
		</div>

		<div class="help">
			<HelpTopicNav
				route-name="help-faq"
				:topics="[...HELP_TOPICS, { id: 'kontakt', title: 'Kontakt' }]"
			/>

			<div class="help__content">
				<section
					v-for="topic in HELP_TOPICS"
					:key="topic.id"
					class="help__topic"
					:aria-labelledby="topic.id"
				>
					<div class="section__intro">
						<h2
							:id="topic.id"
							class="help__heading"
							tabindex="-1"
						>
							{{ topic.title }}
						</h2>

						<p class="section__lead">
							{{ topic.lead }}
						</p>
					</div>

					<div class="faq">
						<details
							v-for="item in topic.questions"
							:id="item.id"
							:key="item.id"
							class="faq__item"
						>
							<summary class="faq__question">
								<span>
									{{ item.question }}
								</span>

								<BaseIcon
									class="faq__chevron"
									:icon="ChevronDownIcon"
								/>
							</summary>

							<div class="faq__answer">
								<p
									v-for="(paragraph, index) in item.answer"
									:key="index"
								>
									{{ paragraph }}
								</p>

								<ul
									v-if="item.links?.length"
									class="faq__links"
								>
									<li
										v-for="link in item.links"
										:key="link.label"
									>
										<BaseLink
											:route-name="link.routeName"
											:hash="link.hash"
											:href="link.href"
										>
											{{ link.label }}
										</BaseLink>
									</li>
								</ul>
							</div>
						</details>
					</div>
				</section>

				<HelpContact />
			</div>
		</div>
	</main>
</template>
