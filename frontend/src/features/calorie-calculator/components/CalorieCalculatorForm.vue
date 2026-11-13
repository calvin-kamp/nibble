<script setup lang="ts">
import type {
	CalculatorSection,
	CalorieCalculatorValues,
	Workout,
} from '@features/calorie-calculator/calorie-calculator.types'

import { ArrowLeftIcon, ArrowRightIcon, DumbbellIcon, PlusIcon, TrashIcon } from '@lucide/vue'
import { useFieldArray, useForm } from 'vee-validate'
import { computed, nextTick, ref, watch } from 'vue'

import { BaseActions, BaseButton, BaseCard, BaseEmptyState, BaseIcon } from '@shared/ui'

import {
	CALCULATOR_SECTIONS,
	EMPTY_WORKOUT,
	GOAL_OPTIONS,
	SEX_OPTIONS,
} from '@features/calorie-calculator/calorie-calculator.constants'
import { calorieCalculatorSchema } from '@features/calorie-calculator/calorie-calculator.schema'
import { TRAINING_SELECT_GROUPS } from '@features/calorie-calculator/calorie-calculator.utils'
import { focusFirstError, NumberField, RadioField, SelectField } from '@shared/forms'

interface Props {
	initialValues?: Partial<CalorieCalculatorValues>
	/**
	 * Sections this form asks for. Left out sections must already be valid in initialValues,
	 * e.g. when onboarding has asked for them before.
	 */
	sections?: readonly CalculatorSection[]
	/**
	 * Show only one section (index in sections), e.g. step by step on phones.
	 * Without part, all sections are shown in one form.
	 */
	part?: number
}

const props = withDefaults(defineProps<Props>(), {
	initialValues: () => ({}),
	sections: () => CALCULATOR_SECTIONS,
	part: undefined,
})

const emit = defineEmits<{
	calculate: [values: CalorieCalculatorValues]
	reset: []
	'part-complete': [values: Partial<CalorieCalculatorValues>]
	back: []
	'go-to-part': [part: number]
}>()

// "Gewicht halten" preselected: anyone who does not choose deliberately gets no deficit
// keepValuesOnUnmount: when going section by section, the other fields are hidden, but their
// values still have to stay in the form
const { handleSubmit, resetForm, validateField, errors, values } = useForm({
	validationSchema: calorieCalculatorSchema,
	initialValues: { steps: 6000, goal: 'maintain', exercises: [], ...props.initialValues },
	keepValuesOnUnmount: true,
})

const { fields: workouts, push, remove } = useFieldArray<Workout>('exercises')

const visibleSections = computed<readonly CalculatorSection[]>(() =>
	props.part === undefined ? props.sections : [props.sections[props.part]!],
)

const isLastPart = computed<boolean>(
	() => props.part === undefined || props.part === props.sections.length - 1,
)

function isVisible(section: CalculatorSection): boolean {
	return visibleSections.value.includes(section)
}

// Errors of left out sections, e.g. the safety rules on a goal chosen earlier in onboarding
const hiddenErrors = computed<string[]>(() =>
	CALCULATOR_SECTIONS.filter((section) => !props.sections.includes(section)).flatMap(
		(section) =>
			fieldsOf(section)
				.map((field) => errors.value[field as keyof typeof errors.value])
				.filter((message): message is string => !!message),
	),
)

function fieldsOf(section: CalculatorSection): string[] {
	if (section === 'basal') return ['sex', 'age', 'height', 'weight']
	if (section === 'steps') return ['steps']
	if (section === 'goal') return ['goal']

	const workoutFields = workouts.value.flatMap((_, index) =>
		['met', 'duration', 'frequency'].map((key) => `exercises[${index}].${key}`),
	)

	return [...workoutFields, 'exercises']
}

function sectionOf(path: string): CalculatorSection {
	return CALCULATOR_SECTIONS.find((section) =>
		fieldsOf(section).some((field) => path === field || path.startsWith(`${field}[`)),
	)!
}

const headings = ref<Partial<Record<CalculatorSection, HTMLElement>>>({})
const form = ref<InstanceType<typeof BaseCard> | null>(null)
let focusErrorAfterSwitch = false

watch(
	() => props.part,
	async (part) => {
		if (part === undefined) return

		await nextTick()

		if (focusErrorAfterSwitch) {
			const element = form.value?.$el as HTMLElement | undefined

			element?.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus()
			focusErrorAfterSwitch = false
		} else {
			headings.value[props.sections[part]!]?.focus()
		}
	},
)

function focusHeading(): void {
	headings.value[props.sections[props.part ?? 0]!]?.focus()
}

defineExpose({ focusHeading })

function addWorkout(): void {
	push({ ...EMPTY_WORKOUT })
}

const submitAll = handleSubmit(
	(calculated) => emit('calculate', calculated),
	({ errors: invalid, evt }) => {
		const firstPath = Object.keys(invalid)[0]
		const section = firstPath ? sectionOf(firstPath) : undefined

		if (props.part !== undefined && section && props.sections.includes(section) && !isVisible(section)) {
			focusErrorAfterSwitch = true
			emit('go-to-part', props.sections.indexOf(section))
			return
		}

		focusFirstError(evt)
	},
)

async function onSubmit(event: Event): Promise<void> {
	if (isLastPart.value) return submitAll(event)

	event.preventDefault()

	const section = props.sections[props.part!]!
	const results = await Promise.all(
		fieldsOf(section).map((field) => validateField(field as never)),
	)

	if (results.every((result) => result.valid)) {
		emit('part-complete', { ...values } as Partial<CalorieCalculatorValues>)
	} else {
		focusFirstError(event)
	}
}

function onReset(): void {
	resetForm()
	emit('reset')
}
</script>

<template>
	<BaseCard
		ref="form"
		as="form"
		size="lg"
		novalidate
		@submit="onSubmit"
	>
		<div class="flex flex-col gap-6">
			<slot name="header" />

			<div class="flex flex-col gap-8">
				<section
					v-if="isVisible('basal')"
					class="grid grid-cols-12 gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="calculator-bmr-title"
				>
					<div class="flex flex-col gap-2 col-span-12">
						<h2
							id="calculator-bmr-title"
							:ref="(el) => (headings.basal = el as HTMLElement)"
							class="outline-none wrap-break-word hyphens-auto"
							tabindex="-1"
						>
							Grundumsatz
						</h2>

						<p class="text-muted-foreground">
							Diese vier Angaben bestimmen, was dein Körper in Ruhe verbraucht.
						</p>
					</div>

					<RadioField
						class="col-span-12"
						name="sex"
						label="Geschlecht"
						orientation="horizontal"
						:options="SEX_OPTIONS"
					/>

					<NumberField
						class="col-span-12 md:col-span-4"
						name="age"
						label="Alter"
						unit="Jahre"
						:format-options="{ maximumFractionDigits: 0 }"
					/>

					<NumberField
						class="col-span-12 md:col-span-4"
						name="height"
						label="Größe"
						unit="cm"
						:format-options="{ maximumFractionDigits: 0 }"
					/>

					<NumberField
						class="col-span-12 md:col-span-4"
						name="weight"
						label="Gewicht"
						unit="kg"
						:step="0.1"
						:format-options="{ maximumFractionDigits: 1 }"
					/>
				</section>

				<section
					v-if="isVisible('steps')"
					class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="calculator-steps-title"
				>
					<h2
						id="calculator-steps-title"
						:ref="(el) => (headings.steps = el as HTMLElement)"
						class="outline-none wrap-break-word hyphens-auto"
						tabindex="-1"
					>
						Alltagsbewegung
					</h2>

					<NumberField
						name="steps"
						label="Schritte pro Tag"
						hint="Dein Handy zählt schon mit, schau in der Health-App nach deinem Tagesdurchschnitt. Zum Schätzen: rund 4.000 bei überwiegend sitzendem Alltag, rund 7.000 bei gemischtem, rund 10.000, wenn du viel auf den Beinen bist."
						stepper
						:min="0"
						:step="100"
						increment-label="100 Schritte mehr"
						decrement-label="100 Schritte weniger"
						:format-options="{ maximumFractionDigits: 0 }"
					/>
				</section>

				<section
					v-if="isVisible('training')"
					class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="calculator-training-title"
				>
					<div class="flex flex-col gap-2">
						<h2
							id="calculator-training-title"
							:ref="(el) => (headings.training = el as HTMLElement)"
							class="outline-none wrap-break-word hyphens-auto"
							tabindex="-1"
						>
							Training
						</h2>

						<p class="text-muted-foreground">
							Optional und nur für gezielten Sport: Spaziergänge und Wege stecken
							schon in deinen Schritten. Hat dein Handy beim Laufen oder Wandern
							mitgezählt, trag die Einheit nicht zusätzlich ein.
						</p>
					</div>

					<BaseEmptyState
						v-if="!workouts.length"
						size="sm"
						:icon="DumbbellIcon"
						title="Kein Training eingetragen"
					>
						Wir rechnen dann nur mit Grundumsatz und Alltagsbewegung.

						<template #actions>
							<BaseButton
								variant="outline"
								@click="addWorkout"
							>
								<BaseIcon :icon="PlusIcon" />

								Training hinzufügen
							</BaseButton>
						</template>
					</BaseEmptyState>

					<template v-else>
						<ul class="flex flex-col gap-4">
							<li
								v-for="(workout, index) in workouts"
								:key="workout.key"
							>
								<div
									class="repeat-group"
									role="group"
									:aria-labelledby="`workout-${workout.key}-title`"
								>
									<div class="repeat-group__header">
										<h3
											:id="`workout-${workout.key}-title`"
											class="repeat-group__title font-sans text-md tracking-normal"
										>
											Training {{ index + 1 }}
										</h3>

										<BaseButton
											variant="danger-soft"
											size="icon-sm"
											:aria-label="`Training ${index + 1} entfernen`"
											@click="remove(index)"
										>
											<BaseIcon
												:icon="TrashIcon"
												:size="16"
											/>
										</BaseButton>
									</div>

									<div class="grid grid-cols-12 gap-4">
										<SelectField
											class="col-span-12"
											:name="`exercises[${index}].met`"
											label="Sportart"
											placeholder="Sportart auswählen"
											:groups="TRAINING_SELECT_GROUPS"
										/>

										<NumberField
											class="col-span-12 md:col-span-6"
											:name="`exercises[${index}].duration`"
											label="Dauer pro Einheit"
											unit="Minuten"
											:min="0"
											:format-options="{ maximumFractionDigits: 0 }"
										/>

										<NumberField
											class="col-span-12 md:col-span-6"
											:name="`exercises[${index}].frequency`"
											label="Einheiten pro Woche"
											unit="pro Woche"
											:min="0"
											:format-options="{ maximumFractionDigits: 0 }"
										/>
									</div>
								</div>
							</li>
						</ul>

						<p
							v-if="errors.exercises"
							class="text-md font-semibold text-destructive"
						>
							{{ errors.exercises }}
						</p>

						<BaseButton
							class="self-center"
							variant="outline"
							@click="addWorkout"
						>
							<BaseIcon :icon="PlusIcon" />

							Weiteres Training hinzufügen
						</BaseButton>
					</template>
				</section>

				<section
					v-if="isVisible('goal')"
					class="flex flex-col gap-5 pt-8 border-t border-divider first-of-type:pt-0 first-of-type:border-t-0"
					aria-labelledby="calculator-goal-title"
				>
					<h2
						id="calculator-goal-title"
						:ref="(el) => (headings.goal = el as HTMLElement)"
						class="outline-none wrap-break-word hyphens-auto"
						tabindex="-1"
					>
						Dein Ziel
					</h2>

					<RadioField
						name="goal"
						label="Was möchtest du erreichen?"
						orientation="horizontal"
						:options="GOAL_OPTIONS"
					/>
				</section>

				<p
					v-if="isLastPart && hiddenErrors.length"
					class="notice notice--danger"
					role="alert"
				>
					{{ hiddenErrors.join(' ') }}
				</p>

				<slot
					name="actions"
					:is-last-part="isLastPart"
				>
					<BaseActions class="pt-8 border-t border-divider">
						<BaseButton type="submit">
							<template v-if="isLastPart">
								Bedarf berechnen
							</template>

							<template v-else>
								Weiter

								<BaseIcon :icon="ArrowRightIcon" />
							</template>
						</BaseButton>

						<BaseButton
							v-if="props.part"
							variant="outline"
							@click="emit('back')"
						>
							<BaseIcon :icon="ArrowLeftIcon" />

							Zurück
						</BaseButton>

						<BaseButton
							v-else
							variant="ghost"
							@click="onReset"
						>
							Zurücksetzen
						</BaseButton>
					</BaseActions>
				</slot>
			</div>
		</div>
	</BaseCard>
</template>
