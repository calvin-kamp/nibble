<script setup lang="ts">
import { useFieldValue, useSetFieldValue } from 'vee-validate'
import { computed, onMounted, watch } from 'vue'

import { kcalFromMacros } from '@features/tracking/tracking.utils'
import { CheckboxField, NumberField, TextField } from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

interface Props {
	/** Path of the values in the form, e.g. "manual" or "items[2].own" */
	path: string
}

const props = defineProps<Props>()

const field = (key: string) => `${props.path}.${key}`

const MACRO_KEYS = ['protein', 'carbs', 'fat'] as const

const protein = useFieldValue<number | undefined>(() => field('protein'))
const carbs = useFieldValue<number | undefined>(() => field('carbs'))
const fat = useFieldValue<number | undefined>(() => field('fat'))
const setKcal = useSetFieldValue<number | undefined>(() => field('kcal'))
const setters = Object.fromEntries(
	MACRO_KEYS.map((key) => [key, useSetFieldValue<number | undefined>(() => field(key))]),
) as Record<(typeof MACRO_KEYS)[number], (value: number | undefined, validate?: boolean) => void>

// Only in the form: kcal alone, or the macros with kcal computed from them. Not sent to the API.
const withMacros = useFieldValue<boolean | undefined>(() => field('withMacros'))
const setWithMacros = useSetFieldValue<boolean | undefined>(() => field('withMacros'))

const macros = computed(() => ({
	protein: protein.value ?? 0,
	carbs: carbs.value ?? 0,
	fat: fat.value ?? 0,
}))

const macroKcal = computed<number>(() => kcalFromMacros(macros.value))

function setMacros(value: number | undefined): void {
	for (const key of MACRO_KEYS) setters[key](value, false)
}

// An entry being edited that has macros starts with them, everything else with kcal only
onMounted(() => {
	if (withMacros.value !== undefined) return

	const hasMacros = Object.values(macros.value).some((value) => value > 0)

	setWithMacros(hasMacros, false)
	if (!hasMacros) setMacros(0)
})

// Without macros they count as 0, so the API gets complete values. With them the fields start
// empty, so nothing is saved as 0 by accident.
watch(withMacros, (next, previous) => {
	if (previous === undefined) return

	setMacros(next ? undefined : 0)
})

// With macros the kcal follow them
watch(macroKcal, (next) => {
	if (withMacros.value) setKcal(next, false)
})
</script>

<template>
	<div class="flex flex-col gap-4">
		<TextField
			:name="field('name')"
			label="Name"
			autocomplete="off"
		/>

		<CheckboxField
			:name="field('withMacros')"
			label="Makros eintragen"
			hint="Eiweiß, Kohlenhydrate und Fett. Die Kalorien rechnen wir daraus aus."
		/>

		<!-- v-show, not v-if: hidden fields stay registered, so their values stay in the form -->
		<div
			v-show="withMacros"
			class="flex flex-col gap-4"
		>
			<!-- By the width of the form, not the screen: in the dialog (max. 32rem) one below the
				other, on the wider meal page side by side -->
			<div class="@container">
				<div class="grid grid-cols-12 gap-4">
					<NumberField
						class="col-span-12 @xl:col-span-4"
						:name="field('protein')"
						label="Eiweiß"
						unit="g"
						:min="0"
						:step="0.1"
					/>

					<NumberField
						class="col-span-12 @xl:col-span-4"
						:name="field('carbs')"
						label="Kohlenhydrate"
						unit="g"
						:min="0"
						:step="0.1"
					/>

					<NumberField
						class="col-span-12 @xl:col-span-4"
						:name="field('fat')"
						label="Fett"
						unit="g"
						:min="0"
						:step="0.1"
					/>
				</div>
			</div>

			<p
				class="text-md text-muted-foreground"
				aria-live="polite"
			>
				Ergibt

				<strong class="text-foreground tabular-nums">
					{{ formatNumber(macroKcal) }} kcal
				</strong>

				(4 kcal je Gramm Eiweiß und Kohlenhydrate, 9 je Gramm Fett).
			</p>
		</div>

		<!-- Without macros only this field shows, in its own row and full width. Protein, carbs and
			fat are 0 in the background. -->
		<NumberField
			v-show="!withMacros"
			:name="field('kcal')"
			label="Kalorien"
			unit="kcal"
			:min="0"
			:step="1"
			:format-options="{ maximumFractionDigits: 0 }"
		/>
	</div>
</template>
