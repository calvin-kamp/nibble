<script setup lang="ts">
import { useId } from 'vue'

interface Props {
  label: string
  description?: string
}

const props = defineProps<Props>()

const descriptionId = useId()
</script>

<template>
  <fieldset
    class="w-full min-w-0"
    :aria-describedby="props.description ? descriptionId : undefined"
  >
    <legend class="w-full text-lg font-semibold">
      {{ props.label }}
    </legend>

    <p
      v-if="props.description"
      :id="descriptionId"
      class="mt-2 text-muted-foreground text-sm"
    >
      {{ props.description }}
    </p>

    <div class="flex flex-col gap-6 mt-4">
      <slot />
    </div>
  </fieldset>
</template>
