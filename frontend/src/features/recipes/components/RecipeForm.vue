<script setup lang="ts">
import type {
	IngredientDraft,
	RecipeFormSection,
	RecipeFormValues,
} from '@features/recipes/recipes.types'
import type { RouteLocationRaw } from 'vue-router'

import {
	ArrowDownIcon,
	ArrowLeftIcon,
	ArrowRightIcon,
	ArrowUpIcon,
	PlusIcon,
	TrashIcon,
} from '@lucide/vue'
import { useId } from 'reka-ui'
import { useFieldArray, useForm } from 'vee-validate'
import { computed, nextTick, ref, watch } from 'vue'

import { BaseActions, BaseButton, BaseCard, BaseIcon, BaseStepProgress } from '@shared/ui'

import { useBreakpoint } from '@shared/composables/breakpoint'
import { useFormSteps } from '@shared/composables/form-steps'

import {
	DIET_LABELS,
	EQUIPMENT_LABELS,
	INGREDIENT_UNIT_LABELS,
	INGREDIENT_UNITS,
	INTOLERANCE_LABELS,
	MAX_SERVINGS,
	MEAL_TYPE_LABELS,
	MIN_SERVINGS,
	RECIPE_FORM_SECTIONS,
} from '@features/recipes/recipes.constants'
import { NO_NUTRIENTS_MESSAGE, recipeSchema } from '@features/recipes/recipes.schema'
import { emptyIngredient, kcalOf } from '@features/recipes/recipes.utils'
import {
	CheckboxGroupField,
	focusFirstError,
	ImageField,
	NumberField,
	SelectField,
	TextareaField,
	TextField,
} from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

interface Props {
	initialValues?: Partial<RecipeFormValues>
	submitLabel: string
	submitting?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	initialValues: () => ({}),
	submitting: false,
})

const emit = defineEmits<{
	submit: [values: RecipeFormValues]
	/** "Abbrechen": where it leads and whether to confirm is decided by the page */
	cancel: []
}>()

const DIET_OPTIONS = [
	{ value: 'omnivore', label: 'Keine Angabe' },
	...(['pescetarian', 'vegetarian', 'vegan'] as const).map((diet) => ({
		value: diet,
		label: DIET_LABELS[diet]!,
	})),
]

const INTOLERANCE_OPTIONS = Object.entries(INTOLERANCE_LABELS).map(([value, label]) => ({
	value,
	label,
}))
const EQUIPMENT_OPTIONS = Object.entries(EQUIPMENT_LABELS).map(([value, label]) => ({
	value,
	label,
}))
const MEAL_TYPE_OPTIONS = Object.entries(MEAL_TYPE_LABELS).map(([value, label]) => ({
	value,
	label,
}))
const UNIT_OPTIONS = INGREDIENT_UNITS.map((unit) => ({
	value: unit,
	label: INGREDIENT_UNIT_LABELS[unit],
}))

// keepValuesOnUnmount: on phones the other sections are hidden, but their values still have
// to stay in the form
const { handleSubmit, validateField, setFieldError, values, errors, meta } = useForm({
	validationSchema: recipeSchema,
	initialValues: {
		description: '',
		image: null,
		servings: 2,
		diet: 'omnivore',
		freeFrom: [],
		equipment: [],
		mealTypes: [],
		ingredients: [emptyIngredient(), emptyIngredient()],
		steps: ['', '', ''],
		...props.initialValues,
	},
	keepValuesOnUnmount: true,
})

const ingredients = useFieldArray<IngredientDraft>('ingredients')
const steps = useFieldArray<string>('steps')

// The calorie error is not attached to an input but to the "kcal" path
const kcalError = computed<string | undefined>(
	() => (errors.value as Record<string, string | undefined>).kcal,
)

const kcal = computed<number>(() =>
	kcalOf({ protein: values.protein ?? 0, carbs: values.carbs ?? 0, fat: values.fat ?? 0 }),
)

watch(kcal, (value) => {
	if (value >= 1 && kcalError.value) setFieldError('kcal' as never, undefined)
})

// One section per step on phones, all sections stacked from tablet up
const { isTablet } = useBreakpoint()

const isStepped = computed<boolean>(() => !isTablet.value)

// The step lives in the address, so the phone's back gesture goes to the previous one.
// On change, the new section's heading receives focus.
const headings = ref<Partial<Record<RecipeFormSection, HTMLElement>>>({})

const formSteps = useFormSteps({
	keys: RECIPE_FORM_SECTIONS.map((_, index) => String(index + 1)),
	enabled: isStepped,
	onChange: (index) => headings.value[RECIPE_FORM_SECTIONS[index]!]?.focus(),
})

const part = formSteps.index

const isLastPart = computed<boolean>(() => !isStepped.value || formSteps.isLast.value)

function isVisible(section: RecipeFormSection): boolean {
	return !isStepped.value || RECIPE_FORM_SECTIONS[part.value] === section
}

/** After saving, go to the target page without Back landing in the form again */
function finish(to: RouteLocationRaw): Promise<void> {
	return formSteps.finish(to)
}

/** Whether anything changed since opening, e.g. to confirm before cancelling */
const isDirty = computed<boolean>(() => meta.value.dirty)

defineExpose({ finish, isDirty })

function fieldsOf(section: RecipeFormSection): string[] {
	if (section === 'basics')
		return ['title', 'description', 'image', 'servings', 'durationMinutes']
	if (section === 'nutrition') return ['protein', 'carbs', 'fat', 'kcal']
	if (section === 'properties') return ['mealTypes', 'diet', 'freeFrom', 'equipment']

	if (section === 'ingredients') {
		const rowFields = ingredients.fields.value.flatMap((_, index) =>
			['name', 'amount', 'unit'].map((key) => `ingredients[${index}].${key}`),
		)

		return [...rowFields, 'ingredients']
	}

	return [...steps.fields.value.map((_, index) => `steps[${index}]`), 'steps']
}

function sectionOf(path: string): RecipeFormSection {
	return RECIPE_FORM_SECTIONS.find((section) =>
		fieldsOf(section).some((field) => path === field || path.startsWith(`${field}[`)),
	)!
}

// New rows receive focus; after removing one, the add button receives it
const ingredientList = ref<HTMLElement | null>(null)
const stepList = ref<HTMLElement | null>(null)
const addIngredientButton = ref<InstanceType<typeof BaseButton> | null>(null)
const addStepButton = ref<InstanceType<typeof BaseButton> | null>(null)

async function focusLastRow(list: HTMLElement | null): Promise<void> {
	await nextTick()
	list?.lastElementChild?.querySelector<HTMLElement>('input, textarea')?.focus()
}

function focusButton(button: InstanceType<typeof BaseButton> | null): void {
	const element = button?.$el as HTMLElement | undefined

	element?.focus()
}

function addIngredient(): void {
	ingredients.push(emptyIngredient())
	focusLastRow(ingredientList.value)
}

// The last row is cleared instead of removed, so there is always one
function removeIngredient(index: number): void {
	ingredients.remove(index)

	if (!ingredients.fields.value.length) ingredients.push(emptyIngredient())

	focusButton(addIngredientButton.value)
}

function addStep(): void {
	steps.push('')
	focusLastRow(stepList.value)
}

function removeStep(index: number): void {
	steps.remove(index)

	if (!steps.fields.value.length) steps.push('')

	focusButton(addStepButton.value)
}

const stepIdBase = useId(undefined, 'recipe-step')

// Focus moves with the moved step. Once it reaches the top or bottom, the button in that
// direction is disabled, so the other button receives focus.
async function moveStep(index: number, direction: -1 | 1): Promise<void> {
	const target = index + direction

	steps.swap(index, target)

	await nextTick()

	const lastIndex = steps.fields.value.length - 1
	const focusDirection =
		direction === -1 ? (target === 0 ? 'down' : 'up') : target === lastIndex ? 'up' : 'down'

	document.getElementById(`${stepIdBase}-${target}-${focusDirection}`)?.focus()
}

/** Empty ingredients and steps are dropped on save */
function clean(formValues: RecipeFormValues): RecipeFormValues {
	return {
		...formValues,
		ingredients: formValues.ingredients.filter((ingredient) => ingredient.name.trim()),
		steps: formValues.steps.map((step) => step.trim()).filter(Boolean),
	}
}

const submitAll = handleSubmit(
	(formValues) => emit('submit', clean(formValues)),
	async ({ errors: invalid, evt }) => {
		const firstPath = Object.keys(invalid)[0]

		// If the error is in another section, go back there
		if (isStepped.value && firstPath) {
			await formSteps.goTo(RECIPE_FORM_SECTIONS.indexOf(sectionOf(firstPath)), {
				focus: false,
			})
		}

		focusFirstError(evt)
	},
)

// vee-validate already validates the lists silently on load. Only show their messages
// ("mindestens eine Zutat") once someone tried to continue or save.
const attempted = ref<boolean>(false)

async function onSubmit(event: Event): Promise<void> {
	attempted.value = true
	if (isLastPart.value) return submitAll(event)

	event.preventDefault()

	const section = RECIPE_FORM_SECTIONS[part.value]!
	const fields = fieldsOf(section).filter((field) => field !== 'kcal')
	const results = await Promise.all(fields.map((field) => validateField(field as never)))
	let valid = results.every((result) => result.valid)

	// The calorie rule spans several fields and would otherwise only run on save
	if (valid && section === 'nutrition' && kcal.value < 1) {
		setFieldError('kcal' as never, NO_NUTRIENTS_MESSAGE)
		valid = false
	}

	if (valid) formSteps.next()
	else focusFirstError(event)
}
</script>

<template>
	<!-- max-w-4xl: on wide screens the rows would otherwise be too long to fill in -->
	<BaseCard
		as="form"
		size="lg"
		class="w-full max-w-4xl"
		novalidate
		@submit="onSubmit"
	>
		<div class="flex flex-col gap-6">
			<BaseStepProgress
				v-if="isStepped"
				:current="part + 1"
				:total="RECIPE_FORM_SECTIONS.length"
			/>

			<div class="flex flex-col gap-8">
				<section
					v-if="isVisible('basics')"
					class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="recipe-form-basics-title"
				>
					<h2
						id="recipe-form-basics-title"
						:ref="(el) => (headings.basics = el as HTMLElement)"
						class="text-2xl outline-none"
						tabindex="-1"
					>
						Grunddaten
					</h2>

					<!-- The photo first: it is the first thing others see of the recipe -->
					<ImageField
						name="image"
						label="Foto (optional)"
						hint="Am besten im Querformat, als JPG, PNG oder WebP bis 5 MB."
					/>

					<TextField
						name="title"
						label="Titel"
						autocomplete="off"
					/>

					<TextareaField
						name="description"
						label="Kurzbeschreibung"
						hint="Ein bis zwei Sätze, die Lust aufs Kochen machen."
						:rows="3"
					/>

					<div class="grid grid-cols-12 gap-5">
						<NumberField
							class="col-span-12 md:col-span-6"
							name="servings"
							label="Portionen"
							hint="Für so viele Portionen gelten die Zutaten."
							stepper
							:min="MIN_SERVINGS"
							:max="MAX_SERVINGS"
							increment-label="Eine Portion mehr"
							decrement-label="Eine Portion weniger"
							:format-options="{ maximumFractionDigits: 0 }"
						/>

						<NumberField
							class="col-span-12 md:col-span-6"
							name="durationMinutes"
							label="Zubereitungszeit"
							hint="Vom ersten Schnippeln bis auf den Teller."
							unit="Minuten"
							:min="0"
							:format-options="{ maximumFractionDigits: 0 }"
						/>
					</div>
				</section>

				<section
					v-if="isVisible('nutrition')"
					class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="recipe-form-nutrition-title"
				>
					<div class="flex flex-col gap-2">
						<h2
							id="recipe-form-nutrition-title"
							:ref="(el) => (headings.nutrition = el as HTMLElement)"
							class="text-2xl outline-none"
							tabindex="-1"
						>
							Nährwerte pro Portion
						</h2>

						<p class="text-muted">
							Die Kalorien rechnen wir aus: Protein und Kohlenhydrate haben 4 kcal pro
							Gramm, Fett 9 kcal pro Gramm. Trag 0 ein, wenn ein Wert nicht vorkommt.
						</p>
					</div>

					<!-- Not an input: calories are derived from the macros. output announces the new value. -->
					<div class="flex flex-col gap-2">
						<p class="flex flex-wrap items-baseline gap-x-2">
							<output
								aria-label="Kalorien pro Portion"
								class="font-display text-5xl font-extrabold tracking-tighter tabular-nums"
							>
								{{ kcal ? formatNumber(kcal) : '–' }}
							</output>

							<span class="font-semibold text-ink-soft">kcal pro Portion</span>
						</p>

						<p
							v-if="kcalError"
							class="text-sm font-semibold text-danger"
							role="alert"
						>
							{{ kcalError }}
						</p>
					</div>

					<div class="grid grid-cols-12 gap-5">
						<NumberField
							class="col-span-12 sm:col-span-4"
							name="protein"
							label="Protein"
							unit="g"
							:min="0"
						/>

						<NumberField
							class="col-span-12 sm:col-span-4"
							name="carbs"
							label="Kohlenhydrate"
							unit="g"
							:min="0"
						/>

						<NumberField
							class="col-span-12 sm:col-span-4"
							name="fat"
							label="Fett"
							unit="g"
							:min="0"
						/>
					</div>
				</section>

				<section
					v-if="isVisible('properties')"
					class="flex flex-col gap-6 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="recipe-form-properties-title"
				>
					<div class="flex flex-col gap-2">
						<h2
							id="recipe-form-properties-title"
							:ref="(el) => (headings.properties = el as HTMLElement)"
							class="text-2xl outline-none"
							tabindex="-1"
						>
							Eigenschaften
						</h2>

						<p class="text-muted">
							Damit andere dein Rezept über die Filter finden. Nur die Mahlzeit ist
							Pflicht.
						</p>
					</div>

					<CheckboxGroupField
						name="mealTypes"
						label="Passt zu"
						:options="MEAL_TYPE_OPTIONS"
					/>

					<SelectField
						name="diet"
						label="Ernährungsform"
						:options="DIET_OPTIONS"
					/>

					<CheckboxGroupField
						name="freeFrom"
						label="Unverträglichkeiten"
						:options="INTOLERANCE_OPTIONS"
					/>

					<CheckboxGroupField
						name="equipment"
						label="Geräte"
						hint="Nichts ausgewählt heißt: kein Gerät nötig."
						:options="EQUIPMENT_OPTIONS"
					/>
				</section>

				<section
					v-if="isVisible('ingredients')"
					class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="recipe-form-ingredients-title"
				>
					<div class="flex flex-col gap-2">
						<h2
							id="recipe-form-ingredients-title"
							:ref="(el) => (headings.ingredients = el as HTMLElement)"
							class="text-2xl outline-none"
							tabindex="-1"
						>
							Zutaten
						</h2>

						<p class="text-muted">
							Die Mengen gelten für die Portionen aus den Grunddaten. Beim Kochen
							lassen sie sich umrechnen.
						</p>
					</div>

					<ul
						ref="ingredientList"
						class="flex flex-col gap-5"
					>
						<li
							v-for="(ingredient, index) in ingredients.fields.value"
							:key="ingredient.key"
							class="pb-5 border-b border-divider md:pb-0 md:border-b-0"
						>
							<fieldset
								class="grid grid-cols-12 gap-3 min-w-0 md:flex md:items-start"
							>
								<legend class="sr-only">Zutat {{ index + 1 }}</legend>

								<TextField
									class="col-span-12 md:flex-1"
									:name="`ingredients[${index}].name`"
									label="Zutat"
									autocomplete="off"
								/>

								<NumberField
									class="col-span-6 md:w-36"
									:name="`ingredients[${index}].amount`"
									label="Menge"
									:min="0"
									:format-options="{ maximumFractionDigits: 2 }"
								/>

								<SelectField
									class="col-span-6 md:w-36"
									:name="`ingredients[${index}].unit`"
									label="Einheit"
									:options="UNIT_OPTIONS"
								/>

								<!-- From tablet up in the row of fields: an invisible label lines the button up with the inputs -->
								<div class="field col-span-12 items-start">
									<span
										class="field__label invisible max-md:hidden"
										aria-hidden="true"
										>Entfernen</span
									>

									<BaseButton
										class="md:size-12 md:px-0"
										variant="outline"
										:aria-label="`Zutat ${index + 1} entfernen`"
										@click="removeIngredient(index)"
									>
										<BaseIcon :icon="TrashIcon" />

										<span class="md:sr-only">Entfernen</span>
									</BaseButton>
								</div>
							</fieldset>
						</li>
					</ul>

					<p
						v-if="attempted && errors.ingredients"
						class="text-sm font-semibold text-danger"
					>
						{{ errors.ingredients }}
					</p>

					<BaseButton
						ref="addIngredientButton"
						class="self-center"
						variant="outline"
						@click="addIngredient"
					>
						<BaseIcon :icon="PlusIcon" />
						Zutat hinzufügen
					</BaseButton>
				</section>

				<section
					v-if="isVisible('steps')"
					class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="recipe-form-steps-title"
				>
					<h2
						id="recipe-form-steps-title"
						:ref="(el) => (headings.steps = el as HTMLElement)"
						class="text-2xl outline-none"
						tabindex="-1"
					>
						Zubereitung
					</h2>

					<ol
						ref="stepList"
						class="flex flex-col gap-5"
					>
						<!-- The buttons sit in the label row, to the right of "Schritt 1". In the markup they come
                     before the text field so the tab order follows the visual order. -->
						<li
							v-for="(step, index) in steps.fields.value"
							:key="step.key"
							class="relative"
						>
							<div class="absolute z-1 -top-1 right-0 flex gap-2">
								<BaseButton
									:id="`${stepIdBase}-${index}-up`"
									variant="outline"
									size="icon-sm"
									:aria-label="`Schritt ${index + 1} nach oben`"
									:disabled="index === 0"
									@click="moveStep(index, -1)"
								>
									<BaseIcon
										:icon="ArrowUpIcon"
										:size="16"
									/>
								</BaseButton>

								<BaseButton
									:id="`${stepIdBase}-${index}-down`"
									variant="outline"
									size="icon-sm"
									:aria-label="`Schritt ${index + 1} nach unten`"
									:disabled="index === steps.fields.value.length - 1"
									@click="moveStep(index, 1)"
								>
									<BaseIcon
										:icon="ArrowDownIcon"
										:size="16"
									/>
								</BaseButton>

								<BaseButton
									variant="outline"
									size="icon-sm"
									:aria-label="`Schritt ${index + 1} entfernen`"
									@click="removeStep(index)"
								>
									<BaseIcon
										:icon="TrashIcon"
										:size="16"
									/>
								</BaseButton>
							</div>

							<TextareaField
								:name="`steps[${index}]`"
								:label="`Schritt ${index + 1}`"
								:rows="3"
							/>
						</li>
					</ol>

					<p
						v-if="attempted && errors.steps"
						class="text-sm font-semibold text-danger"
					>
						{{ errors.steps }}
					</p>

					<BaseButton
						ref="addStepButton"
						class="self-center"
						variant="outline"
						@click="addStep"
					>
						<BaseIcon :icon="PlusIcon" />
						Schritt hinzufügen
					</BaseButton>
				</section>

				<BaseActions class="pt-8 border-t border-divider">
					<BaseButton
						type="submit"
						:disabled="props.submitting"
					>
						<template v-if="isLastPart">{{ props.submitLabel }}</template>

						<template v-else>
							Weiter
							<BaseIcon :icon="ArrowRightIcon" />
						</template>
					</BaseButton>

					<BaseButton
						v-if="isStepped && part > 0"
						variant="outline"
						@click="formSteps.back()"
					>
						<BaseIcon :icon="ArrowLeftIcon" />
						Zurück
					</BaseButton>

					<BaseButton
						v-else
						variant="ghost"
						@click="emit('cancel')"
						>Abbrechen</BaseButton
					>
				</BaseActions>
			</div>
		</div>
	</BaseCard>
</template>
