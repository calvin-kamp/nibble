<script setup lang="ts">
import { CheckIcon } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed } from 'vue'

import OnboardingNav from '@features/onboarding/components/OnboardingNav.vue'
import OnboardingStep from '@features/onboarding/components/OnboardingStep.vue'
import { BaseIcon, BaseLink } from '@shared/ui'

import { CONSENT_LABEL } from '@features/legal/legal.constants'
import { consentSchema } from '@features/onboarding/onboarding.schema'
import { CheckboxField, focusFirstError } from '@shared/forms'

interface Props {
	consent: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
	next: [consent: boolean]
	back: []
}>()

const COMPARISON = [
	{
		id: 'consent-without',
		title: 'Ohne Einwilligung',
		items: [
			'Alle Rezepte ansehen, speichern und eigene teilen',
			'Kalorienrechner nutzen, ohne zu speichern',
		],
	},
	{
		id: 'consent-with',
		title: 'Mit Einwilligung',
		items: [
			'Gewicht und Verlauf festhalten',
			'Mahlzeiten eintragen',
			'Tagesbedarf speichern und im Dashboard sehen',
		],
	},
]

const { handleSubmit, values } = useForm({
	validationSchema: consentSchema,
	initialValues: { consent: props.consent },
})

const submitLabel = computed<string>(() => (values.consent ? 'Weiter' : 'Weiter ohne Einwilligung'))

const onSubmit = handleSubmit(
	(formValues) => emit('next', formValues.consent),
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<OnboardingStep
		title="Darf Nibble deine Daten speichern?"
		lead="Gewicht, Körperdaten, Ziele, Tagebuch und eigene Mahlzeiten können Gesundheitsdaten sein. Wir speichern sie nur mit deiner ausdrücklichen Einwilligung. Sie ist freiwillig und jederzeit widerrufbar."
		@submit="onSubmit"
	>
		<!-- Stacked: the step is never wider than max-w-3xl, side by side the columns get too narrow -->
		<div class="flex flex-col gap-6">
			<section
				v-for="column in COMPARISON"
				:key="column.id"
				class="flex flex-col gap-1"
				:aria-labelledby="`${column.id}-title`"
			>
				<h2
					:id="`${column.id}-title`"
					class="text-xl"
				>
					{{ column.title }}
				</h2>

				<ul>
					<li
						v-for="item in column.items"
						:key="item"
						class="flex gap-3 py-3 border-b border-divider last:border-b-0"
					>
						<!-- As high as a line of text, so the icon sits centered on the first line -->
						<span class="flex items-center shrink-0 h-lh">
							<BaseIcon
								class="text-brand"
								:icon="CheckIcon"
							/>
						</span>
						{{ item }}
					</li>
				</ul>
			</section>
		</div>

		<CheckboxField
			name="consent"
			:label="CONSENT_LABEL"
		/>

		<p>
			<BaseLink
				route-name="legal-privacy"
				target="_blank"
			>
				Datenschutzerklärung lesen
				<span class="sr-only">(öffnet in neuem Tab)</span>
			</BaseLink>
		</p>

		<OnboardingNav
			:submit-label="submitLabel"
			@back="emit('back')"
		/>
	</OnboardingStep>
</template>
