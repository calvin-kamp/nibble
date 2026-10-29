<script setup lang="ts">
import type { MealFormValues, MealItemDraft } from '@features/meals/meals.types'
import type { FoodProduct, Nutrition } from '@features/tracking/tracking.types'

import { useFieldArray, useForm } from 'vee-validate'
import { computed, nextTick, ref } from 'vue'

import MealItemRow from '@features/meals/components/MealItemRow.vue'
import FoodSearchField from '@features/tracking/components/FoodSearchField.vue'
import NutritionCard from '@features/tracking/components/NutritionCard.vue'
import { BaseActions, BaseButton, BaseCard } from '@shared/ui'

import { mealSchema } from '@features/meals/meals.schema'
import { draftNutrition, sumNutrition } from '@features/meals/meals.utils'
import { focusFirstError, TextareaField, TextField } from '@shared/forms'

interface Props {
	initialValues?: MealFormValues
	submitLabel: string
	submitting?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	initialValues: () => ({ name: '', items: [] }),
	submitting: false,
})

const emit = defineEmits<{
	submit: [values: MealFormValues]
	cancel: []
}>()

const { handleSubmit, meta, errors, values, submitCount } = useForm({
	validationSchema: mealSchema,
	initialValues: props.initialValues,
})

const items = useFieldArray<MealItemDraft>('items')

// A new food moves focus to "Menge"; after removing one, focus returns to the search
const list = ref<HTMLElement | null>(null)
const addSection = ref<HTMLElement | null>(null)

async function focusLastItem(): Promise<void> {
	await nextTick()
	list.value?.lastElementChild?.querySelector<HTMLElement>('input')?.focus()
}

/** Suggestion: one serving if known, otherwise 100 g or ml */
function addProduct(product: FoodProduct): void {
	const unit = product.serving ? 'serving' : product.unit

	items.push({ product, unit, amount: unit === 'serving' ? 1 : 100 })
	focusLastItem()
}

async function removeItem(index: number): Promise<void> {
	items.remove(index)

	await nextTick()
	addSection.value?.querySelector<HTMLElement>('input')?.focus()
}

// Sum of all items that already have an amount
const total = computed<Nutrition>(() =>
	sumNutrition(
		(values.items ?? []).map(draftNutrition).filter((nutrition) => nutrition !== null),
	),
)

// Without items, the error is attached to the search, where the first item is added
const itemsError = computed<string | undefined>(() =>
	submitCount.value ? errors.value.items : undefined,
)

const onSubmit = handleSubmit(
	(formValues) => emit('submit', formValues as MealFormValues),
	({ evt }) => focusFirstError(evt),
)

defineExpose({ isDirty: computed<boolean>(() => meta.value.dirty) })
</script>

<template>
	<!-- Same structure as the recipe form. max-w-4xl: on wide screens the rows would otherwise be
       too long to fill in. -->
	<BaseCard
		as="form"
		size="lg"
		class="w-full max-w-4xl"
		novalidate
		@submit="onSubmit"
	>
		<div class="flex flex-col gap-8">
			<section
				class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
				aria-labelledby="meal-form-basics-title"
			>
				<h2
					id="meal-form-basics-title"
					class="text-2xl"
				>
					Grunddaten
				</h2>

				<TextField
					name="name"
					label="Name"
					autocomplete="off"
				/>

				<TextareaField
					name="note"
					label="Notiz (optional)"
					hint="Z. B. wie du sie zubereitest. Steht auf der Seite der Mahlzeit."
					:rows="2"
				/>
			</section>

			<section
				class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
				aria-labelledby="meal-form-items-title"
			>
				<div class="flex flex-col gap-2">
					<h2
						id="meal-form-items-title"
						class="text-2xl"
					>
						Lebensmittel
					</h2>

					<p class="text-muted">
						Was gehört dazu und wie viel davon? Die Nährwerte rechnen wir zusammen.
					</p>
				</div>

				<ul
					v-if="items.fields.value.length"
					ref="list"
					class="flex flex-col gap-6"
				>
					<MealItemRow
						v-for="(field, index) in items.fields.value"
						:key="field.key"
						:index="index"
						@remove="removeItem(index)"
					/>
				</ul>

				<div ref="addSection">
					<FoodSearchField
						label="Lebensmittel hinzufügen"
						:error="itemsError"
						@select="addProduct"
					/>
				</div>
			</section>

			<!-- Meal total, in the same card as on the recipe and meal pages. aria-live: announced after
             every change. -->
			<div class="flex flex-col gap-3 pt-8 border-t border-divider">
				<NutritionCard
					title="Nährwerte der Mahlzeit"
					:nutrition="total"
					aria-live="polite"
				/>

				<p class="text-muted">Die Summe aller Lebensmittel. So landet sie im Tagebuch.</p>
			</div>

			<BaseActions class="pt-8 border-t border-divider">
				<BaseButton
					type="submit"
					:disabled="props.submitting"
					>{{ props.submitLabel }}</BaseButton
				>

				<BaseButton
					variant="ghost"
					@click="emit('cancel')"
					>Abbrechen</BaseButton
				>
			</BaseActions>
		</div>
	</BaseCard>
</template>
