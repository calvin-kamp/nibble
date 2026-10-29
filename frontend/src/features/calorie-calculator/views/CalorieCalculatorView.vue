<script setup lang="ts">
import type {
	CalculatorPrefill,
	CalorieCalculatorValues,
	CalorieResult as CalorieResultData,
} from '@features/calorie-calculator/calorie-calculator.types'

import { CheckIcon, PencilIcon, UserPlusIcon } from '@lucide/vue'
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import CalorieCalculatorForm from '@features/calorie-calculator/components/CalorieCalculatorForm.vue'
import CalorieResult from '@features/calorie-calculator/components/CalorieResult.vue'
import { BaseButton, BaseIcon, BaseLink, BaseStepProgress } from '@shared/ui'

import { useBreakpoint } from '@shared/composables/breakpoint'
import { useFormSteps } from '@shared/composables/form-steps'
import { useToast } from '@shared/composables/toast'

import { saveNutritionSettings } from '@features/account/account.api'
import { useAuthStore } from '@features/auth/auth.store'
import { loadCalculatorPrefill } from '@features/calorie-calculator/calorie-calculator.api'
import { CALCULATOR_SECTIONS } from '@features/calorie-calculator/calorie-calculator.constants'
import { usePendingCalculationStore } from '@features/calorie-calculator/calorie-calculator.store'
import {
	calculateCalories,
	resultToNeeds,
} from '@features/calorie-calculator/calorie-calculator.utils'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

// With tracking, the form is prefilled from the account. It only appears afterwards, otherwise
// empty fields would show briefly.
const prefill = ref<CalculatorPrefill | null>(null)
const prefillReady = ref<boolean>(!auth.hasDataConsent)

onMounted(async () => {
	if (!auth.hasDataConsent || !auth.user) return

	try {
		prefill.value = await loadCalculatorPrefill(auth.user)
	} finally {
		prefillReady.value = true
	}
})

/** "Alter, Größe und Gewicht" */
const prefillSummary = computed<string>(() => {
	const labels = prefill.value?.labels ?? []

	return labels.length > 1
		? `${labels.slice(0, -1).join(', ')} und ${labels.at(-1)}`
		: (labels[0] ?? '')
})

const values = ref<CalorieCalculatorValues | null>(null)
const result = ref<CalorieResultData | null>(null)

// Rebuilt on every calculation so focus jumps to the result again
const resultKey = ref<number>(0)

// On phones, one section per step, followed by the result as its own step.
// From tablet up the form is on one page. In both cases the result replaces the
// form; "Angaben ändern" goes back.
const { isTablet } = useBreakpoint()

const isStepped = computed<boolean>(() => !isTablet.value)

const STEP_KEYS = [...CALCULATOR_SECTIONS.map((_, index) => String(index + 1)), 'ergebnis']
const RESULT_STEP = STEP_KEYS.length - 1

const form = ref<InstanceType<typeof CalorieCalculatorForm> | null>(null)
const furthest = ref<number>(0)

const steps = useFormSteps({
	keys: STEP_KEYS,
	enabled: isStepped,
	furthest,
	onChange: (index) => {
		if (index < RESULT_STEP) form.value?.focusHeading()
	},
})

const part = computed<number | undefined>(() =>
	isStepped.value ? Math.min(steps.index.value, RESULT_STEP - 1) : undefined,
)

// From tablet up without steps: the result stays visible until the details are changed
const editing = ref<boolean>(true)

const showsResult = computed<boolean>(() =>
	isStepped.value ? steps.index.value === RESULT_STEP : !editing.value && result.value !== null,
)

function onCalculate(formValues: CalorieCalculatorValues): void {
	values.value = formValues
	result.value = calculateCalories(formValues)
	resultKey.value++
	editing.value = false

	if (isStepped.value) steps.next()
}

async function editValues(): Promise<void> {
	if (isStepped.value) return steps.back()

	editing.value = true

	await nextTick()
	form.value?.focusHeading()
}

function onReset(): void {
	values.value = null
	result.value = null
	furthest.value = 0
	editing.value = true
}

// Signed in with consent: the result becomes the new daily needs
const saving = ref<boolean>(false)

async function applyAsNeeds(): Promise<void> {
	if (!result.value || !values.value) return

	saving.value = true

	try {
		await saveNutritionSettings({ needs: resultToNeeds(result.value), goal: values.value.goal })
		toast.show('Tagesbedarf übernommen')
		await router.push({ name: 'account-nutrition' })
	} catch {
		toast.show('Der Tagesbedarf konnte nicht gespeichert werden.', 'danger')
	} finally {
		saving.value = false
	}
}

// Guests carry their details through registration into onboarding, in memory only
const pendingCalculation = usePendingCalculationStore()

async function startSignup(): Promise<void> {
	if (values.value) pendingCalculation.save(values.value)

	await router.push({ name: 'auth-register' })
}
</script>

<template>
	<main class="content-wrapper pt-6 pb-10">
		<!-- Header, form and result centered at one width. max-w-4xl: on wide screens the rows would
         otherwise be too long to fill in. -->
		<div class="content-column content-column--form gap-6">
			<div class="flex flex-col gap-3">
				<h1>Kalorienrechner</h1>

				<p class="max-w-3xl text-lg text-muted">
					Wie viele Kalorien brauchst du wirklich? Wir rechnen Grundumsatz, Alltag,
					Training und Verdauung einzeln und zeigen dir jeden Posten. Ohne Anmeldung.
				</p>
			</div>

			<p
				v-if="prefillSummary && !showsResult"
				class="notice notice--info"
				role="note"
			>
				{{ prefillSummary }} haben wir aus deinem Konto übernommen. Du kannst sie hier für
				die Rechnung ändern, dauerhaft unter
				<BaseLink route-name="account-personal">Persönliches</BaseLink>.
			</p>

			<!-- v-show instead of v-if: after "Angaben ändern" the inputs are still there -->
			<CalorieCalculatorForm
				v-if="prefillReady"
				v-show="!showsResult"
				ref="form"
				:initial-values="prefill?.values"
				:part="part"
				@calculate="onCalculate"
				@reset="onReset"
				@part-complete="steps.next()"
				@back="steps.back()"
				@go-to-part="steps.goTo($event, { focus: false })"
			>
				<template
					v-if="isStepped"
					#header
				>
					<BaseStepProgress
						:current="(part ?? 0) + 1"
						:total="CALCULATOR_SECTIONS.length"
					/>
				</template>
			</CalorieCalculatorForm>

			<CalorieResult
				v-if="result && values && showsResult"
				:key="resultKey"
				:result="result"
				:values="values"
			>
				<!-- Adopting belongs right with the value, so it sits in the card with the result -->
				<template #actions>
					<div class="flex flex-col gap-4">
						<p v-if="!auth.isLoggedIn">
							Mit einem kostenlosen Konto zeigt dir dein Dashboard jeden Tag, wie viel
							noch übrig ist. Deine Angaben nehmen wir mit.
						</p>

						<p v-else-if="auth.hasDataConsent">
							Dein Dashboard rechnet dann mit diesem Wert. Ändern kannst du ihn
							jederzeit in den Einstellungen.
						</p>

						<div class="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
							<BaseButton
								v-if="!auth.isLoggedIn"
								variant="secondary"
								@click="startSignup"
							>
								<BaseIcon :icon="UserPlusIcon" />
								Konto erstellen
							</BaseButton>

							<BaseButton
								v-else-if="auth.hasDataConsent"
								variant="secondary"
								:disabled="saving"
								@click="applyAsNeeds"
							>
								<BaseIcon :icon="CheckIcon" />
								Als Tagesbedarf übernehmen
							</BaseButton>

							<BaseButton
								variant="outline"
								@click="editValues"
							>
								<BaseIcon :icon="PencilIcon" />
								Angaben ändern
							</BaseButton>
						</div>
					</div>
				</template>
			</CalorieResult>
		</div>
	</main>
</template>
