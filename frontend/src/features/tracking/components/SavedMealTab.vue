<script setup lang="ts">
import type { SavedMeal } from '@features/meals/meals.types'
import type { FieldOption } from '@shared/forms/types'

import { BookmarkIcon } from '@lucide/vue'
import { computed } from 'vue'

import { BaseButton, BaseEmptyState } from '@shared/ui'

import { formatMacrosShort } from '@features/tracking/tracking.utils'
import { RadioField } from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

// "Mahlzeiten" tab in the food dialog: pick a saved meal and log it with one click. Runs
// inside FoodEntryForm's form.
interface Props {
	meals: SavedMeal[]
}

const props = defineProps<Props>()

const options = computed<FieldOption[]>(() =>
	props.meals.map((meal) => ({
		value: meal.id,
		label: meal.name,
		description: `${formatNumber(meal.kcal)} kcal · ${formatMacrosShort(meal)}`,
	})),
)
</script>

<template>
	<RadioField
		v-if="props.meals.length"
		name="savedMealId"
		label="Gespeicherte Mahlzeit"
		label-hidden
		:options="options"
	/>

	<BaseEmptyState
		v-else
		size="sm"
		:icon="BookmarkIcon"
		title="Noch keine Mahlzeiten gespeichert"
	>
		Stell zusammen, was du oft isst. Danach trägst du alles mit einem Klick ein.

		<template #actions>
			<BaseButton
				variant="outline"
				size="sm"
				route-name="meal-create"
			>
				Mahlzeit anlegen
			</BaseButton>
		</template>
	</BaseEmptyState>
</template>
