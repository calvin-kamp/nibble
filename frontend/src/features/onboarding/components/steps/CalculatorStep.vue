<script setup lang="ts">
import type {
	CalculatorSection,
	CalorieCalculatorValues,
	CalorieResult as CalorieResultData,
	Goal,
} from '@features/calorie-calculator/calorie-calculator.types'
import type { DailyNeeds } from '@features/onboarding/onboarding.types'

import { ArrowRightIcon } from '@lucide/vue'
import { computed, nextTick, ref, watch } from 'vue'

import CalorieCalculatorForm from '@features/calorie-calculator/components/CalorieCalculatorForm.vue'
import CalorieResult from '@features/calorie-calculator/components/CalorieResult.vue'
import OnboardingNav from '@features/onboarding/components/OnboardingNav.vue'
import OnboardingStep from '@features/onboarding/components/OnboardingStep.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import {
	calculateCalories,
	resultToNeeds,
} from '@features/calorie-calculator/calorie-calculator.utils'

interface Props {
	goal?: Goal
	values?: Partial<CalorieCalculatorValues>
	sections?: readonly CalculatorSection[]
	part?: number
	showResult?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	goal: undefined,
	values: undefined,
	sections: undefined,
	part: undefined,
	showResult: false,
})

const emit = defineEmits<{
	calculated: [values: CalorieCalculatorValues]
	confirm: [payload: { needs: DailyNeeds; goal: Goal }]
	back: []
	'part-complete': [values: Partial<CalorieCalculatorValues>]
	'go-to-part': [part: number]
}>()

// The goal chosen in onboarding takes precedence over the one from the guest calculator. The
// calculator does not ask for it again, so without a choice it calculates for maintenance.
const initialValues = { ...props.values, goal: props.goal ?? props.values?.goal ?? 'maintain' }

const result = computed<CalorieResultData | null>(() =>
	props.showResult && props.values
		? calculateCalories(props.values as CalorieCalculatorValues)
		: null,
)

const form = ref<InstanceType<typeof CalorieCalculatorForm> | null>(null)

watch(
	() => props.showResult,
	async (showResult) => {
		if (showResult) return

		await nextTick()
		form.value?.focusHeading()
	},
)

function onConfirm(): void {
	emit('confirm', { goal: props.values!.goal!, needs: resultToNeeds(result.value!) })
}
</script>

<template>
	<OnboardingStep
		as="section"
		:title="result ? 'Dein Tagesbedarf' : 'Wir berechnen deinen Tagesbedarf'"
		:lead="
			result
				? 'Passt der Wert, übernimm ihn. Sonst geh zurück und ändere deine Angaben.'
				: 'Ein paar Angaben zu dir und deiner Bewegung, dann steht dein Richtwert.'
		"
	>
		<!-- v-show instead of v-if: after going back from the result, the inputs are still there -->
		<CalorieCalculatorForm
			v-show="!result"
			ref="form"
			:initial-values="initialValues"
			:sections="props.sections"
			:part="props.part"
			@calculate="emit('calculated', $event)"
			@part-complete="emit('part-complete', $event)"
			@go-to-part="emit('go-to-part', $event)"
		>
			<template #actions="{ isLastPart }">
				<OnboardingNav
					:submit-label="isLastPart ? 'Bedarf berechnen' : 'Weiter'"
					@back="emit('back')"
				/>
			</template>
		</CalorieCalculatorForm>

		<template v-if="result && props.values">
			<CalorieResult
				:result="result"
				:values="props.values as CalorieCalculatorValues"
			/>

			<OnboardingNav @back="emit('back')">
				<template #primary>
					<BaseButton @click="onConfirm">
						Wert übernehmen

						<BaseIcon :icon="ArrowRightIcon" />
					</BaseButton>
				</template>
			</OnboardingNav>
		</template>
	</OnboardingStep>
</template>
