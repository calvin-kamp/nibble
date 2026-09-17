<script setup lang="ts">
import type { UserMenuItem } from '@interfaces/navigation.types'

import { UserRoundIcon } from '@lucide/vue'
import { PopoverClose } from 'reka-ui'
import { RouterLink } from 'vue-router'
import { UiButton, UiIcon, UiPopover, UiSeparator } from '@components/ui'
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
  <UiPopover
    :trigger-icon="UserRoundIcon"
    trigger-label="Profil"
    sr-only-trigger-label
    align="end"
    title="Konto"
    :description="auth.user?.email"
  >
    <template #content>
      <UiSeparator />

      <template
        v-for="item of userMenu"
        :key="item.label"
      >
        <PopoverClose
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
        </PopoverClose>

        <PopoverClose
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
        </PopoverClose>
      </template>
    </template>
  </UiPopover>
</template>
