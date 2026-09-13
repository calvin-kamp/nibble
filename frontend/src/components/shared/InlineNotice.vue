<script setup lang="ts">
import { InfoIcon, TriangleAlertIcon } from '@lucide/vue'
import { computed } from 'vue'
import { cn } from '@/lib/utils'
import LucideIcon from './LucideIcon.vue'

interface Props {
  variant?: 'info' | 'warning'
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  title: undefined,
})

const isWarning = computed<boolean>(() => props.variant === 'warning')
</script>

<template>
  <div
    :class="
      cn(
        'flex gap-3 rounded-xl border p-4 text-sm',
        isWarning
          ? 'border-destructive/30 bg-destructive/8'
          : 'border-border bg-muted text-muted-foreground',
      )
    "
  >
    <LucideIcon
      :icon="isWarning ? TriangleAlertIcon : InfoIcon"
      :size="18"
      :class="cn('mt-0.5 shrink-0', isWarning && 'text-destructive')"
    />

    <p>
      <span class="sr-only">{{ isWarning ? 'Warnung:' : 'Hinweis:' }}</span>

      <strong
        v-if="props.title"
        :class="cn('block', isWarning && 'text-destructive')"
      >
        {{ props.title }}
      </strong>

      <slot />
    </p>
  </div>
</template>
