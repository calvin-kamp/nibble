<script setup lang="ts">
import { useId } from 'vue'
import { UiIcon } from '@components/ui'
import { benefitPanel } from '../auth.data'

const titleId = useId()
</script>

<template>
  <aside
    :aria-labelledby="titleId"
    class="relative isolate after:absolute after:inset-y-[-100vh] after:left-[-100vw] after:right-0 after:-z-10 after:bg-muted"
  >
    <div class="flex flex-col gap-10 py-6">
      <h2
        :id="titleId"
        class="text-xl md:text-2xl"
      >
        {{ benefitPanel.title }}
      </h2>

      <ul class="flex flex-col gap-5 max-w-prose">
        <li
          v-for="benefit in benefitPanel.benefits"
          :key="benefit.text"
          class="flex items-start gap-3"
        >
          <UiIcon
            :icon="benefit.icon"
            :size="20"
            class="mt-0.5 text-primary"
          />

          <span>
            {{ benefit.text }}
          </span>
        </li>
      </ul>
    </div>
  </aside>
</template>
