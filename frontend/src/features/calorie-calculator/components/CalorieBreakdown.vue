<script setup lang="ts">
import type { CalorieCalculatorValues, CalorieResult } from '../calorie-calculator.types'

import { computed } from 'vue'
import { exercises } from '../calorie-calculator.data'

interface Props {
  result: CalorieResult
  values: CalorieCalculatorValues
}

interface BreakdownRow {
  name: string
  kcal: number
  caption: string
}

const props = defineProps<Props>()

const wholeNumber = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 })

const hasSteps = computed<boolean>(() => props.result.stepsConsumption >= 1)

const hasTraining = computed<boolean>(() => props.result.trainingConsumption >= 1)

const thermicEffect = computed<number>(
  () => props.result.maintenanceCalories - props.result.consumptionBeforeTef,
)

const trainingCaption = computed<string>(() =>
  props.values.exercises
    .filter((workout) => workout.met && workout.duration > 0 && workout.frequency > 0)
    .map((workout) => {
      const label: string | undefined = exercises
        .flatMap((group) => group.options)
        .find((option) => option.value === workout.met)?.label

      return `${workout.frequency}× ${workout.duration} min ${label ?? 'Training'}`
    })
    .join(', '),
)

const rows = computed<BreakdownRow[]>(() => {
  const list: BreakdownRow[] = [
    {
      name: 'Grundumsatz',
      kcal: props.result.basalMetabolicRate,
      caption:
        'Was dein Körper braucht, wenn du den ganzen Tag liegst. Aus Alter, Größe, Gewicht und Geschlecht.',
    },
  ]

  if (hasSteps.value) {
    list.push({
      name: 'Alltag',
      kcal: props.result.stepsConsumption,
      caption: `Aus ${wholeNumber.format(props.values.steps)} Schritten pro Tag.`,
    })
  }

  if (hasTraining.value) {
    list.push({
      name: 'Training',
      kcal: props.result.trainingConsumption,
      caption: `${trainingCaption.value} — auf die Woche verteilt.`,
    })
  }

  list.push({
    name: 'Verdauung',
    kcal: thermicEffect.value,
    caption: 'Rund 10 % dessen, was du isst, verbrennst du beim Verdauen.',
  })

  return list
})

function share(kcal: number): number {
  if (props.result.maintenanceCalories <= 0) {
    return 0
  }

  return Math.round((kcal / props.result.maintenanceCalories) * 100)
}
</script>

<template>
  <div>
    <h3 class="mb-4">Woraus sich das zusammensetzt</h3>

    <dl class="flex flex-col">
      <div
        v-for="row in rows"
        :key="row.name"
        class="flex flex-col gap-2 py-4 border-border border-b first:pt-0 nth-last-2:border-b-0"
      >
        <div class="flex items-baseline justify-between gap-4">
          <dt class="font-medium">
            {{ row.name }}
          </dt>

          <dd class="font-semibold whitespace-nowrap tabular-nums">
            {{ wholeNumber.format(row.kcal) }} kcal
          </dd>
        </div>

        <div
          class="h-1.5 overflow-hidden bg-muted rounded-full"
          aria-hidden="true"
        >
          <span
            class="block h-full bg-primary rounded-full"
            :style="{ width: `${share(row.kcal)}%` }"
          />
        </div>

        <p class="text-muted-foreground text-sm">
          {{ row.caption }}
        </p>
      </div>

      <div class="mt-1 flex items-baseline justify-between gap-4 pt-4 border-foreground border-t-2">
        <dt class="font-semibold">Erhaltungsbedarf</dt>

        <dd class="font-semibold whitespace-nowrap tabular-nums">
          {{ wholeNumber.format(props.result.maintenanceCalories) }} kcal
        </dd>
      </div>
    </dl>
  </div>
</template>
