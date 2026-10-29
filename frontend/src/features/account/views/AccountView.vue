<script setup lang="ts">
import type { AccountZone } from '@features/account/account.types'
import type { SelectOption } from '@shared/ui/types'

import { IdCardIcon, SaladIcon, ShieldCheckIcon, TrashIcon, UserRoundIcon } from '@lucide/vue'
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { BaseIcon, BaseSelect } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'

const ZONES: AccountZone[] = [
	{ routeName: 'account-profile', title: 'Konto', icon: UserRoundIcon },
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

// Phone and tablet: the areas sit in a select, and choosing one switches the page directly
const currentZone = computed<string | undefined>({
	get: () => (typeof route.name === 'string' ? route.name : undefined),
	set: (routeName) => {
		if (routeName && routeName !== route.name) router.push({ name: routeName })
	},
})
</script>

<template>
	<main class="content-wrapper flex flex-col gap-6 pt-6 pb-10">
		<h1>Einstellungen</h1>

		<div class="grid grid-cols-12 gap-6 xl:items-start xl:gap-10">
			<nav
				class="flex flex-col gap-5 col-span-12 xl:col-span-3"
				aria-label="Bereiche der Einstellungen"
			>
				<!-- Phone and tablet: a select saves the room a separate list would take before the content -->
				<div class="field md:max-w-sm xl:hidden">
					<label
						for="account-zone"
						class="field__label"
						>Bereich</label
					>

					<BaseSelect
						id="account-zone"
						v-model="currentZone"
						:options="ZONE_OPTIONS"
					/>
				</div>

				<!-- Desktop: who is signed in, plus the areas as a list -->
				<p class="flex items-center gap-3 max-xl:hidden">
					<span
						class="grid place-items-center shrink-0 size-12 rounded-full bg-forest font-display text-xl font-extrabold text-lime"
						aria-hidden="true"
					>
						{{ initial }}
					</span>

					<span class="flex flex-col min-w-0">
						<span class="font-semibold truncate">{{
							auth.user?.username ?? 'Dein Konto'
						}}</span>

						<span class="text-sm text-muted truncate">{{ auth.user?.email }}</span>
					</span>
				</p>

				<ul class="flex flex-col gap-1 max-xl:hidden">
					<li
						v-for="zone in ZONES"
						:key="zone.routeName"
					>
						<RouterLink
							:to="{ name: zone.routeName }"
							class="flex items-center gap-3 min-h-12 px-4 rounded-md font-semibold transition-interactive hover:bg-surface focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
							:class="{
								'text-danger': zone.danger && route.name !== zone.routeName,
								'bg-forest text-white hover:bg-forest':
									route.name === zone.routeName && !zone.danger,
								'bg-danger text-white hover:bg-danger':
									route.name === zone.routeName && zone.danger,
							}"
							:aria-current="route.name === zone.routeName ? 'page' : undefined"
						>
							<BaseIcon :icon="zone.icon" />
							{{ zone.title }}
						</RouterLink>
					</li>
				</ul>
			</nav>

			<!-- RouterView hands the classes on to the panel -->
			<RouterView class="col-span-12 min-w-0 xl:col-span-9 xl:max-w-3xl" />
		</div>
	</main>
</template>
