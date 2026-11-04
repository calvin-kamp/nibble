<script setup lang="ts">
import type { MealItemDraft } from '@features/meals/meals.types'
import type { FoodUnit } from '@features/tracking/tracking.types'
import type { FieldOption } from '@shared/forms/types'

import { TrashIcon } from '@lucide/vue'
import { useFieldValue, useSetFieldValue } from 'vee-validate'
import { computed, useId, watch } from 'vue'

import NutritionFacts from '@features/tracking/components/NutritionFacts.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { draftNutrition } from '@features/meals/meals.utils'
import { formatUnitOption, unitsOf } from '@features/tracking/tracking.utils'
import { NumberField, SelectField } from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

interface Props {
	index: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
	remove: []
}>()

const path = (key: keyof MealItemDraft) => `items[${props.index}].${key}`

const item = useFieldValue<MealItemDraft>(() => `items[${props.index}]`)
const unit = useFieldValue<FoodUnit | undefined>(() => path('unit'))
const setAmount = useSetFieldValue<number | undefined>(() => path('amount'))

// A different unit starts with its own suggestion, otherwise 80 g would become 80 servings
watch(unit, (next, previous) => {
	if (next && previous) setAmount(next === 'serving' || next === 'package' ? 1 : 100)
})

const unitOptions = computed<FieldOption[]>(() => {
	const product = item.value?.product

	return product
		? unitsOf(product).map((value) => ({ value, label: formatUnitOption(product, value) }))
		: []
})

const nutrition = computed(() => (item.value ? draftNutrition(item.value) : null))

const titleId = useId()
</script>

<template>
	<li
		v-if="item"
		class="flex flex-col gap-4 pb-6 border-b border-divider"
		role="group"
		:aria-labelledby="titleId"
	>
		<div class="flex items-start justify-between gap-4">
			<p class="flex flex-col min-w-0">
				<span
					:id="titleId"
					class="text-md font-bold"
				>
					{{ item.product.name }}
				</span>

				<span class="text-md text-muted-foreground tabular-nums">
					<template v-if="item.product.brand">
						{{ item.product.brand }} –
					</template>

					{{ formatNumber(item.product.per100.kcal) }} kcal pro 100

					{{ item.product.unit }}
				</span>
			</p>

			<BaseButton
				class="shrink-0"
				variant="danger-soft"
				size="icon"
				:aria-label="`${item.product.name} entfernen`"
				@click="emit('remove')"
			>
				<BaseIcon :icon="TrashIcon" />
			</BaseButton>
		</div>

		<div class="grid grid-cols-12 gap-3 md:flex md:items-start">
			<NumberField
				class="col-span-12 md:w-36"
				:name="path('amount')"
				label="Menge"
				:min="0"
				:step="0.1"
			/>

			<SelectField
				class="col-span-12 md:w-64"
				:name="path('unit')"
				label="Einheit"
				:options="unitOptions"
			/>
		</div>

		<NutritionFacts
			:nutrition="nutrition"
			aria-live="polite"
		/>
	</li>
</template>
