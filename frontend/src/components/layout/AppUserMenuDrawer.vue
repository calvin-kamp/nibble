<script setup lang="ts">
import type { UserMenuItem } from '@interfaces/navigation.types'

import { UserRoundIcon } from '@lucide/vue'
import { DrawerClose } from 'reka-ui'
import { RouterLink } from 'vue-router'
import { UiButton, UiDrawer, UiIcon, UiSeparator } from '@components/ui'
import { useLogout } from '@composables/logout'
import { userMenu } from '@data/user-menu.data'
import { useAuthStore } from '@stores/auth.store'

const auth = useAuthStore()

const { handleLogout } = useLogout()

function handleAction(action: UserMenuItem['action']): void {
  if (action === 'logout') handleLogout()
}
</script>

<template>
  <UiDrawer
    title="Konto"
    :description="auth.user?.email"
  >
    <template #trigger>
      <UiButton
        variant="ghost"
        class="flex flex-col gap-0 w-full h-16 px-0"
      >
        <UiIcon
          :icon="UserRoundIcon"
          :size="24"
        />

        <span class="sr-only md:not-sr-only"> Profil </span>
      </UiButton>
    </template>

    <template #content>
      <UiSeparator />

      <template
        v-for="item of userMenu"
        :key="item.label"
      >
        <DrawerClose
          v-if="item.routeName"
          as-child
        >
          <UiButton
            as-child
            :variant="item.variant"
            class="justify-start"
          >
            <RouterLink :to="{ name: item.routeName }">
              <UiIcon
                :icon="item.icon"
                :size="20"
              />

              {{ item.label }}
            </RouterLink>
          </UiButton>
        </DrawerClose>

        <DrawerClose
          v-else
          as-child
        >
          <UiButton
            :variant="item.variant"
            class="justify-start"
            @click="handleAction(item.action)"
          >
            <UiIcon
              :icon="item.icon"
              :size="20"
            />

            {{ item.label }}
          </UiButton>
        </DrawerClose>
      </template>
    </template>
  </UiDrawer>
</template>
