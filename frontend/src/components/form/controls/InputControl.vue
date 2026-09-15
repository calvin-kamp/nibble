<script setup lang="ts">
defineOptions({ inheritAttrs: false })

const modelValue = defineModel<string | number>()
</script>

<template>
  <div
    :class="[
      'flex items-center gap-2 w-full min-w-0 h-11 px-4',
      'bg-input/30 border border-input rounded-md',
      'transition-interactive has-[input:focus-visible]:focus-ring',
      'has-aria-invalid:border-destructive has-aria-invalid:has-[input:focus-visible]:focus-ring-destructive',
      'has-[input:disabled]:inactive',
    ]"
  >
    <span
      v-if="$slots.leading"
      class="text-muted-foreground"
    >
      <slot name="leading" />
    </span>

    <input
      v-bind="$attrs"
      v-model="modelValue"
      class="min-w-0 flex-1 bg-transparent outline-hidden text-base placeholder:text-muted-foreground"
    />

    <span
      v-if="$slots.trailing"
      class="text-muted-foreground"
    >
      <slot name="trailing" />
    </span>
  </div>
</template>
