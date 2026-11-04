<script setup lang="ts">
import { MailIcon } from '@lucide/vue'

import { BaseIcon, BaseLink } from '@shared/ui'

import { OPERATOR } from '@features/legal/legal.constants'
import { ACCESSIBILITY_EMAIL, CONTACT_EMAIL, SUPPORT_EMAIL } from '@shared/constants'

const CHANNELS = [
	{ label: 'Fragen zur App und Probleme', email: SUPPORT_EMAIL },
	{ label: 'Barrieren in nibble', email: ACCESSIBILITY_EMAIL },
	{ label: 'Fragen zu deinen Daten und zur Einwilligung', email: OPERATOR.privacyEmail },
	{ label: 'Alles andere', email: CONTACT_EMAIL },
]
</script>

<template>
	<section
		class="help__contact on-forest"
		aria-labelledby="kontakt"
	>
		<div class="section__intro">
			<h2
				id="kontakt"
				class="help__heading"
				tabindex="-1"
			>
				Noch Fragen?
			</h2>

			<p class="text-forest-muted-foreground">
				Schreib uns eine E-Mail, wir antworten so bald wie möglich.
			</p>
		</div>

		<dl class="help__channels">
			<div
				v-for="channel in CHANNELS"
				:key="channel.email"
				class="help__channel"
			>
				<dt class="text-md text-forest-muted-foreground">
					{{ channel.label }}
				</dt>

				<dd>
					<a
						class="help__mail"
						:href="`mailto:${channel.email}`"
					>
						<BaseIcon
							class="max-md:hidden"
							:icon="MailIcon"
						/>

						{{ channel.email }}
					</a>
				</dd>
			</div>
		</dl>

		<p class="text-md text-forest-muted-foreground">
			Anschrift und weitere Angaben findest du im

			<BaseLink
				route-name="legal-notice"
				variant="inline"
				class="text-forest-foreground hover:text-highlight"
			>
				Impressum
			</BaseLink>.
		</p>
	</section>
</template>
