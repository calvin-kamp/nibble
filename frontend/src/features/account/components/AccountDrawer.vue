<script setup lang="ts">
import { LogOutIcon, UserRoundIcon } from '@lucide/vue'

import AppNavDrawer from '@layouts/AppNavDrawer.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { useLogout } from '@features/auth/composables/logout'

import { ACCOUNT_NAV } from '@layouts/navigation'

const logout = useLogout()

async function onLogout(close: () => void): Promise<void> {
	close()
	await logout()
}
</script>

<template>
	<AppNavDrawer
		id="account-drawer"
		label="Konto"
		:icon="UserRoundIcon"
		:items="ACCOUNT_NAV"
		:item-variants="[]"
		item-variant="muted"
	>
		<template #default="{ close }">
			<BaseButton
				variant="danger-soft"
				size="lg"
				class="justify-start"
				@click="onLogout(close)"
			>
				<BaseIcon :icon="LogOutIcon" />

				Abmelden
			</BaseButton>
		</template>
	</AppNavDrawer>
</template>
