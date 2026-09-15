<script setup lang="ts">
interface Props {
  title?: string
  description?: string
}

const props = defineProps<Props>()
</script>

<template>
  <div
    class="flex flex-1 flex-col items-center justify-center gap-4 w-full min-w-0 p-8 md:p-12 border border-dashed rounded-lg text-center text-balance"
  >
    <div
      v-if="$slots.media"
      class="flex shrink-0 items-center justify-center text-muted-foreground"
    >
      <slot name="media" />
    </div>

    <div
      v-if="props.title || props.description || $slots.title || $slots.description"
      class="flex flex-col items-center gap-2 max-w-sm"
    >
      <p
        v-if="props.title || $slots.title"
        class="font-heading text-lg leading-snug font-medium"
      >
        <slot name="title">{{ props.title }}</slot>
      </p>

      <p
        v-if="props.description || $slots.description"
        class="text-muted-foreground text-sm"
      >
        <slot name="description">{{ props.description }}</slot>
      </p>
    </div>

    <div
      v-if="$slots.default"
      class="flex flex-col items-center gap-4 w-full max-w-sm min-w-0"
    >
      <slot />
    </div>
  </div>
</template>
