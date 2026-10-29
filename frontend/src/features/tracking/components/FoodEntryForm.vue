<script setup lang="ts">
import type { SavedMeal } from '@features/meals/meals.types'
import type { FoodEntrySource } from '@features/tracking/tracking.schema'
import type { FoodEntry, FoodProduct, MealType } from '@features/tracking/tracking.types'
import type { FieldOption } from '@shared/forms/types'

import { TabsContent, TabsList, TabsRoot, TabsTrigger } from 'reka-ui'
import { useForm } from 'vee-validate'
import { computed, onMounted, ref } from 'vue'

import FoodProductTab from '@features/tracking/components/FoodProductTab.vue'
import SavedMealTab from '@features/tracking/components/SavedMealTab.vue'
import { BaseActions, BaseButton } from '@shared/ui'

import { listMeals } from '@features/meals/meals.api'
import { addProductEntry, addSavedMealEntry } from '@features/tracking/tracking.api'
import { MEAL_LABELS, MEAL_ORDER } from '@features/tracking/tracking.constants'
import { foodEntrySchema } from '@features/tracking/tracking.schema'
import { DateField, focusFirstError, SelectField } from '@shared/forms'
import { toIsoDate } from '@shared/utils/date'

interface Props {
	/** Prefill; defaults to today and the meal matching the time of day */
	date?: string
	meal?: MealType
	/** Saved meal, e.g. from its own page. The dialog then starts on the "Mahlzeiten" tab. */
	savedMealId?: string
}

const props = withDefaults(defineProps<Props>(), {
	date: undefined,
	meal: undefined,
	savedMealId: undefined,
})

const emit = defineEmits<{
	saved: [entry: FoodEntry]
	cancel: []
}>()

const MEAL_OPTIONS: FieldOption[] = MEAL_ORDER.map((meal) => ({
	value: meal,
	label: MEAL_LABELS[meal],
}))

const TABS: { value: FoodEntrySource; label: string }[] = [
	{ value: 'product', label: 'Lebensmittel' },
	{ value: 'saved', label: 'Mahlzeiten' },
]

/** Preselection by time of day; most people log right after eating */
function mealOfNow(): MealType {
	const hour = new Date().getHours()

	if (hour < 11) return 'breakfast'
	if (hour < 15) return 'lunch'
	if (hour >= 17 && hour < 22) return 'dinner'

	return 'snack'
}

const today = toIsoDate()

// One form for all tabs. keepValuesOnUnmount: switching tabs keeps the inputs. Only what
// belongs to the active tab is saved.
const { handleSubmit, isSubmitting, values, setFieldValue } = useForm({
	validationSchema: foodEntrySchema,
	initialValues: {
		date: props.date ?? today,
		meal: props.meal ?? mealOfNow(),
		source: (props.savedMealId ? 'saved' : 'product') as FoodEntrySource,
		savedMealId: props.savedMealId,
	},
	keepValuesOnUnmount: true,
})

const source = computed<FoodEntrySource>({
	get: () => values.source ?? 'product',
	set: (value) => setFieldValue('source', value, false),
})

const product = ref<FoodProduct | null>(null)
const savedMeals = ref<SavedMeal[]>([])

onMounted(async () => {
	try {
		savedMeals.value = await listMeals()
	} catch {
		// Without meals the tab stays empty; foods can still be logged
	}
})

type FormValues = Parameters<Parameters<typeof handleSubmit>[0]>[0]

/** Saves what belongs to the active tab. The backend calculates the nutrition values. */
function saveEntry(formValues: FormValues): Promise<FoodEntry> {
	const target = { date: formValues.date, meal: formValues.meal }

	if (formValues.source === 'product') {
		return addProductEntry({
			...target,
			product: product.value!,
			amount: formValues.amount!,
			unit: formValues.unit!,
		})
	}

	return addSavedMealEntry({ ...target, mealId: formValues.savedMealId! })
}

const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async (formValues) => {
		submitError.value = null

		try {
			emit('saved', await saveEntry(formValues))
		} catch {
			submitError.value =
				'Der Eintrag konnte nicht gespeichert werden. Versuch es bitte noch einmal.'
		}
	},
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<form
		class="flex flex-col gap-7"
		novalidate
		@submit="onSubmit"
	>
		<div class="flex flex-col gap-5">
			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<!-- Where the entry belongs, often prefilled, e.g. via "Hinzufügen" on breakfast.
             Stacked on phones, where two columns would cut off the values. -->
			<div class="grid grid-cols-12 gap-4">
				<SelectField
					class="col-span-12 sm:col-span-6"
					name="meal"
					label="Mahlzeit"
					:options="MEAL_OPTIONS"
				/>

				<DateField
					class="col-span-12 sm:col-span-6"
					name="date"
					label="Datum"
					:max="today"
				/>
			</div>

			<TabsRoot
				v-model="source"
				class="flex flex-col gap-5"
			>
				<TabsList
					class="tabs tabs--fill"
					aria-label="Eintragen aus"
				>
					<TabsTrigger
						v-for="tab in TABS"
						:key="tab.value"
						class="tabs__item"
						:value="tab.value"
					>
						{{ tab.label }}
					</TabsTrigger>
				</TabsList>

				<TabsContent
					value="product"
					class="tabs__panel"
				>
					<FoodProductTab v-model:product="product" />
				</TabsContent>

				<TabsContent
					value="saved"
					class="tabs__panel"
				>
					<SavedMealTab :meals="savedMeals" />
				</TabsContent>
			</TabsRoot>
		</div>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
				>Eintragen</BaseButton
			>

			<BaseButton
				variant="outline"
				@click="emit('cancel')"
				>Abbrechen</BaseButton
			>
		</BaseActions>
	</form>
</template>
