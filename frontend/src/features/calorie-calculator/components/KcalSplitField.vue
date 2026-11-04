<script setup lang="ts">
import { useFieldValue, useSetFieldValue } from 'vee-validate'

import { BaseButton } from '@shared/ui'

import { DEFAULT_MACRO_SPLIT, splitKcal } from '@features/calorie-calculator/calorie-calculator.utils'
import { NumberField } from '@shared/forms'

// For people who only know their calorie target: fills the protein, carbs and fat fields of
// the surrounding form. The kcal field itself is not part of the schema and is not saved.
const kcalTarget = useFieldValue<number | undefined>('kcalTarget')
const setProtein = useSetFieldValue<number>('protein')
const setCarbs = useSetFieldValue<number>('carbs')
const setFat = useSetFieldValue<number>('fat')

const percent = (share: number) => Math.round(share * 100)
const hint =
	`Wir teilen sie auf: ${percent(DEFAULT_MACRO_SPLIT.protein)} % Protein, ` +
	`${percent(DEFAULT_MACRO_SPLIT.carbs)} % Kohlenhydrate, ` +
	`${percent(DEFAULT_MACRO_SPLIT.fat)} % Fett. Danach kannst du die Gramm anpassen.`

function split(): void {
	if (!kcalTarget.value) return

	const macros = splitKcal(kcalTarget.value)

	setProtein(macros.protein)
	setCarbs(macros.carbs)
	setFat(macros.fat)
}
</script>

<template>
	<!-- Enter splits instead of submitting the form with empty macros -->
	<!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
	<div
		class="flex flex-col gap-3 p-4 rounded-md bg-muted sm:flex-row sm:items-end"
		@keydown.enter.prevent="split"
	>
		<NumberField
			class="flex-1"
			name="kcalTarget"
			label="Du kennst nur deine Kalorien?"
			:hint="hint"
			unit="kcal"
			:min="0"
		/>

		<BaseButton
			class="shrink-0"
			variant="outline"
			:disabled="!kcalTarget"
			@click="split"
		>
			Aufteilen
		</BaseButton>
	</div>
</template>
