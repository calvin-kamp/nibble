<script setup lang="ts">
import { UiCard, UiSeparator } from '@components/ui'

interface Props {
  title: string
  description: string
}

const props = defineProps<Props>()
</script>

<template>
  <UiCard
    :title="props.title"
    title-as="h1"
    :description="props.description"
    class="w-full max-w-lg mx-auto py-0 overflow-visible bg-transparent ring-0 md:py-6 md:bg-card md:ring-1 lg:me-0"
    header-class="px-0 md:px-6"
    title-class="text-2xl font-bold tracking-tight md:text-3xl"
    description-class="text-base"
    content-class="flex flex-col gap-6 px-0 md:px-6"
    footer-class="justify-center px-0 md:px-6"
  >
    <slot />

    <UiSeparator />

    <template #footer>
      <p class="text-muted-foreground">
        <slot name="footer" />
      </p>
    </template>
  </UiCard>
</template>
