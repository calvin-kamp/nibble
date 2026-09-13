<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import CalorieCalculatorForm from '../components/CalorieCalculatorForm.vue'
import CalorieCalculatorResult from '../components/CalorieCalculatorResult.vue'
import type { CalorieCalculatorValues, CalorieResult } from '../calorie-calculator.types'

const result = ref<CalorieResult | null>(null)
const submittedValues = ref<CalorieCalculatorValues | null>(null)

const formContainer = useTemplateRef<{ $el?: HTMLElement }>('formContainer')

function onCalculated(next: CalorieResult, values: CalorieCalculatorValues): void {
  result.value = next
  submittedValues.value = values
}

function scrollBehavior(): ScrollBehavior {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
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
  <div class="flex flex-col gap-4">
    <h1>Kalorienrechner</h1>

    <p
      v-if="!result"
      class="text-muted-foreground max-w-[60ch]"
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
</template>
