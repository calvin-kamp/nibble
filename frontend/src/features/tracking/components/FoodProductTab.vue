<script setup lang="ts">
import type { FoodProduct, FoodUnit, Nutrition } from '@features/tracking/tracking.types'
import type { FieldOption } from '@shared/forms/types'

import { useFieldError, useFieldValue, useSetFieldValue } from 'vee-validate'
import { computed, nextTick, ref, watch } from 'vue'

import FoodSearchField from '@features/tracking/components/FoodSearchField.vue'
import NutritionFacts from '@features/tracking/components/NutritionFacts.vue'
import { BaseButton } from '@shared/ui'

import {
	formatUnitOption,
	nutritionFor,
	toQuantity,
	unitsOf,
} from '@features/tracking/tracking.utils'
import { NumberField, SelectField } from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

// "Lebensmittel" tab in the food dialog: search, then choose amount and unit. The nutrition
// values below are recalculated on every change. Runs inside FoodEntryForm's form.
const product = defineModel<FoodProduct | null>('product', { required: true })

const setProductCode = useSetFieldValue<string | undefined>('productCode')
const setAmount = useSetFieldValue<number | undefined>('amount')
const setUnit = useSetFieldValue<FoodUnit | undefined>('unit')
const amount = useFieldValue<number | undefined>('amount')
const unit = useFieldValue<FoodUnit | undefined>('unit')
const productError = useFieldError('productCode')

const root = ref<HTMLElement | null>(null)

async function focusFirstInput(): Promise<void> {
	await nextTick()
	root.value?.querySelector<HTMLElement>('input')?.focus()
}

/** Suggestion per unit: one serving or package, otherwise 100 g or ml */
function defaultAmount(target: FoodUnit): number {
	return target === 'serving' || target === 'package' ? 1 : 100
}

function choose(selected: FoodProduct): void {
	const firstUnit: FoodUnit = selected.serving ? 'serving' : selected.unit

	product.value = selected
	setProductCode(selected.code, false)
	setUnit(firstUnit, false)
	setAmount(defaultAmount(firstUnit), false)
	focusFirstInput()
}

function clear(): void {
	product.value = null
	setProductCode(undefined, false)
	setAmount(undefined, false)
	setUnit(undefined, false)
	focusFirstInput()
}

const unitOptions = computed<FieldOption[]>(() =>
	product.value
		? unitsOf(product.value).map((value) => ({
				value,
				label: formatUnitOption(product.value!, value),
			}))
		: [],
)

// A different unit starts with its own suggestion, otherwise 80 g would become 80 servings.
// When selecting or resetting there is no previous unit, so the amount stays.
watch(unit, (next, previous) => {
	if (next && previous) setAmount(defaultAmount(next))
})

const nutrition = computed<Nutrition | null>(() => {
	if (!product.value || !amount.value || !unit.value) return null

	return nutritionFor(product.value, toQuantity(product.value, amount.value, unit.value).base)
})
</script>

<template>
	<div
		ref="root"
		class="flex flex-col gap-5"
	>
		<!-- In the dialog the search is the first thing to do, so it takes focus on open -->
		<!-- eslint-disable vuejs-accessibility/no-autofocus -->
		<FoodSearchField
			v-if="!product"
			autofocus
			:error="productError"
			@select="choose"
		/>
		<!-- eslint-enable vuejs-accessibility/no-autofocus -->

		<template v-else>
			<div
				class="flex items-start justify-between gap-4 px-4 py-3 rounded-md bg-surface-muted"
			>
				<p class="flex flex-col min-w-0">
					<span class="font-semibold">{{ product.name }}</span>

					<span class="text-sm text-muted">
						<template v-if="product.brand">{{ product.brand }} · </template>
						{{ formatNumber(product.per100.kcal) }} kcal pro 100 {{ product.unit }}
					</span>
				</p>

				<BaseButton
					class="shrink-0"
					variant="outline"
					size="sm"
					@click="clear"
				>
					Ändern<span class="sr-only">: anderes Lebensmittel suchen</span>
				</BaseButton>
			</div>

			<!-- The unit gets more room, e.g. for "Packung (1.000 ml)" -->
			<div class="grid grid-cols-12 gap-4">
				<NumberField
					class="col-span-5"
					name="amount"
					label="Menge"
					:min="0"
					:step="0.1"
				/>

				<SelectField
					class="col-span-7"
					name="unit"
					label="Einheit"
					:options="unitOptions"
				/>
			</div>

			<!-- Nutrition values for the chosen amount. aria-live: announced after a new amount. -->
			<NutritionFacts
				class="py-4 border-y border-divider"
				:nutrition="nutrition"
				aria-live="polite"
			/>
		</template>
	</div>
</template>
