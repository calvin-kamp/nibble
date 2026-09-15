<script setup lang="ts">
import type { Macro } from '../calorie-calculator.types'

import MacroPieChart from './MacroPieChart.vue'
import { macroChart } from '../calorie-calculator.data'

interface Props {
  macros: Macro[]
  targetCalories: number
}

const props = defineProps<Props>()

const gramNumber = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 1 })
const wholeNumber = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 })

function macroColor(name: string): string | undefined {
  return macroChart[name]?.color
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-1 text-center">
      <h3 class="text-center">Deine Makro-Verteilung</h3>

      <p class="text-muted-foreground text-sm">
        Ein Vorschlag, wie sich die {{ wholeNumber.format(props.targetCalories) }} kcal aufteilen
        lassen.
      </p>
    </div>

    <MacroPieChart :macros="props.macros" />

    <dl class="grid grid-cols-3 divide-border divide-x">
      <div
        v-for="macro in props.macros"
        :key="macro.name"
        class="flex flex-col-reverse items-center gap-1 px-2"
      >
        <dt class="flex items-center gap-1.5 text-muted-foreground text-sm">
          <span
            class="size-2 shrink-0 rounded-full"
            :style="{ backgroundColor: macroColor(macro.name) }"
            aria-hidden="true"
          />

          {{ macro.name }}
        </dt>

        <dd class="font-semibold tabular-nums">{{ gramNumber.format(macro.amount) }} g</dd>
      </div>
    </dl>
  </div>
</template>
