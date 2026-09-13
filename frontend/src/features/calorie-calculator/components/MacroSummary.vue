<script setup lang="ts">
import { macroChart } from '../calorie-calculator.data'
import MacroPieChart from './MacroPieChart.vue'
import type { Macro } from '../calorie-calculator.types'

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
    <div class="flex flex-col gap-1">
      <h3 class="text-center text-base leading-snug font-bold">Deine Makro-Verteilung</h3>

      <p class="text-muted-foreground text-center text-sm">
        Ein Vorschlag, wie sich die {{ wholeNumber.format(props.targetCalories) }} kcal aufteilen
        lassen.
      </p>
    </div>

    <MacroPieChart :macros="props.macros" />

    <dl class="divide-border grid grid-cols-3 divide-x">
      <div
        v-for="macro in props.macros"
        :key="macro.name"
        class="flex flex-col-reverse items-center gap-1 px-2"
      >
        <dt class="text-muted-foreground flex items-center gap-1.5 text-xs">
          <span
            class="size-2 shrink-0 rounded-full"
            :style="{ backgroundColor: macroColor(macro.name) }"
            aria-hidden="true"
          />

          {{ macro.name }}
        </dt>

        <dd class="text-lg font-bold tabular-nums">{{ gramNumber.format(macro.amount) }} g</dd>
      </div>
    </dl>
  </div>
</template>
