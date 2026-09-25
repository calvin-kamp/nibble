<script setup lang="ts">
import type { RecipeIngredient } from '../recipes.types'

import { Label as RekaLabel } from 'reka-ui'
import { ref, useId, watch } from 'vue'
import { NumberInputControl } from '@components/form/controls'
import { formatIngredientAmount } from '../recipes.utils'

interface Props {
  ingredients: RecipeIngredient[]
  baseServings: number
}

const props = defineProps<Props>()

const servingsFieldId = useId()

const servingsAmount = ref<number>(props.baseServings)

watch(
  () => props.baseServings,
  (baseServings) => (servingsAmount.value = baseServings),
)
</script>

<template>
  <section
    aria-labelledby="ingredients-heading"
    class="flex flex-col gap-4 min-w-0"
  >
    <h2
      id="ingredients-heading"
      class="pb-4 border-b"
    >
      Zutaten
    </h2>

    <div class="flex flex-wrap items-center justify-between gap-4">
      <RekaLabel
        :for="servingsFieldId"
        class="text-sm text-muted-foreground"
      >
        Portionen
      </RekaLabel>

      <div class="w-36">
        <NumberInputControl
          :id="servingsFieldId"
          v-model="servingsAmount"
          :min="1"
          :max="12"
          stepper
        />
      </div>
    </div>

    <p
      aria-live="polite"
      class="sr-only"
    >
      Mengen für {{ servingsAmount }} {{ servingsAmount === 1 ? 'Portion' : 'Portionen' }}
    </p>

    <ul class="flex flex-col">
      <li
        v-for="ingredient in props.ingredients"
        :key="ingredient.name"
        class="flex items-baseline gap-3 py-3 border-b md:last:border-b-0"
      >
        <span class="w-20 shrink-0 text-right font-medium tabular-nums">
          {{ formatIngredientAmount(ingredient, props.baseServings, servingsAmount) }}
        </span>

        <span>
          {{ ingredient.name }}
        </span>
      </li>
    </ul>
  </section>
</template>
