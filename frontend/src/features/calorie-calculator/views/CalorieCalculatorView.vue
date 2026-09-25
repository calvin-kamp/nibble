<script setup lang="ts">
import type { CalorieCalculatorValues, CalorieResult } from '../calorie-calculator.types'

import { nextTick, ref, useTemplateRef } from 'vue'
import { scrollBehavior } from '@lib/scroll'
import CalorieCalculatorForm from '../components/CalorieCalculatorForm.vue'
import CalorieCalculatorResult from '../components/CalorieCalculatorResult.vue'

const result = ref<CalorieResult | null>(null)
const submittedValues = ref<CalorieCalculatorValues | null>(null)

const formContainer = useTemplateRef<{ $el?: HTMLElement }>('formContainer')

function onCalculated(next: CalorieResult, values: CalorieCalculatorValues): void {
  result.value = next
  submittedValues.value = values
}

async function onEdit(): Promise<void> {
  result.value = null
  submittedValues.value = null

  await nextTick()

  const element = formContainer.value?.$el

  element?.scrollIntoView({ behavior: scrollBehavior(), block: 'start' })
  element?.querySelector<HTMLElement>('input, button, [role="radio"]')?.focus()
}
</script>

<template>
  <div :class="['flex flex-col gap-6 w-full mx-auto', result ? 'max-w-6xl' : 'max-w-2xl']">
    <div class="flex flex-col gap-4">
      <h1>Kalorienrechner</h1>

      <p
        v-if="!result"
        class="text-muted-foreground max-w-prose"
      >
        Wie viele Kalorien brauchst du wirklich? Wir rechnen Grundumsatz, Alltag, Training und
        Verdauung einzeln — und zeigen dir jeden Posten.
      </p>
    </div>

    <CalorieCalculatorForm
      v-show="!result"
      ref="formContainer"
      @calculated="onCalculated"
    />

    <CalorieCalculatorResult
      v-if="result && submittedValues"
      :result="result"
      :values="submittedValues"
      @edit="onEdit"
    />
  </div>
</template>
