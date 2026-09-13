<script lang="ts">
export interface PieSlice {
  /** Must match a key in chartConfig — decides label and colour. */
  key: string
  value: number
}

interface PieDatum {
  key: string
  [property: string]: string | number
}
</script>

<script setup lang="ts">
import type { ChartConfig } from '@/components/ui/chart'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  componentToString,
} from '@/components/ui/chart'
import { Donut } from '@unovis/ts'
import { VisDonut, VisSingleContainer } from '@unovis/vue'
import { computed } from 'vue'

interface Props {
  chartData: PieSlice[]
  chartConfig: ChartConfig
  /** Text alternative — the chart renders with role="img". */
  alt: string
  centralLabel?: string
  centralSubLabel?: string
  arcWidth?: number
}

const props = withDefaults(defineProps<Props>(), {
  centralLabel: undefined,
  centralSubLabel: undefined,
  arcWidth: 30,
})

/**
 * ChartTooltipContent reads the keys of a datum and looks each one up in the config,
 * dropping everything it does not find. So the value has to sit under its own config
 * key — `{ key: 'fat', fat: 900 }`, not `{ macro: 'fat', kcal: 900 }`.
 */
const donutData = computed<PieDatum[]>(() =>
  props.chartData.map((slice) => ({ key: slice.key, [slice.key]: slice.value })),
)

const total = computed<number>(() => props.chartData.reduce((sum, slice) => sum + slice.value, 0))

const tooltipTriggers = computed(() => ({
  [Donut.selectors.segment]: componentToString(props.chartConfig, ChartTooltipContent, {
    hideLabel: true,
  })!,
}))

function sliceValue(datum: PieDatum): number {
  return Number(datum[datum.key])
}

function sliceColor(datum: PieDatum): string {
  return `var(--color-${datum.key})`
}
</script>

<template>
  <ChartContainer
    v-if="total > 0"
    role="img"
    :aria-label="props.alt"
    :config="props.chartConfig"
    class="max-h-62.5 mx-auto aspect-square"
    :style="{
      '--vis-donut-central-label-font-size': 'var(--text-3xl)',
      '--vis-donut-central-label-font-weight': 'var(--font-weight-bold)',
      '--vis-donut-central-label-text-color': 'var(--foreground)',
      '--vis-donut-central-sub-label-text-color': 'var(--muted-foreground)',
    }"
  >
    <VisSingleContainer
      :data="donutData"
      :margin="{ top: 30, bottom: 30 }"
    >
      <VisDonut
        :value="sliceValue"
        :color="sliceColor"
        :arc-width="props.arcWidth"
        :central-label="props.centralLabel"
        :central-sub-label="props.centralSubLabel"
        :central-label-offset-y="10"
      />

      <ChartTooltip :triggers="tooltipTriggers" />
    </VisSingleContainer>
  </ChartContainer>
</template>
