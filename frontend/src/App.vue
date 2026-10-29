<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'

import TrackingDialogs from '@features/tracking/components/TrackingDialogs.vue'
import AppBottomNav from '@layouts/AppBottomNav.vue'
import AppHeader from '@layouts/AppHeader.vue'
import AppSideBar from '@layouts/AppSideBar.vue'
import { BaseToaster } from '@shared/ui'

import { usePageAnnouncement } from '@shared/composables/page-title'

import { useAuthStore } from '@features/auth/auth.store'

const route = useRoute()
const auth = useAuthStore()
const announcement = usePageAnnouncement()

const navigation = computed(() => route.meta.navigation ?? 'full')

// Every view renders exactly one main. It gets focus without becoming part of the tab order.
function skipToContent(): void {
	const main = document.querySelector<HTMLElement>('main')

	if (!main) return

	main.tabIndex = -1
	main.focus()
}
</script>

<template>
	<a
		href="#"
		class="skip-link"
		@click.prevent="skipToContent"
		>Zum Inhalt springen</a
	>

	<AppSideBar v-if="navigation === 'full'" />

	<AppHeader
		v-if="navigation !== 'none'"
		:standalone="navigation === 'header'"
	/>

	<RouterView />

	<TrackingDialogs v-if="auth.isLoggedIn && auth.hasDataConsent" />

	<BaseToaster />

	<AppBottomNav v-if="navigation === 'full'" />

	<p
		class="sr-only"
		aria-live="polite"
	>
		{{ announcement }}
	</p>
</template>
