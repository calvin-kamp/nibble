<script setup lang="ts">
import { UiButton, UiDrawer, UiIcon, UiSeparator } from '@components/ui'
import { trackingMenu } from '@data/tracking-menu.data'
import { toRouteDate } from '@lib/date'
import { PlusIcon } from '@lucide/vue'
import { DrawerClose } from 'reka-ui'
import { RouterLink } from 'vue-router'
</script>

<template>
  <UiDrawer
    trigger-variant="default"
    trigger-size="icon-lg"
    :trigger-icon="PlusIcon"
    trigger-label="Eintrag hinzufügen"
    sr-only-trigger-label
    title="Was möchtest du eintragen?"
  >
    <template #content>
      <UiSeparator />

      <DrawerClose
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
      </DrawerClose>
    </template>
  </UiDrawer>
</template>
