<script setup lang="ts">
import { ChevronDownIcon, LogOutIcon, SettingsIcon, UserRoundIcon } from '@lucide/vue'
import { PopoverClose, PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import { ref } from 'vue'

import { BaseIcon, BaseLink } from '@shared/ui'

import { useLogout } from '@features/auth/composables/logout'

import { useAuthStore } from '@features/auth/auth.store'

// Account in the desktop header: who is signed in, settings, sign out
const auth = useAuthStore()
const logout = useLogout()

const open = ref<boolean>(false)

async function onLogout(): Promise<void> {
	open.value = false
	await logout()
}
</script>

<template>
	<PopoverRoot v-model:open="open">
		<PopoverTrigger class="button button--outline">
			<BaseIcon :icon="UserRoundIcon" />

			{{ auth.user?.username ?? 'Konto' }}

			<BaseIcon
				:icon="ChevronDownIcon"
				:size="18"
			/>
		</PopoverTrigger>

		<PopoverPortal>
			<PopoverContent
				class="popover flex flex-col gap-2 p-2"
				align="end"
				:side-offset="8"
			>
				<p class="flex flex-col px-3 pt-2 pb-3 border-b border-divider">
					<span class="font-semibold">
						{{ auth.user?.username ?? 'Angemeldet' }}
					</span>

					<span class="text-sm text-muted break-all">
						{{ auth.user?.email }}
					</span>
				</p>

				<div class="flex flex-col gap-1">
					<!-- PopoverClose as wrapper: clicking an item closes the popover -->
					<PopoverClose as-child>
						<BaseLink
							route-name="account"
							variant="no-decoration"
							class="popover__item"
						>
							<BaseIcon :icon="SettingsIcon" />

							Einstellungen
						</BaseLink>
					</PopoverClose>

					<button
						type="button"
						class="popover__item text-danger"
						@click="onLogout"
					>
						<BaseIcon :icon="LogOutIcon" />

						Abmelden
					</button>
				</div>
			</PopoverContent>
		</PopoverPortal>
	</PopoverRoot>
</template>
