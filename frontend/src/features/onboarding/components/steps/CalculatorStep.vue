<script setup lang="ts">
import type {
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
	/** Previous inputs, e.g. after a reload or from the calculator as a guest */
	values?: Partial<CalorieCalculatorValues>
	/** Calculator section on phones; without it, all sections at once */
	part?: number
	/** Show the result instead of the form. It is calculated from values. */
	showResult?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	goal: undefined,
	values: undefined,
	part: undefined,
	showResult: false,
})

const emit = defineEmits<{
	/** All details are valid, the result comes next */
	calculated: [values: CalorieCalculatorValues]
	/** The value from the result is adopted */
	confirm: [payload: { needs: DailyNeeds; goal: Goal }]
	back: []
	'part-complete': [values: Partial<CalorieCalculatorValues>]
	'go-to-part': [part: number]
}>()

// The goal chosen in onboarding takes precedence over the one from the guest calculator
const initialValues = { ...props.values, goal: props.goal ?? props.values?.goal }

const result = computed<CalorieResultData | null>(() =>
	props.showResult && props.values
		? calculateCalories(props.values as CalorieCalculatorValues)
		: null,
)

// Back from the result: the form is visible again and its heading receives focus
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
		wide
		title="Wir berechnen deinen Tagesbedarf"
		lead="Ein paar Angaben zu dir und deiner Bewegung, dann steht dein Richtwert."
	>
		<!-- v-show instead of v-if: after going back from the result, the inputs are still there -->
		<CalorieCalculatorForm
			v-show="!result"
			ref="form"
			:initial-values="initialValues"
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

		<!-- The result with all notes, before the value is adopted -->
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
