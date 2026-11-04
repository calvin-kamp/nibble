<script setup lang="ts">
import type { BodyData } from '@features/onboarding/onboarding.types'

import { useForm } from 'vee-validate'

import OnboardingNav from '@features/onboarding/components/OnboardingNav.vue'
import OnboardingStep from '@features/onboarding/components/OnboardingStep.vue'

import { SEX_OPTIONS } from '@features/calorie-calculator/calorie-calculator.constants'
import { bodyDataSchema } from '@features/onboarding/onboarding.schema'
import { DateField, focusFirstError, NumberField, RadioField } from '@shared/forms'
import { toIsoDate } from '@shared/utils/date'

interface Props {
	body?: BodyData
}

const props = withDefaults(defineProps<Props>(), {
	body: undefined,
})

const emit = defineEmits<{
	next: [body: BodyData | undefined]
	back: []
}>()

const { handleSubmit } = useForm<BodyData>({
	validationSchema: bodyDataSchema,
	initialValues: { ...props.body },
})

const onSubmit = handleSubmit(
	(values) => {
		const entered = Object.fromEntries(
			Object.entries(values).filter(([, value]) => value !== undefined),
		) as BodyData

		emit('next', Object.keys(entered).length ? entered : undefined)
	},
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<OnboardingStep
		title="Erzähl uns etwas über dich"
		lead="Damit füllen wir den Kalorienrechner vor, dein Gewicht wird der erste Eintrag im Gewichtstagebuch. Lass leer, was du nicht angeben möchtest: Du kannst alles später in den Einstellungen eintragen."
		@submit="onSubmit"
	>
		<div class="grid grid-cols-12 gap-5">
			<RadioField
				class="col-span-12 sm:col-span-6"
				name="sex"
				label="Geschlecht"
				orientation="horizontal"
				:options="SEX_OPTIONS"
			/>

			<DateField
				class="col-span-12 sm:col-span-6"
				name="birthDate"
				label="Geburtsdatum"
				:max="toIsoDate()"
			/>

			<NumberField
				class="col-span-12 sm:col-span-6"
				name="heightCm"
				label="Größe"
				unit="cm"
				:format-options="{ maximumFractionDigits: 0 }"
			/>

			<NumberField
				class="col-span-12 sm:col-span-6"
				name="weightKg"
				label="Gewicht"
				unit="kg"
				:step="0.1"
				:format-options="{ minimumFractionDigits: 1, maximumFractionDigits: 1 }"
			/>
		</div>

		<OnboardingNav @back="emit('back')" />
	</OnboardingStep>
</template>
