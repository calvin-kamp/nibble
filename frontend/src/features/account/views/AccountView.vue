<script setup lang="ts">
import type { AccountZone } from '@features/account/account.types'
import type { SelectOption } from '@shared/ui/types'

import { IdCardIcon, SaladIcon, ShieldCheckIcon, TrashIcon, UserRoundIcon } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { BaseIcon, BaseSelect } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'

const ZONES: AccountZone[] = [
	{ routeName: 'account-profile', title: 'Anmeldedaten', icon: UserRoundIcon },
	{ routeName: 'account-personal', title: 'Persönliches', icon: IdCardIcon },
	{ routeName: 'account-nutrition', title: 'Ernährung', icon: SaladIcon },
	{ routeName: 'account-privacy', title: 'Datenschutz', icon: ShieldCheckIcon },
	{ routeName: 'account-delete', title: 'Konto löschen', icon: TrashIcon, danger: true },
]

const ZONE_OPTIONS: SelectOption[] = ZONES.map((zone) => ({
	value: zone.routeName,
	label: zone.title,
}))

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const initial = computed<string>(() =>
	(auth.user?.username ?? auth.user?.email ?? '?').charAt(0).toUpperCase(),
)

const currentZone = computed<string | undefined>({
	get: () => (typeof route.name === 'string' ? route.name : undefined),
	set: (routeName) => {
		if (routeName && routeName !== route.name) router.push({ name: routeName })
	},
})
</script>

<template>
	<main class="page">
		<div class="page__header">
			<h1>
				Einstellungen
			</h1>
		</div>

		<div class="grid grid-cols-12 gap-y-6 xl:items-start xl:gap-x-10">
			<nav
				class="flex flex-col gap-5 col-span-12 xl:col-span-3"
				aria-label="Bereiche der Einstellungen"
			>
				<div class="field md:max-w-sm xl:hidden">
					<label
						for="account-zone"
						class="field__label"
					>
						Bereich
					</label>

					<BaseSelect
						id="account-zone"
						v-model="currentZone"
						:options="ZONE_OPTIONS"
					/>
				</div>

				<p class="flex items-center gap-3 max-xl:hidden">
					<span
						class="grid place-items-center shrink-0 size-12 rounded-full bg-forest font-display text-xl font-bold text-highlight"
						aria-hidden="true"
					>
						{{ initial }}
					</span>

					<span class="flex flex-col min-w-0">
						<span class="font-semibold truncate">
							{{
								auth.user?.username ?? 'Dein Konto'
							}}
						</span>

						<span class="text-md text-muted-foreground truncate">
							{{
								auth.user?.email
							}}
						</span>
					</span>
				</p>

				<ul class="flex flex-col gap-1 max-xl:hidden">
					<li
						v-for="zone in ZONES"
						:key="zone.routeName"
					>
						<RouterLink
							:to="{ name: zone.routeName }"
							class="sidebar__link"
							:class="{
								'sidebar__link--active': route.name === zone.routeName,
								'sidebar__link--danger': zone.danger,
							}"
							:aria-current="route.name === zone.routeName ? 'page' : undefined"
						>
							<BaseIcon :icon="zone.icon" />

							{{ zone.title }}
						</RouterLink>
					</li>
				</ul>
			</nav>

			<RouterView class="col-span-12 min-w-0 xl:col-span-9 xl:max-w-3xl" />
		</div>
	</main>
</template>
