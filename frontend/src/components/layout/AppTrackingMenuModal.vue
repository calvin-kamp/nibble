<script setup lang="ts">
import { UiButton, UiDialog, UiIcon, UiSeparator } from '@components/ui'
import { trackingMenu } from '@data/tracking-menu.data'
import { toRouteDate } from '@lib/date'
import { PlusIcon } from '@lucide/vue'
import { DialogClose } from 'reka-ui'
import { RouterLink } from 'vue-router'
</script>

<template>
  <UiDialog
    trigger-variant="default"
    :trigger-icon="PlusIcon"
    trigger-label="Eintrag hinzufügen"
    sr-only-trigger-label
    title="Was möchtest du eintragen?"
    description="Wähle aus, welche Art von Eintrag du anlegen möchtest."
    sr-only-description
  >
    <template #content>
      <UiSeparator />

      <DialogClose
        v-for="item of trackingMenu"
        :key="item.label"
        as-child
      >
        <UiButton
          as-child
          variant="ghost"
          class="justify-start"
        >
          <RouterLink :to="{ name: item.routeName, params: { date: toRouteDate() } }">
            <UiIcon
              :icon="item.icon"
              :size="20"
            />

            {{ item.label }}
          </RouterLink>
        </UiButton>
      </DialogClose>
    </template>
  </UiDialog>
</template>
