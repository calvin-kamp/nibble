<script setup lang="ts">
import { LogOutIcon, SettingsIcon, UserRoundIcon } from '@lucide/vue'
import { ref } from 'vue'

import { BaseButton, BaseDrawer, BaseIcon } from '@shared/ui'

import { useLogout } from '@features/auth/composables/logout'

// Account entry in the bottom navigation (phone, tablet). AccountMenu takes over on desktop.
const open = ref<boolean>(false)

const logout = useLogout()

async function onLogout(): Promise<void> {
	open.value = false
	await logout()
}
</script>

<template>
	<button
		type="button"
		class="nav-item"
		aria-label="Konto Menü öffnen"
		aria-haspopup="dialog"
		aria-controls="account-drawer"
		:aria-expanded="open"
		@click="open = true"
	>
		<BaseIcon
			:icon="UserRoundIcon"
			:size="24"
		/>

		<span class="sr-only md:not-sr-only"> Konto </span>
	</button>

	<BaseDrawer
		id="account-drawer"
		v-model:open="open"
		title="Konto"
	>
		<BaseButton
			variant="muted"
			size="lg"
			class="justify-start"
			route-name="account"
			@click="open = false"
		>
			<BaseIcon :icon="SettingsIcon" />

			Einstellungen
		</BaseButton>

		<BaseButton
			variant="danger"
			size="lg"
			class="justify-start"
			@click="onLogout"
		>
			<BaseIcon :icon="LogOutIcon" />

			Abmelden
		</BaseButton>
	</BaseDrawer>
</template>
