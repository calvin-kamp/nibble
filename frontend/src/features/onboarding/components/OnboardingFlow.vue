<script setup lang="ts">
import type {
	CalorieCalculatorValues,
	Goal,
} from '@features/calorie-calculator/calorie-calculator.types'
import type {
	BodyData,
	DailyNeeds,
	NeedsMethod,
	OnboardingData,
	OnboardingProgress,
	OnboardingStepId,
	OnboardingStepItem,
} from '@features/onboarding/onboarding.types'

import { computed, onMounted, reactive, ref, watch } from 'vue'

import BodyDataStep from '@features/onboarding/components/steps/BodyDataStep.vue'
import CalculatorStep from '@features/onboarding/components/steps/CalculatorStep.vue'
import ConsentStep from '@features/onboarding/components/steps/ConsentStep.vue'
import DoneStep from '@features/onboarding/components/steps/DoneStep.vue'
import GoalStep from '@features/onboarding/components/steps/GoalStep.vue'
import ManualNeedsStep from '@features/onboarding/components/steps/ManualNeedsStep.vue'
import NeedsMethodStep from '@features/onboarding/components/steps/NeedsMethodStep.vue'
import UsernameStep from '@features/onboarding/components/steps/UsernameStep.vue'
import { BaseProgressBar } from '@shared/ui'

import { useBreakpoint } from '@shared/composables/breakpoint'
import { useFormSteps } from '@shared/composables/form-steps'

import { CALCULATOR_SECTIONS } from '@features/calorie-calculator/calorie-calculator.constants'
import { usePendingCalculationStore } from '@features/calorie-calculator/calorie-calculator.store'
import { useOnboardingStore } from '@features/onboarding/onboarding.store'
import { ageOn } from '@shared/utils/date'

interface Props {
	/** State from memory or, after a reload, from the backend; null on the first visit */
	progress: OnboardingProgress | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
	complete: [data: OnboardingData]
}>()

const onboarding = useOnboardingStore()
const pendingCalculation = usePendingCalculationStore()

// Saved state. A guest coming from the calculator has goal and details prefilled.
// They still go through every step; nothing is saved until consent is given.
function initialData(): OnboardingData {
	const data: OnboardingData = props.progress
		? { ...props.progress.data }
		: { username: '', consent: false }
	const pending = pendingCalculation.values

	if (pending && !data.calculatorValues) {
		data.goal ??= pending.goal
		data.method ??= 'calculate'
		data.calculatorValues = pending
		// The body data step starts with what the calculator already knows. No birth date: the
		// calculator only asks for the age.
		data.body ??= { sex: pending.sex, heightCm: pending.height, weightKg: pending.weight }
	}

	return data
}

const data = reactive<OnboardingData>(initialData())

const { isTablet } = useBreakpoint()

const consentAnswered = ref<boolean>(props.progress?.consentAnswered ?? false)

// Which steps exist depends on the answers: without consent the flow jumps straight to the
// end, and on phones the calculator is split into sections.
function buildSteps(consent: boolean, method: NeedsMethod | undefined): OnboardingStepItem[] {
	const list: OnboardingStepItem[] = [{ id: 'username' }, { id: 'consent' }]

	if (consent) {
		list.push({ id: 'body' }, { id: 'goal' }, { id: 'method' })

		if (method === 'calculate') {
			list.push(
				...(isTablet.value
					? [{ id: 'calculator' as const }]
					: CALCULATOR_SECTIONS.map((_, part) => ({ id: 'calculator' as const, part }))),
				{ id: 'calculator', result: true },
			)
		}

		if (method === 'manual') list.push({ id: 'manual' })
	}

	list.push({ id: 'done' })

	return list
}

const stepList = computed<OnboardingStepItem[]>(() => buildSteps(data.consent, data.method))

// For "Schritt x von y", count the longest possible path while answers are missing.
// Otherwise the total would grow with every answer.
const countedSteps = computed<OnboardingStepItem[]>(() =>
	buildSteps(consentAnswered.value ? data.consent : true, data.method ?? 'calculate'),
)

// Keeps the step in the address, e.g. /einrichten?schritt=ziel
const STEP_KEYS: Record<OnboardingStepId, string> = {
	username: 'benutzername',
	consent: 'datenschutz',
	body: 'koerperdaten',
	goal: 'ziel',
	method: 'bedarf',
	calculator: 'rechner',
	manual: 'werte',
	done: 'fertig',
}

function keyOf(step: OnboardingStepItem): string {
	if (step.result) return `${STEP_KEYS.calculator}-ergebnis`
	if (step.part !== undefined) return `${STEP_KEYS.calculator}-${step.part + 1}`

	return STEP_KEYS[step.id]
}

const keys = computed<string[]>(() => stepList.value.map(keyOf))

/** Index of a saved step. After switching between phone and desktop, the calculator section
 *  no longer exists, so the flow continues at the calculator. */
function indexOfKey(key: string): number {
	const index = keys.value.indexOf(key)

	if (index >= 0 || !key.startsWith(STEP_KEYS.calculator)) return Math.max(index, 0)

	return keys.value.findIndex((entry) => entry.startsWith(STEP_KEYS.calculator))
}

// The address cannot take the user past the saved state
const furthest = ref<number>(props.progress ? indexOfKey(props.progress.step) : 0)

const steps = useFormSteps({ keys, furthest })

const current = computed<OnboardingStepItem>(() => stepList.value[steps.index.value]!)

// The last step does not count, it is the summary
const stepCount = computed<number>(() => countedSteps.value.length - 1)

// On the first visit without a step in the address, continue where the user left off
onMounted(() => {
	if (steps.index.value === 0 && furthest.value > 0) steps.goTo(furthest.value)
})

// Every step change is kept in memory, so leaving and coming back resumes here. Health data
// only after consent.
watch(steps.key, (step) => {
	const saved: OnboardingData = data.consent
		? { ...data }
		: { username: data.username, consent: false }

	onboarding.save({ step, consentAnswered: consentAnswered.value, data: saved })
})

/** When an answer changes the remaining path, later steps count as not reached yet */
function resetFurthest(): void {
	furthest.value = steps.index.value
}

function onUsername(username: string): void {
	data.username = username
	steps.next()
}

function onConsent(consent: boolean): void {
	if (consent !== data.consent) resetFurthest()

	data.consent = consent
	consentAnswered.value = true

	// Without consent we also save no goal, no daily needs and no personal details
	if (!consent) {
		data.body = undefined
		data.goal = undefined
		data.method = undefined
		data.needs = undefined
		data.calculatorValues = undefined
		pendingCalculation.clear()
	}

	steps.next()
}

/** Nothing entered: nothing is saved. Entered details also prefill the calculator. */
function onBody(body: BodyData | undefined): void {
	data.body = body

	if (body) {
		const age = body.birthDate ? ageOn(body.birthDate) : null

		data.calculatorValues = {
			...data.calculatorValues,
			...(body.sex && { sex: body.sex }),
			...(age !== null && { age }),
			...(body.heightCm && { height: body.heightCm }),
			...(body.weightKg && { weight: body.weightKg }),
		}
	}

	steps.next()
}

function onGoal(goal: Goal | undefined): void {
	data.goal = goal
	steps.next()
}

function onMethod(method: NeedsMethod): void {
	if (method !== data.method) {
		data.needs = undefined
		resetFurthest()
	}

	data.method = method
	steps.next()
}

function onNeeds(needs: DailyNeeds): void {
	data.needs = needs
	steps.next()
}

function onCalculatorPart(values: Partial<CalorieCalculatorValues>): void {
	data.calculatorValues = values
	steps.next()
}

function onCalculated(values: CalorieCalculatorValues): void {
	data.calculatorValues = values
	data.goal = values.goal
	steps.next()
}

function onConfirm(payload: { needs: DailyNeeds; goal: Goal }): void {
	data.goal = payload.goal
	onNeeds(payload.needs)
}

function goToCalculatorPart(part: number): void {
	steps.goTo(keys.value.indexOf(`${STEP_KEYS.calculator}-${part + 1}`), { focus: false })
}

function onComplete(): void {
	pendingCalculation.clear()
	emit('complete', { ...data })
}
</script>

<template>
	<div class="flex flex-wrap items-center justify-between gap-x-4 gap-y-3">
		<p class="font-display text-2xl font-extrabold tracking-tighter text-forest">nibble</p>

		<p class="text-sm font-semibold text-muted">
			{{
				current.id === 'done'
					? 'Fertig'
					: `Schritt ${steps.index.value + 1} von ${stepCount}`
			}}
		</p>

		<BaseProgressBar
			class="basis-full h-1.5"
			:value="steps.index.value + 1"
			:max="countedSteps.length"
			label="Fortschritt"
		/>
	</div>

	<UsernameStep
		v-if="current.id === 'username'"
		:username="data.username"
		@next="onUsername"
	/>

	<ConsentStep
		v-else-if="current.id === 'consent'"
		:consent="data.consent"
		@next="onConsent"
		@back="steps.back()"
	/>

	<BodyDataStep
		v-else-if="current.id === 'body'"
		:body="data.body"
		@next="onBody"
		@back="steps.back()"
	/>

	<GoalStep
		v-else-if="current.id === 'goal'"
		:goal="data.goal"
		@next="onGoal"
		@back="steps.back()"
	/>

	<NeedsMethodStep
		v-else-if="current.id === 'method'"
		:method="data.method"
		@next="onMethod"
		@back="steps.back()"
	/>

	<!-- One instance for all sections and the result, so the inputs are kept -->
	<CalculatorStep
		v-else-if="current.id === 'calculator'"
		:goal="data.goal"
		:values="data.calculatorValues"
		:part="current.part"
		:show-result="current.result"
		@calculated="onCalculated"
		@confirm="onConfirm"
		@back="steps.back()"
		@part-complete="onCalculatorPart"
		@go-to-part="goToCalculatorPart"
	/>

	<ManualNeedsStep
		v-else-if="current.id === 'manual'"
		:needs="data.needs"
		@next="onNeeds"
		@back="steps.back()"
	/>

	<DoneStep
		v-else
		:data="data"
		@back="steps.back()"
		@complete="onComplete"
	/>
</template>
