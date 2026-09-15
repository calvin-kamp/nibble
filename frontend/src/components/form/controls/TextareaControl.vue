<script setup lang="ts">
const modelValue = defineModel<string>()
</script>

<template>
  <textarea
    v-model="modelValue"
    :class="[
      'w-full min-h-29 px-4 py-2 resize-y',
      'bg-input/30 border border-input rounded-md',
      'text-base',
      'placeholder:text-muted-foreground',
      'transition-interactive focus-visible:focus-ring',
      'aria-invalid:border-destructive aria-invalid:focus-visible:focus-ring-destructive',
      'disabled:inactive',
    ]"
  />
</template>
