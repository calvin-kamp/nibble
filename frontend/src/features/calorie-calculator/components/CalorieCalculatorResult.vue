<script setup lang="ts">
import { RotateCcwIcon, TargetIcon } from '@lucide/vue'
import { computed, onMounted, useTemplateRef } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import InlineNotice from '@/components/shared/InlineNotice.vue'
import CalorieBreakdown from './CalorieBreakdown.vue'
import MacroSummary from './MacroSummary.vue'
import ResultCta from './ResultCta.vue'
import { goals } from '../calorie-calculator.data'
import { MIN_INTAKE } from '../calorie-calculator.constants'
import type { CalorieCalculatorValues, CalorieResult } from '../calorie-calculator.types'

interface Props {
  result: CalorieResult
  values: CalorieCalculatorValues
}

const props = defineProps<Props>()

defineEmits<{
  edit: []
}>()

interface ResultNotice {
  id: string
  variant: 'info' | 'warning'
  title: string
  text: string
}

const GOAL_CAPTION: Record<CalorieCalculatorValues['goal'], string> = {
  diet: 'So viel darfst du täglich essen, um abzunehmen.',
  maintain: 'So viel darfst du täglich essen, um dein Gewicht zu halten.',
  gain: 'So viel solltest du täglich essen, um zuzunehmen.',
}

const wholeNumber = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 })

const container = useTemplateRef<HTMLElement>('container')

onMounted(() => container.value?.focus())

const goalLabel = computed<string>(
  () => goals.find((goal) => goal.value === props.values.goal)?.label ?? '',
)

const hasSafetyAdjustment = computed<boolean>(() => props.result.safetyAdjustment >= 1)

const minimumExceedsMaintenance = computed<boolean>(
  () =>
    hasSafetyAdjustment.value &&
    props.values.goal !== 'gain' &&
    props.result.targetCalories >= props.result.maintenanceCalories,
)

const headerCaption = computed<string>(() =>
  minimumExceedsMaintenance.value
    ? 'Das ist unsere Untergrenze, nicht dein Ziel — siehe Hinweis.'
    : GOAL_CAPTION[props.values.goal],
)

const bmi = computed<number>(() => props.values.weight / (props.values.height / 100) ** 2)

const notices = computed<ResultNotice[]>(() => {
  const list: ResultNotice[] = []

  if (props.values.age >= 18 && bmi.value < 18.5 && props.values.goal === 'diet') {
    list.push({
      id: 'underweight',
      variant: 'warning',
      title: 'Dein Gewicht liegt unter dem Normalbereich.',
      text: 'Ein Kaloriendefizit ist hier nicht das Richtige für dich. Sprich mit deiner Ärztin oder deinem Arzt, bevor du weniger isst.',
    })
  }

  if (minimumExceedsMaintenance.value) {
    list.push({
      id: 'below-minimum',
      variant: 'warning',
      title: 'Dein Erhaltungsbedarf liegt unter unserer Untergrenze.',
      text: `Wir gehen nie unter ${wholeNumber.format(MIN_INTAKE[props.values.sex])} kcal — darunter lässt sich dein Bedarf an Vitaminen und Mineralstoffen kaum noch decken. Dein Körper verbraucht bei deiner aktuellen Bewegung aber weniger als das. Über das Essen lässt sich hier also kein Defizit erzeugen. Wenn du Schritte oder Training bisher nicht eingetragen hast, hol das nach — sonst besprich dein Ziel mit deiner Ärztin oder deinem Arzt.`,
    })
  } else if (hasSafetyAdjustment.value) {
    list.push({
      id: 'safety',
      variant: 'warning',
      title: `Wir haben deinen Wert um ${wholeNumber.format(props.result.safetyAdjustment)} kcal angehoben.`,
      text: 'Unter diesem Wert lässt sich dein Bedarf an Vitaminen und Mineralstoffen kaum noch decken. Wenn du schneller abnehmen willst, erhöh lieber deine Bewegung, statt weiter zu kürzen.',
    })
  }

  if (props.values.age < 18) {
    list.push({
      id: 'adolescent',
      variant: props.values.goal === 'diet' ? 'warning' : 'info',
      title: 'Du bist unter 18.',
      text:
        props.values.goal === 'diet'
          ? 'Der Rechner benutzt eine Formel für Erwachsene, und im Wachstum liegt dein Bedarf höher als sie annimmt. Weniger zu essen als hier steht, solltest du vorher mit deinem Arzt oder deiner Ärztin besprechen.'
          : 'Der Rechner benutzt eine Formel für Erwachsene — im Wachstum liegt dein tatsächlicher Bedarf eher etwas höher. Nimm die Zahl als groben Anhaltspunkt.',
    })
  }

  if (props.values.age >= 75) {
    list.push({
      id: 'senior',
      variant: 'info',
      title: 'Ab etwa 75 Jahren wird die Schätzung ungenauer.',
      text: 'Die Formel wurde an Erwachsenen bis 78 Jahren geprüft. Im höheren Alter verschiebt sich das Verhältnis von Muskel- zu Fettmasse, und der Wert kann dadurch zu hoch liegen.',
    })
  }

  return list
})
</script>

<template>
  <section
    ref="container"
    tabindex="-1"
    aria-labelledby="result-heading"
    class="flex w-full flex-col gap-8 outline-hidden"
  >
    <h2
      id="result-heading"
      class="font-bold"
    >
      Dein Ergebnis
    </h2>

    <Card class="gap-0 py-0">
      <div class="bg-primary/6 border-border flex flex-col items-start gap-1.5 border-b p-6 md:p-7">
        <p class="text-primary dark:text-chart-1 flex items-center gap-1.5 text-sm font-semibold">
          <LucideIcon
            :icon="TargetIcon"
            :size="14"
          />
          Ziel: {{ goalLabel }}
        </p>

        <p
          class="flex items-baseline gap-2.5 text-5xl font-bold tracking-tighter tabular-nums md:text-6xl"
        >
          {{ wholeNumber.format(props.result.targetCalories) }}
          <span class="text-muted-foreground text-base font-medium tracking-normal">
            kcal pro Tag
          </span>
        </p>

        <p class="text-muted-foreground text-sm">
          {{ headerCaption }}
        </p>
      </div>

      <CardContent
        v-if="notices.length > 0"
        class="flex flex-col gap-3 pt-6"
      >
        <InlineNotice
          v-for="notice in notices"
          :key="notice.id"
          :variant="notice.variant"
          :title="notice.title"
        >
          {{ notice.text }}
        </InlineNotice>
      </CardContent>

      <CardContent class="py-6">
        <CalorieBreakdown
          :result="props.result"
          :values="props.values"
        />
      </CardContent>

      <CardContent class="border-border border-t py-6">
        <MacroSummary
          :macros="props.result.macros"
          :target-calories="props.result.targetCalories"
        />
      </CardContent>

      <CardContent class="pb-6">
        <InlineNotice>
          Das Ergebnis ist eine Schätzung auf Basis von Durchschnittswerten. Wieg dich zwei Wochen
          lang regelmäßig und pass die Menge an, wenn sich nichts bewegt. Bei Erkrankungen oder
          Medikamenten sprich mit deiner Ärztin oder deinem Arzt.
        </InlineNotice>
      </CardContent>
    </Card>

    <ResultCta />

    <div class="flex justify-center">
      <Button
        type="button"
        variant="ghost"
        @click="$emit('edit')"
      >
        <LucideIcon :icon="RotateCcwIcon" />
        Angaben ändern
      </Button>
    </div>
  </section>
</template>
