<script setup lang="ts">
import type { ChartConfig } from '@/components/ui/chart'
import type { PieSlice } from '@/components/shared/PieChart.vue'
import PieChart from '@/components/shared/PieChart.vue'
import { computed } from 'vue'
import { macroChart } from '../calorie-calculator.data'
import type { Macro, MacroChartEntry } from '../calorie-calculator.types'

interface Props {
  macros: Macro[]
}

const props = defineProps<Props>()

interface MacroChartSlice extends MacroChartEntry {
  kcal: number
  amount: number
}

const wholeNumber = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 })

const slices = computed<MacroChartSlice[]>(() =>
  props.macros.flatMap((macro) => {
    const entry = macroChart[macro.name]

    if (entry === undefined || macro.kcal <= 0) {
      return []
    }

    return [{ ...entry, kcal: macro.kcal, amount: macro.amount }]
  }),
)

const chartConfig = computed<ChartConfig>(() =>
  Object.fromEntries(
    slices.value.map((slice) => [
      slice.key,
      {
        label: slice.label,
        color: slice.color,
      },
    ]),
  ),
)

const chartData = computed<PieSlice[]>(() =>
  slices.value.map((slice) => ({
    key: slice.key,
    value: Math.round(slice.kcal),
  })),
)

const totalCalories = computed<number>(() =>
  slices.value.reduce((sum, slice) => sum + slice.kcal, 0),
)

const altText = computed<string>(() => {
  const parts: string[] = slices.value.map(
    (slice) =>
      `${slice.label} ${wholeNumber.format(slice.kcal)} Kilokalorien, ${wholeNumber.format(slice.amount)} Gramm`,
  )

  return `Nährstoffverteilung: ${parts.join(', ')}.`
})
</script>

<template>
  <PieChart
    :chart-data="chartData"
    :chart-config="chartConfig"
    :alt="altText"
    :central-label="wholeNumber.format(totalCalories)"
    central-sub-label="kcal"
  />
</template>
