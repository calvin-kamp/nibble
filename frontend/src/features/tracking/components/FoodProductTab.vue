<script setup lang="ts">
import type { FoodEntry, FoodProduct, FoodUnit, Nutrition } from '@features/tracking/tracking.types'
import type { FieldOption } from '@shared/forms/types'

import { useFieldError, useFieldValue, useSetFieldValue, useSubmitCount } from 'vee-validate'
import { computed, nextTick, onMounted, ref, watch } from 'vue'

import FoodSearchField from '@features/tracking/components/FoodSearchField.vue'
import NutritionFacts from '@features/tracking/components/NutritionFacts.vue'
import { BaseButton } from '@shared/ui'

import { useBreakpoint } from '@shared/composables/breakpoint'
import { useToast } from '@shared/composables/toast'

import { fetchRecentFoods, findByBarcode } from '@features/tracking/tracking.api'
import {
	formatUnitOption,
	nutritionFor,
	toQuantity,
	unitsOf,
} from '@features/tracking/tracking.utils'
import { NumberField, SelectField } from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

const product = defineModel<FoodProduct | null>('product', { required: true })

const RECENT_FOODS_SHOWN = 6
const toast = useToast()

const setProductCode = useSetFieldValue<string | undefined>('productCode')
const setAmount = useSetFieldValue<number | undefined>('amount')
const setUnit = useSetFieldValue<FoodUnit | undefined>('unit')
const amount = useFieldValue<number | undefined>('amount')
const unit = useFieldValue<FoodUnit | undefined>('unit')
// The form checks itself as soon as the date field reports its first value. "Nothing chosen"
// is only an error once the user tried to save.
const productFieldError = useFieldError('productCode')
const submitCount = useSubmitCount()
const productError = computed<string | undefined>(() =>
	submitCount.value > 0 ? productFieldError.value : undefined,
)

const root = ref<HTMLElement | null>(null)

async function focusFirstInput(): Promise<void> {
	await nextTick()
	root.value?.querySelector<HTMLElement>('input')?.focus()
}

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

const { isTablet } = useBreakpoint()
const recentFoods = ref<FoodEntry[]>([])
const loadingCode = ref<string | null>(null)

onMounted(async () => {
	recentFoods.value = await fetchRecentFoods(RECENT_FOODS_SHOWN).catch(() => [])
})

async function chooseRecent(entry: FoodEntry): Promise<void> {
	loadingCode.value = entry.productCode ?? null

	try {
		const found = entry.productCode ? await findByBarcode(entry.productCode) : null

		if (found) choose(found)
		else toast.show(`${entry.name} ist nicht mehr in der Lebensmittelsuche.`, 'danger')
	} catch {
		toast.show('Das Lebensmittel konnte nicht geladen werden.', 'danger')
	} finally {
		loadingCode.value = null
	}
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
		<template v-if="!product">
			<!-- eslint-disable vuejs-accessibility/no-autofocus -->
			<FoodSearchField
				autofocus
				:error="productError"
				@select="choose"
			/>
			<!-- eslint-enable vuejs-accessibility/no-autofocus -->

			<section
				v-if="isTablet && recentFoods.length"
				class="flex flex-col gap-2"
				aria-labelledby="recent-foods-title"
			>
				<h3
					id="recent-foods-title"
					class="font-sans text-md font-semibold tracking-normal text-foreground"
				>
					Zuletzt eingetragen
				</h3>

				<ul class="flex flex-wrap gap-2">
					<li
						v-for="entry in recentFoods"
						:key="entry.productCode"
					>
						<BaseButton
							variant="outline"
							size="sm"
							:disabled="loadingCode !== null"
							@click="chooseRecent(entry)"
						>
							{{ entry.name }}
						</BaseButton>
					</li>
				</ul>
			</section>
		</template>

		<template v-else>
			<!-- Stacked on narrow screens, so the name keeps the full width -->
			<div class="flex flex-col items-start gap-3 px-4 py-3 rounded-md bg-muted sm:flex-row sm:justify-between sm:gap-4">
				<p class="flex flex-col min-w-0">
					<span class="font-semibold wrap-break-word">
						{{ product.name }}
					</span>

					<span class="text-md text-muted-foreground">
						<template v-if="product.brand">
							{{ product.brand }} –
						</template>

						{{ formatNumber(product.per100.kcal) }} kcal pro 100 {{ product.unit }}
					</span>
				</p>

				<BaseButton
					class="shrink-0"
					variant="outline"
					size="sm"
					@click="clear"
				>
					Ändern<span class="sr-only">
						: anderes Lebensmittel suchen
					</span>
				</BaseButton>
			</div>

			<div class="grid grid-cols-12 gap-4">
				<NumberField
					class="col-span-12 sm:col-span-5"
					name="amount"
					label="Menge"
					:min="0"
					:step="0.1"
				/>

				<SelectField
					class="col-span-12 sm:col-span-7"
					name="unit"
					label="Einheit"
					:options="unitOptions"
				/>
			</div>

			<NutritionFacts
				class="py-4 border-y border-divider"
				:nutrition="nutrition"
				aria-live="polite"
			/>
		</template>
	</div>
</template>
