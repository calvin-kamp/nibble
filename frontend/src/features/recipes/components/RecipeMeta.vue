<script setup lang="ts">
import type { LucideIcon } from '@lucide/vue'
import type { Equipment, MealType } from '../recipes.types'

import { ClockIcon, CookingPotIcon, UtensilsIcon } from '@lucide/vue'
import { computed } from 'vue'
import { UiIcon } from '@components/ui'

interface Props {
  durationMinutes: number
  mealTypes: MealType[]
  equipment: Equipment[]
}

interface MetaEntry {
  id: string
  icon: LucideIcon
  label: string
  values: string[]
}

const props = defineProps<Props>()

const entries = computed<MetaEntry[]>(() => {
  const list: MetaEntry[] = [
    {
      id: 'duration',
      icon: ClockIcon,
      label: 'Dauer',
      values: [`${props.durationMinutes} Minuten`],
    },
  ]

  if (props.mealTypes.length > 0) {
    list.push({ id: 'meal-types', icon: UtensilsIcon, label: 'Mahlzeit', values: props.mealTypes })
  }

  if (props.equipment.length > 0) {
    list.push({
      id: 'equipment',
      icon: CookingPotIcon,
      label: 'Ausstattung',
      values: props.equipment,
    })
  }

  return list
})
</script>

<template>
  <dl class="flex flex-col gap-3 md:flex-row md:flex-wrap md:gap-x-7 md:gap-y-3">
    <div
      v-for="entry in entries"
      :key="entry.id"
      class="flex gap-2.5"
    >
      <UiIcon
        :icon="entry.icon"
        :size="20"
        class="mt-0.5 text-muted-foreground"
      />

      <div>
        <dt class="text-sm text-muted-foreground">{{ entry.label }}</dt>

        <dd class="flex gap-1 font-medium">
          <span
            v-for="value in entry.values"
            :key="value"
            class="after:content-[','] last:after:content-none"
          >
            {{ value }}
          </span>
        </dd>
      </div>
    </div>
  </dl>
</template>
