<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  kcalPerServing: number
  proteinPerServing: number
  carbsPerServing: number
  fatPerServing: number
}

interface Macro {
  id: string
  label: string
  grams: number
  share: number
  dotClass: string
  barClass: string
}

const props = defineProps<Props>()

const macros = computed<Macro[]>(() => [
  {
    id: 'protein',
    label: 'Eiweiß',
    grams: props.proteinPerServing,
    share: props.proteinPerServing * 4,
    dotClass: 'before:bg-macro-protein',
    barClass: 'bg-macro-protein',
  },
  {
    id: 'carbs',
    label: 'Kohlenhydrate',
    grams: props.carbsPerServing,
    share: props.carbsPerServing * 4,
    dotClass: 'before:bg-macro-carbs',
    barClass: 'bg-macro-carbs',
  },
  {
    id: 'fat',
    label: 'Fett',
    grams: props.fatPerServing,
    share: props.fatPerServing * 9,
    dotClass: 'before:bg-macro-fat',
    barClass: 'bg-macro-fat',
  },
])
</script>

<template>
  <section
    aria-labelledby="nutrition-heading"
    class="flex flex-col gap-4 py-5 border-y md:gap-5 md:py-6"
  >
    <h2
      id="nutrition-heading"
      class="sr-only"
    >
      Nährwerte pro Portion
    </h2>

    <dl class="flex flex-col gap-4 md:flex-row md:items-end md:gap-6">
      <div class="pb-4 border-b md:shrink-0 md:pr-8 md:pb-0 md:border-r md:border-b-0">
        <dt class="text-sm text-muted-foreground">Pro Portion</dt>

        <dd class="text-3xl leading-none font-semibold tracking-tight tabular-nums lg:text-4xl">
          {{ props.kcalPerServing }} kcal
        </dd>
      </div>

      <div class="flex flex-1 flex-col gap-3 min-w-0 md:flex-row md:gap-7 lg:gap-10">
        <div
          v-for="macro in macros"
          :key="macro.id"
          class="flex items-baseline justify-between gap-3 md:flex-1 md:flex-col md:items-start md:gap-1 md:min-w-0"
        >
          <dt
            :class="[
              'flex items-center gap-1.5 text-sm text-muted-foreground before:size-2 before:rounded-full',
              macro.dotClass,
            ]"
          >
            {{ macro.label }}
          </dt>

          <dd class="text-lg leading-none font-semibold tabular-nums md:text-2xl lg:text-3xl">
            {{ macro.grams }} g
          </dd>
        </div>
      </div>
    </dl>

    <div
      aria-hidden="true"
      class="flex h-1.5 rounded-full bg-muted overflow-hidden"
    >
      <div
        v-for="macro in macros"
        :key="macro.id"
        :class="macro.barClass"
        :style="{ flexGrow: macro.share }"
      />
    </div>
  </section>
</template>
