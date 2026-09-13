<script setup lang="ts">
import { TriangleAlertIcon } from '@lucide/vue'
import { useForm } from 'vee-validate'
import { computed, nextTick, useTemplateRef } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { FieldGroup, FieldSeparator } from '@/components/ui/field'
import { FormFieldset, FormNumberField, FormRadioGroupField } from '@/components/form'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import WorkoutFieldArray from './WorkoutFieldArray.vue'
import { calculateCalories } from '../calculate-calories'
import { calorieCalculatorSchema } from '../calorie-calculator.schema'
import { goals, sexes } from '../calorie-calculator.data'
import type { CalorieCalculatorValues, CalorieResult } from '../calorie-calculator.types'

const emit = defineEmits<{
  calculated: [result: CalorieResult, values: CalorieCalculatorValues]
}>()

const { handleSubmit, resetForm, errors, submitCount } = useForm({
  validationSchema: calorieCalculatorSchema,
  initialValues: {
    sex: 'male',
    goal: 'maintain',
    steps: 0,
    exercises: [],
  },
})

const formElement = useTemplateRef<HTMLFormElement>('formElement')

const errorCount = computed<number>(() => Object.keys(errors.value).length)

const showErrorSummary = computed<boolean>(() => submitCount.value > 0 && errorCount.value > 0)

async function focusFirstInvalidControl(): Promise<void> {
  await nextTick()

  formElement.value
    ?.querySelector<HTMLElement>('input[aria-invalid="true"], button[aria-invalid="true"]')
    ?.focus()
}

const onSubmit = handleSubmit((values) => {
  const typedValues = values as CalorieCalculatorValues

  emit('calculated', calculateCalories(typedValues), typedValues)
}, focusFirstInvalidControl)
</script>

<template>
  <form
    ref="formElement"
    novalidate
    @submit="onSubmit"
  >
    <Card>
      <CardContent>
        <FieldGroup>
          <FormFieldset
            label="Grundumsatz"
            description="Diese vier Angaben bestimmen, was dein Körper in Ruhe verbraucht."
          >
            <FormRadioGroupField
              field-name="sex"
              label="Geschlecht"
              description="Bestimmt die Formel für deinen Grundumsatz."
              variant="button"
              :options="sexes"
              :sr-only-description="true"
            />

            <FieldGroup class="sm:flex-row">
              <FormNumberField
                field-name="age"
                label="Alter"
                unit="Jahre"
                :max="120"
              />

              <FormNumberField
                field-name="height"
                label="Größe"
                unit="cm"
                :max="250"
              />

              <FormNumberField
                field-name="weight"
                label="Gewicht"
                unit="kg"
                :max="400"
                :fraction-digits="1"
              />
            </FieldGroup>
          </FormFieldset>

          <FieldSeparator />

          <FormFieldset label="Alltagsbewegung">
            <FormNumberField
              field-name="steps"
              label="Schritte pro Tag"
              variant="stepper"
              :step="100"
              :max="50000"
            >
              <template #description>
                Dein Handy zählt schon mit — schau in der Health-App nach deinem Tagesdurchschnitt.

                <br />

                Zum Schätzen: rund 4.000 bei überwiegend sitzendem Alltag, rund 7.000 bei
                gemischtem, rund 10.000 wenn du viel auf den Beinen bist.
              </template>
            </FormNumberField>
          </FormFieldset>

          <FieldSeparator />

          <FormFieldset
            label="Training"
            description="Optional. Nur gezielter Sport — Spaziergänge und Wege stecken schon in deinen Schritten."
          >
            <WorkoutFieldArray field-name="exercises" />
          </FormFieldset>

          <FieldSeparator />

          <FormRadioGroupField
            field-name="goal"
            label="Dein Ziel"
            variant="tile"
            :options="goals"
          />
        </FieldGroup>
      </CardContent>

      <CardFooter
        class="border-border flex-col-reverse items-stretch gap-4 border-t pt-6 sm:flex-row sm:items-center sm:justify-between"
      >
        <Button
          type="button"
          variant="ghost"
          @click="resetForm()"
        >
          Zurücksetzen
        </Button>

        <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
          <p
            v-if="showErrorSummary"
            role="alert"
            class="border-destructive/30 bg-destructive/8 flex items-start gap-2 rounded-xl border p-3 text-sm sm:max-w-xs"
          >
            <LucideIcon
              :icon="TriangleAlertIcon"
              class="text-destructive mt-0.5 shrink-0"
            />

            <span>
              <strong class="block text-destructive">
                {{
                  errorCount === 1
                    ? 'Eine Angabe passt nicht.'
                    : `${errorCount} Angaben passen nicht.`
                }}
              </strong>

              Wir haben sie oben markiert.
            </span>
          </p>

          <Button
            type="submit"
            class="w-full sm:w-auto"
          >
            Bedarf berechnen
          </Button>
        </div>
      </CardFooter>
    </Card>
  </form>
</template>
