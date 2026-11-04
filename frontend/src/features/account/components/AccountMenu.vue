<script setup lang="ts">
import { ChevronsUpDownIcon, LogOutIcon, SettingsIcon } from '@lucide/vue'
import { PopoverClose, PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import { computed, ref } from 'vue'

import { BaseIcon, BaseLink } from '@shared/ui'

import { useLogout } from '@features/auth/composables/logout'

import { useAuthStore } from '@features/auth/auth.store'

const auth = useAuthStore()
const logout = useLogout()

const open = ref<boolean>(false)

const initial = computed<string>(() =>
	(auth.user?.username ?? auth.user?.email ?? '?').charAt(0).toUpperCase(),
)

async function onLogout(): Promise<void> {
	open.value = false
	await logout()
}
</script>

<template>
	<PopoverRoot v-model:open="open">
		<PopoverTrigger class="account-menu__trigger">
			<span
				class="account-menu__avatar"
				aria-hidden="true"
			>
				{{ initial }}
			</span>

			<span class="flex flex-col flex-1 min-w-0 text-left">
				<span class="font-semibold truncate">
					{{ auth.user?.username ?? 'Konto' }}
				</span>

				<span class="text-md text-muted-foreground truncate">
					{{ auth.user?.email }}
				</span>
			</span>

			<BaseIcon
				class="text-muted-foreground"
				:icon="ChevronsUpDownIcon"
				:size="18"
			/>
		</PopoverTrigger>

		<PopoverPortal>
			<PopoverContent
				class="popover account-menu__content flex flex-col gap-2 p-2"
				side="top"
				align="start"
				:side-offset="8"
			>
				<div class="flex flex-col gap-1">
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
						class="popover__item popover__item--danger"
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
