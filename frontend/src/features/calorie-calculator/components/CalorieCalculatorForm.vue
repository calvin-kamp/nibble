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
	TRAINING_SELECT_GROUPS,
} from '@features/calorie-calculator/calorie-calculator.constants'
import { calorieCalculatorSchema } from '@features/calorie-calculator/calorie-calculator.schema'
import { focusFirstError, NumberField, RadioField, SelectField } from '@shared/forms'

interface Props {
	initialValues?: Partial<CalorieCalculatorValues>
	/**
	 * Show only one section (index in CALCULATOR_SECTIONS), e.g. step by step on phones.
	 * Without part, all sections are shown in one form.
	 */
	part?: number
}

const props = withDefaults(defineProps<Props>(), {
	initialValues: () => ({}),
	part: undefined,
})

const emit = defineEmits<{
	calculate: [values: CalorieCalculatorValues]
	reset: []
	/** The visible section is valid and the next one follows. Carries the intermediate values. */
	'part-complete': [values: Partial<CalorieCalculatorValues>]
	/** Back to the previous section */
	back: []
	/** On submit, there is an error in another section */
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
	props.part === undefined ? CALCULATOR_SECTIONS : [CALCULATOR_SECTIONS[props.part]!],
)

const isLastPart = computed<boolean>(
	() => props.part === undefined || props.part === CALCULATOR_SECTIONS.length - 1,
)

function isVisible(section: CalculatorSection): boolean {
	return visibleSections.value.includes(section)
}

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

// When switching sections, the new section's heading receives focus. After an error in another
// section, the first invalid field receives it instead.
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
			headings.value[CALCULATOR_SECTIONS[part]!]?.focus()
		}
	},
)

/** Focus the heading of the visible section, e.g. after going back from the result */
function focusHeading(): void {
	headings.value[CALCULATOR_SECTIONS[props.part ?? 0]!]?.focus()
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

		// If the error is in another section, go back there. The watcher on part then sets focus once
		// the section is visible.
		if (props.part !== undefined && section && !isVisible(section)) {
			focusErrorAfterSwitch = true
			emit('go-to-part', CALCULATOR_SECTIONS.indexOf(section))
			return
		}

		focusFirstError(evt)
	},
)

async function onSubmit(event: Event): Promise<void> {
	if (isLastPart.value) return submitAll(event)

	event.preventDefault()

	const section = CALCULATOR_SECTIONS[props.part!]!
	const results = await Promise.all(
		fieldsOf(section).map((field) => validateField(field as never)),
	)

	// Intermediate values: only the sections so far have been validated
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
			<!-- E.g. the progress indicator when the calculator runs section by section -->
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
							class="text-2xl outline-none"
							tabindex="-1"
						>
							Grundumsatz
						</h2>

						<p class="text-muted">
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
						class="text-2xl outline-none"
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
						:step="1000"
						increment-label="1.000 Schritte mehr"
						decrement-label="1.000 Schritte weniger"
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
							class="text-2xl outline-none"
							tabindex="-1"
						>
							Training
						</h2>

						<p class="text-muted">
							Optional. Nur gezielter Sport, Spaziergänge und Wege stecken schon in
							deinen Schritten. Hat dein Handy beim Laufen oder Wandern mitgezählt,
							trag die Einheit nicht zusätzlich ein.
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
							<BaseButton @click="addWorkout">
								<BaseIcon :icon="PlusIcon" />
								Training hinzufügen
							</BaseButton>
						</template>
					</BaseEmptyState>

					<template v-else>
						<!-- Each workout as its own surface with a heading. role="group" groups the fields
                     without the look of a fieldset with border and legend. -->
						<ul class="flex flex-col gap-4">
							<li
								v-for="(workout, index) in workouts"
								:key="workout.key"
							>
								<div
									class="flex flex-col gap-4 p-4 rounded-lg bg-surface-muted md:p-5"
									role="group"
									:aria-labelledby="`workout-${workout.key}-title`"
								>
									<div class="flex items-center justify-between gap-3">
										<h3
											:id="`workout-${workout.key}-title`"
											class="font-sans text-md font-bold tracking-normal"
										>
											Training {{ index + 1 }}
										</h3>

										<BaseButton
											variant="outline"
											size="sm"
											:aria-label="`Training ${index + 1} entfernen`"
											@click="remove(index)"
										>
											<BaseIcon
												:icon="TrashIcon"
												:size="16"
											/>
											Entfernen
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
							class="text-sm font-semibold text-danger"
						>
							{{ errors.exercises }}
						</p>

						<BaseButton
							class="self-center"
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
						class="text-2xl outline-none"
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

				<!-- Custom actions, e.g. back and next in onboarding -->
				<slot
					name="actions"
					:is-last-part="isLastPart"
				>
					<BaseActions class="pt-8 border-t border-divider">
						<BaseButton type="submit">
							<template v-if="isLastPart">Bedarf berechnen</template>

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
							>Zurücksetzen</BaseButton
						>
					</BaseActions>
				</slot>
			</div>
		</div>
	</BaseCard>
</template>
