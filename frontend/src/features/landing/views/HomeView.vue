<script setup lang="ts">
import {
	ArrowRightIcon,
	CalculatorIcon,
	ChartLineIcon,
	ChefHatIcon,
	ScanBarcodeIcon,
	ShieldCheckIcon,
} from '@lucide/vue'
import { computed } from 'vue'

import LandingPreview from '@features/landing/components/LandingPreview.vue'
import LandingRecipes from '@features/landing/components/LandingRecipes.vue'
import LandingStats from '@features/landing/components/LandingStats.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'

const auth = useAuthStore()

// Signed-in users already have an account, so the call to action leads to their overview
const cta = computed(() =>
	auth.isLoggedIn
		? { routeName: 'dashboard', label: 'Zur Übersicht' }
		: { routeName: 'auth-register', label: 'Kostenlos loslegen' },
)

const FEATURES = [
	{
		icon: ScanBarcodeIcon,
		title: 'Scannen statt suchen',
		text: 'Kamera auf den Strichcode, fertig. Über hunderttausend Lebensmittel aus Deutschland, Österreich und der Schweiz.',
	},
	{
		icon: CalculatorIcon,
		title: 'Dein Bedarf, nachvollziehbar',
		text: 'Der Kalorienrechner zeigt jeden Posten einzeln: Grundumsatz, Alltag, Training. Kein Wert aus dem Nichts.',
	},
	{
		icon: ChefHatIcon,
		title: 'Rezepte mit Nährwerten',
		text: 'Gesunde Alternativen zu deinen Lieblingsgerichten, gefiltert nach Ernährung, Unverträglichkeiten und Küchengeräten.',
	},
	{
		icon: ChartLineIcon,
		title: 'Gewicht im Blick',
		text: 'Wochenschnitt statt Tagesschwankung. So siehst du, ob es in die richtige Richtung geht.',
	},
]
</script>

<template>
	<main class="content-wrapper flex flex-col gap-16 pt-4 pb-16 md:gap-24 md:pt-6">
		<!-- Hero: what nibble is, one action. The preview shows a day in the app. -->
		<section
			class="card card--lg card--inverse grid grid-cols-12 items-center gap-10 px-6 py-10 sm:px-10 md:py-14 xl:px-14"
			aria-labelledby="landing-title"
		>
			<div class="flex flex-col items-start gap-6 col-span-12 lg:col-span-6">
				<p class="px-3 py-1 rounded-full bg-lime text-sm font-bold text-ink">
					Ernährungstagebuch &amp; Rezepte
				</p>

				<h1
					id="landing-title"
					class="text-white"
				>
					Iss gut. Wir rechnen mit.
				</h1>

				<p class="max-w-xl text-lg md:text-xl">
					nibble zeigt dir jeden Tag, wie viel du gegessen hast und was noch übrig ist.
					Lebensmittel scannst du einfach ein, Rezepte bringen die Nährwerte gleich mit.
				</p>

				<!-- Stacked at full width on phones, so neither label has to wrap -->
				<div class="flex flex-col gap-3 w-full sm:flex-row sm:flex-wrap sm:w-auto">
					<BaseButton
						variant="secondary"
						size="lg"
						:route-name="cta.routeName"
					>
						{{ cta.label }}
						<BaseIcon :icon="ArrowRightIcon" />
					</BaseButton>

					<BaseButton
						variant="outline"
						size="lg"
						route-name="recipe-list"
					>
						Rezepte ansehen
					</BaseButton>
				</div>

				<p
					v-if="!auth.isLoggedIn"
					class="text-sm text-on-forest-muted"
				>
					Kostenlos. In zwei Minuten eingerichtet.
				</p>
			</div>

			<LandingPreview class="col-span-12 lg:col-span-6" />
		</section>

		<LandingStats />

		<section
			class="flex flex-col gap-8"
			aria-labelledby="landing-features-title"
		>
			<div class="flex flex-col gap-2 max-w-2xl">
				<h2 id="landing-features-title">Alles, was du brauchst. Nicht mehr.</h2>

				<p class="text-lg text-ink-soft">
					Kein Punktesystem, keine Verbote. Nur ehrliche Zahlen und Werkzeuge, die dir
					Arbeit abnehmen.
				</p>
			</div>

			<ul class="grid grid-cols-12 gap-4">
				<li
					v-for="feature in FEATURES"
					:key="feature.title"
					class="flex flex-col gap-3 col-span-12 p-6 rounded-lg bg-surface sm:col-span-6 md:p-8"
				>
					<span
						class="grid place-items-center size-12 rounded-md bg-brand-soft text-brand-ink"
					>
						<BaseIcon
							:icon="feature.icon"
							:size="24"
						/>
					</span>

					<h3>{{ feature.title }}</h3>

					<p class="text-ink-soft">{{ feature.text }}</p>
				</li>
			</ul>

			<!-- Privacy gets its own band: for a food diary it is a reason to sign up, not small print -->
			<div
				class="flex flex-col gap-4 p-6 rounded-lg border-2 border-divider sm:flex-row sm:items-center md:p-8"
			>
				<span class="grid place-items-center shrink-0 size-12 rounded-md bg-lime text-ink">
					<BaseIcon
						:icon="ShieldCheckIcon"
						:size="24"
					/>
				</span>

				<p class="text-ink-soft">
					<strong class="text-ink">Deine Daten gehören dir.</strong>
					Getrackt wird nur mit deiner Einwilligung. Du kannst alles jederzeit exportieren
					oder löschen, und die Kamera liest Barcodes direkt auf deinem Gerät.
				</p>
			</div>
		</section>

		<LandingRecipes />

		<!-- Closing call to action, same target as in the hero -->
		<section
			class="flex flex-col items-start gap-6 px-6 py-10 rounded-xl bg-lime sm:px-10 md:flex-row md:items-center md:justify-between md:py-12 xl:px-14"
			aria-labelledby="landing-cta-title"
		>
			<div class="flex flex-col gap-2">
				<h2 id="landing-cta-title">
					{{ auth.isLoggedIn ? 'Schön, dass du da bist.' : 'Bereit für den ersten Tag?' }}
				</h2>

				<p class="text-lg">
					{{
						auth.isLoggedIn
							? 'Dein Tagebuch wartet in der Übersicht.'
							: 'Konto anlegen, Ziel festlegen, erstes Frühstück scannen.'
					}}
				</p>
			</div>

			<BaseButton
				class="shrink-0"
				size="lg"
				:route-name="cta.routeName"
			>
				{{ auth.isLoggedIn ? cta.label : 'Konto erstellen' }}
				<BaseIcon :icon="ArrowRightIcon" />
			</BaseButton>
		</section>
	</main>
</template>
