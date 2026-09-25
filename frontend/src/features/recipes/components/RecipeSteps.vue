<script setup lang="ts">
import type { CookingStep } from '../recipes.types'

interface Props {
  cookingSteps: CookingStep[]
}

const props = defineProps<Props>()
</script>

<template>
  <section
    aria-labelledby="preparation-heading"
    class="flex flex-col gap-6 min-w-0"
  >
    <h2
      id="preparation-heading"
      class="border-b pb-4"
    >
      Zubereitung
    </h2>

    <ol class="flex flex-col gap-6">
      <li
        v-for="cookingStep in props.cookingSteps"
        :key="cookingStep.step"
        class="flex gap-4"
      >
        <span
          aria-hidden="true"
          class="shrink-0 w-7 text-right font-semibold text-muted-foreground tabular-nums"
        >
          {{ cookingStep.step }}
        </span>

        <p class="max-w-prose">
          {{ cookingStep.text }}
        </p>
      </li>
    </ol>
  </section>
</template>
