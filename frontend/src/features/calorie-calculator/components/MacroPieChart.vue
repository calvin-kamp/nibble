<script setup lang="ts">
import type { Macro, MacroChartEntry } from '../calorie-calculator.types'

import { computed } from 'vue'
import { macroChart } from '../calorie-calculator.data'

interface Props {
  macros: Macro[]
}

interface MacroArc extends MacroChartEntry {
  kcal: number
  amount: number
  length: number
  offset: number
}

const props = defineProps<Props>()

const RADIUS = 40
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

const wholeNumber = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 })

const slices = computed(() =>
  props.macros.flatMap((macro) => {
    const entry = macroChart[macro.name]

    if (entry === undefined || macro.kcal <= 0) {
      return []
    }

    return [{ ...entry, kcal: macro.kcal, amount: macro.amount }]
  }),
)

const totalCalories = computed<number>(() =>
  slices.value.reduce((sum, slice) => sum + slice.kcal, 0),
)

const arcs = computed<MacroArc[]>(() => {
  let offset = 0

  return slices.value.map((slice) => {
    const length = totalCalories.value > 0 ? (slice.kcal / totalCalories.value) * CIRCUMFERENCE : 0

    const arc: MacroArc = { ...slice, length, offset }

    offset += length

    return arc
  })
})

const altText = computed<string>(() => {
  const parts: string[] = slices.value.map(
    (slice) =>
      `${slice.label} ${wholeNumber.format(slice.kcal)} Kilokalorien, ${wholeNumber.format(slice.amount)} Gramm`,
  )

  return `Nährstoffverteilung von insgesamt ${wholeNumber.format(totalCalories.value)} Kilokalorien: ${parts.join(', ')}.`
})
</script>

<template>
  <div class="relative mx-auto size-44 md:size-52">
    <svg
      viewBox="0 0 100 100"
      class="size-full"
      role="img"
      :aria-label="altText"
    >
      <g transform="rotate(-90 50 50)">
        <circle
          v-for="arc in arcs"
          :key="arc.key"
          cx="50"
          cy="50"
          :r="RADIUS"
          fill="none"
          :stroke="arc.color"
          stroke-width="14"
          :stroke-dasharray="`${arc.length} ${CIRCUMFERENCE - arc.length}`"
          :stroke-dashoffset="-arc.offset"
        />
      </g>
    </svg>

    <div
      class="absolute inset-0 flex flex-col items-center justify-center"
      aria-hidden="true"
    >
      <p class="font-semibold tabular-nums">{{ wholeNumber.format(totalCalories) }}</p>

      <p class="text-muted-foreground text-sm">kcal</p>
    </div>
  </div>
</template>
