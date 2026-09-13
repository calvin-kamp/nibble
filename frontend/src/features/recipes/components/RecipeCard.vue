<script setup lang="ts">
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { focusRingCardLink, focusRingResetLink } from '@/lib/interactive-styles'
import { ClockIcon, FlameIcon, ImageIcon } from '@lucide/vue'
import { RouterLink } from 'vue-router'
import type { Recipe } from '../recipes.types'
import { Badge } from '@/components/ui/badge'
import { getRecipeBadgeSummary } from '../recipes.utils'

interface Props {
  recipe: Recipe
}

const props = defineProps<Props>()
</script>

<template>
  <Card
    as="article"
    size="sm"
    :class="[
      focusRingCardLink,
      'relative h-full hover:border-ring hover:-translate-y-0.5 active:translate-0',
    ]"
  >
    <CardHeader class="flex items-stretch px-0 aspect-288/216">
      <img
        v-if="props.recipe.image"
        :src="props.recipe.image.src"
        :alt="props.recipe.image.alt"
      />
      <div
        v-else
        role="img"
        class="grid place-items-center w-full bg-[repeating-linear-gradient(45deg,transparent,transparent_10px,color-mix(in_oklab,var(--muted-foreground)_8%,transparent)_10px,color-mix(in_oklab,var(--muted-foreground)_8%,transparent)_20px)]"
      >
        <LucideIcon
          :icon="ImageIcon"
          :size="32"
        />
      </div>
    </CardHeader>

    <CardContent>
      <ul class="flex gap-2.5">
        <li
          v-for="(badge, index) in getRecipeBadgeSummary(recipe).badges"
          :key="index"
        >
          <Badge :variant="badge.variant">
            {{ badge.label }}
          </Badge>
        </li>

        <li v-if="getRecipeBadgeSummary(recipe).hiddenCount > 0">
          <Badge variant="outline"> +{{ getRecipeBadgeSummary(recipe).hiddenCount }} </Badge>
        </li>
      </ul>
    </CardContent>

    <CardContent>
      <CardTitle
        as="h3"
        class="min-h-10"
      >
        <RouterLink
          data-slot="card-link"
          :to="{ name: 'calorie-calculator' }"
          :class="[focusRingResetLink, 'after:absolute after:inset-0']"
        >
          {{ props.recipe.name }}
        </RouterLink>
      </CardTitle>
    </CardContent>

    <CardFooter class="mt-auto">
      <ul class="flex gap-6">
        <li class="flex items-center gap-1.5 text-muted-foreground text-sm">
          <LucideIcon :icon="ClockIcon" />

          {{ props.recipe.durationMinutes }} Min
        </li>

        <li class="flex items-center gap-1.5 text-muted-foreground text-sm">
          <LucideIcon :icon="FlameIcon" />

          {{ props.recipe.kcalPerServing }} kcal / Portion
        </li>
      </ul>
    </CardFooter>
  </Card>
</template>
