<script setup lang="ts">
import { ArrowRightIcon, LifeBuoyIcon } from '@lucide/vue'

import { BaseButton, BaseIcon } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'

const auth = useAuthStore()
</script>

<template>
	<main class="page not-found">
		<span
			class="not-found__icon"
			aria-hidden="true"
		>
			<BaseIcon
				:icon="LifeBuoyIcon"
				:size="72"
			/>
		</span>

		<div class="not-found__intro">
			<h1 class="not-found__title">
				Hoppla, diese Seite gibt es nicht.
			</h1>

			<p class="not-found__text">
				Vielleicht ist der Link schon älter oder ein Buchstabe ist verrutscht. Kein Problem:
				Von hier aus findest du schnell zurück.
			</p>
		</div>

		<div class="flex flex-col gap-3 w-full sm:flex-row sm:justify-center sm:w-auto">
			<BaseButton
				size="lg"
				:route-name="auth.isLoggedIn ? 'dashboard' : 'home'"
			>
				{{ auth.isLoggedIn ? 'Zur Übersicht' : 'Zur Startseite' }}

				<BaseIcon :icon="ArrowRightIcon" />
			</BaseButton>

			<BaseButton
				variant="outline"
				size="lg"
				route-name="recipe-list"
			>
				Rezepte entdecken
			</BaseButton>
		</div>
	</main>
</template>
