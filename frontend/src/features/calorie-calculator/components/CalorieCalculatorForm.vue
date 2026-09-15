<script setup lang="ts">
import type { CalorieCalculatorValues, CalorieResult } from '../calorie-calculator.types'

import { useForm } from 'vee-validate'
import { DumbbellIcon } from '@lucide/vue'
import { nextTick, useTemplateRef } from 'vue'
import { UiButton, UiCard, UiIcon, UiSeparator } from '@components/ui'
import {
  FormFieldArray,
  FormNumberField,
  FormRadioGroupField,
  FormSection,
  FormSelectField,
} from '@components/form'
import { calculateCalories } from '../calculate-calories'
import { calorieCalculatorSchema } from '../calorie-calculator.schema'
import { exercises, goals, sexes } from '../calorie-calculator.data'
import { useUserStore } from '@stores/user.store'

const emit = defineEmits<{
  calculated: [result: CalorieResult, values: CalorieCalculatorValues]
}>()

const user = useUserStore()

const { handleSubmit, resetForm } = useForm({
  validationSchema: calorieCalculatorSchema,
  initialValues: {
    sex: user.sex,
    age: user.age,
    height: user.height,
    weight: user.weight,
    steps: 0,
    exercises: [],
    goal: 'maintain',
  },
})

const formElement = useTemplateRef<HTMLFormElement>('formElement')

const FOCUSABLE = 'input, select, textarea, button, [tabindex]'

function focusableWithin(element: HTMLElement): HTMLElement {
  if (element.matches(FOCUSABLE)) return element

  return element.querySelector<HTMLElement>(FOCUSABLE) ?? element
}

function scrollBehavior(): ScrollBehavior {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
}

async function revealFirstInvalidField(): Promise<void> {
  await nextTick()

  const invalid = formElement.value?.querySelector<HTMLElement>('[aria-invalid="true"]')

  if (!invalid) return

  focusableWithin(invalid).focus({ preventScroll: true })

  invalid.scrollIntoView({ behavior: scrollBehavior(), block: 'center' })
}

const onSubmit = handleSubmit((values) => {
  const typedValues = values as CalorieCalculatorValues

  emit('calculated', calculateCalories(typedValues), typedValues)
}, revealFirstInvalidField)
</script>

<template>
  <UiCard as-child>
    <form
      ref="formElement"
      novalidate
      class="flex flex-col gap-6"
      @submit="onSubmit"
    >
      <FormSection
        label="Grundumsatz"
        description="Diese vier Angaben bestimmen, was dein Körper in Ruhe verbraucht."
      >
        <FormRadioGroupField
          field-name="sex"
          label="Geschlecht"
          variant="segment"
          :options="sexes"
          :columns="2"
        />

        <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
          <FormNumberField
            field-name="age"
            label="Alter"
            :min="0"
            :max="120"
          >
            <template #trailing> Jahre </template>
          </FormNumberField>

          <FormNumberField
            field-name="height"
            label="Größe"
            :min="0"
            :max="250"
          >
            <template #trailing> cm </template>
          </FormNumberField>

          <FormNumberField
            field-name="weight"
            label="Gewicht"
            :min="0"
            :max="400"
            :fraction-digits="1"
          >
            <template #trailing> kg </template>
          </FormNumberField>
        </div>
      </FormSection>

      <UiSeparator />

      <FormSection label="Alltagsbewegung">
        <FormNumberField
          field-name="steps"
          label="Schritte pro Tag"
          :min="0"
          :max="50000"
          :step="100"
          stepper
        >
          <template #description>
            Dein Handy zählt schon mit — schau in der Health-App nach deinem Tagesdurchschnitt.

            <br />

            Zum Schätzen: rund 4.000 bei überwiegend sitzendem Alltag, rund 7.000 bei gemischtem,
            rund 10.000 wenn du viel auf den Beinen bist.
          </template>
        </FormNumberField>
      </FormSection>

      <UiSeparator />

      <FormSection
        label="Training"
        description="Optional. Nur gezielter Sport — Spaziergänge und Wege stecken schon in deinen Schritten."
      >
        <FormFieldArray
          field-name="exercises"
          entry-label="Training"
          empty-title="Kein Training eingetragen"
          empty-text="Wir rechnen dann nur mit Grundumsatz und Alltagsbewegung."
          add-label="Training hinzufügen"
          add-more-label="Weiteres Training hinzufügen"
          :new-entry="() => ({ met: '', duration: 0, frequency: 0 })"
        >
          <template #media>
            <UiIcon
              :icon="DumbbellIcon"
              :size="24"
            />
          </template>

          <template #default="{ path }">
            <FormSelectField
              :field-name="`${path}.met`"
              label="Sportart"
              placeholder="Sportart wählen"
              :options="exercises"
            />

            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <FormNumberField
                :field-name="`${path}.duration`"
                label="Dauer"
                :min="0"
                :max="600"
                :step="5"
              >
                <template #trailing> min </template>
              </FormNumberField>

              <FormNumberField
                :field-name="`${path}.frequency`"
                label="Pro Woche"
                :min="0"
                :max="7"
              >
                <template #trailing> mal </template>
              </FormNumberField>
            </div>
          </template>
        </FormFieldArray>
      </FormSection>

      <UiSeparator />

      <FormRadioGroupField
        field-name="goal"
        label="Dein Ziel"
        variant="card"
        :options="goals"
        :columns="3"
      />

      <div
        class="flex flex-col-reverse items-stretch gap-4 pt-6 border-border border-t md:flex-row md:items-center md:justify-between"
      >
        <UiButton
          type="button"
          variant="ghost"
          @click="resetForm()"
        >
          Zurücksetzen
        </UiButton>

        <UiButton
          type="submit"
          class="w-full md:w-auto"
        >
          Bedarf berechnen
        </UiButton>
      </div>
    </form>
  </UiCard>
</template>
