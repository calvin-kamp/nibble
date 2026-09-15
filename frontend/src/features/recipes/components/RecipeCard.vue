<script setup lang="ts">
import type { Recipe, RecipeBadgeSummary } from '../recipes.types'

import { getRecipeBadgeSummary, toSlug } from '../recipes.utils'
import { UiBadge, UiCard, UiIcon } from '@components/ui'
import { ClockIcon, FlameIcon, ImageIcon } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

interface Props {
  recipe: Recipe
}

const props = defineProps<Props>()

const badgeSummary = computed<RecipeBadgeSummary>(() => getRecipeBadgeSummary(props.recipe))
</script>

<template>
  <UiCard
    as="article"
    size="sm"
    title-as="h3"
    class="relative h-full hover:ring-ring has-[a:focus-visible]:focus-ring transition-interactive hover:-translate-y-0.5 active:translate-y-0"
    media-class="aspect-4/3 overflow-hidden"
  >
    <template #media>
      <img
        v-if="props.recipe.image"
        :src="props.recipe.image.src"
        :alt="props.recipe.image.alt"
        class="size-full object-cover"
      />

      <div
        v-else
        role="img"
        aria-label="Kein Bild vorhanden"
        class="grid size-full place-items-center bg-muted text-muted-foreground"
      >
        <UiIcon
          :icon="ImageIcon"
          :size="32"
        />
      </div>
    </template>

    <template #title>
      <RouterLink
        :to="{
          name: 'recipe-detail',
          params: { id: props.recipe.id, name: toSlug(props.recipe.name) },
        }"
        class="after:absolute after:inset-0 focus-visible:outline-hidden"
      >
        {{ props.recipe.name }}
      </RouterLink>
    </template>

    <ul class="flex flex-wrap gap-2">
      <li
        v-for="badge in badgeSummary.badges"
        :key="badge.label"
      >
        <UiBadge :variant="badge.variant">
          {{ badge.label }}
        </UiBadge>
      </li>

      <li v-if="badgeSummary.hiddenCount > 0">
        <UiBadge variant="outline">+{{ badgeSummary.hiddenCount }}</UiBadge>
      </li>
    </ul>

    <template #footer>
      <ul class="flex flex-wrap gap-x-6 gap-y-1">
        <li class="flex items-center gap-1.5 text-muted-foreground text-sm">
          <UiIcon :icon="ClockIcon" />

          {{ props.recipe.durationMinutes }} Min
        </li>

        <li class="flex items-center gap-1.5 text-muted-foreground text-sm">
          <UiIcon :icon="FlameIcon" />

          {{ props.recipe.kcalPerServing }} kcal / Portion
        </li>
      </ul>
    </template>
  </UiCard>
</template>
