<script setup lang="ts">
import type { AuthNotice } from '@interfaces/auth.types'

import { watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@stores/auth.store'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

watch(
  () => auth.sessionExpired,
  async (expired) => {
    if (!expired) return

    auth.acknowledgeSessionExpired()

    if (!route.meta.requiresAuth) return

    const notice: AuthNotice = 'session-expired'

    await router.push({ name: 'auth-login', query: { redirect: route.fullPath, notice } })
  },
)
</script>

<template>
  <RouterView />
</template>
