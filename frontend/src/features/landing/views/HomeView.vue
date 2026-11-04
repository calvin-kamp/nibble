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
		text: '7-Tage-Schnitt statt Tagesschwankung. So siehst du, ob es in die richtige Richtung geht.',
	},
]
</script>

<template>
	<main class="landing">
		<section
			class="landing__hero on-forest"
			aria-labelledby="landing-title"
		>
			<div class="landing__hero-text">
				<h1
					id="landing-title"
					class="landing__title"
				>
					Iss gut. <br />

					Wir rechnen mit.
				</h1>

				<p class="landing__lead">
					<strong class="block mb-2 text-highlight">
						Ernährungstagebuch &amp; Rezepte
					</strong>

					nibble zeigt dir jeden Tag, wie viel du gegessen hast und was noch übrig ist.
					Lebensmittel scannst du einfach ein, Rezepte bringen die Nährwerte gleich mit.
				</p>

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
					class="text-md text-forest-muted-foreground"
				>
					Kostenlos. In zwei Minuten eingerichtet.
				</p>
			</div>

			<LandingPreview class="landing__hero-preview" />
		</section>

		<LandingStats />

		<section
			class="landing__features"
			aria-labelledby="landing-features-title"
		>
			<div class="landing__features-intro">
				<div class="flex flex-col gap-3">
					<h2 id="landing-features-title">
						Alles, was du brauchst. Nicht mehr.
					</h2>

					<p class="text-lg text-foreground/80">
						Kein Punktesystem, keine Verbote. Nur ehrliche Zahlen und Werkzeuge, die dir
						Arbeit abnehmen.
					</p>
				</div>

				<div class="landing__privacy">
					<span
						class="landing__privacy-icon"
						aria-hidden="true"
					>
						<BaseIcon :icon="ShieldCheckIcon" />
					</span>

					<p class="text-lg text-foreground/80">
						<strong class="landing__privacy-title">
							Deine Daten gehören dir.
						</strong>

						Gewicht, Körperdaten und Tagebuch speichern wir nur mit deiner Einwilligung.
						Du kannst alles jederzeit exportieren oder löschen, und die Kamera liest
						Barcodes direkt auf deinem Gerät.
					</p>
				</div>
			</div>

			<ul class="landing__feature-list">
				<li
					v-for="feature in FEATURES"
					:key="feature.title"
					class="landing__feature"
				>
					<span
						class="landing__feature-icon"
						aria-hidden="true"
					>
						<BaseIcon :icon="feature.icon" />
					</span>

					<div class="flex flex-col gap-2">
						<h3>
							{{ feature.title }}
						</h3>

						<p class="text-foreground/80">
							{{ feature.text }}
						</p>
					</div>
				</li>
			</ul>
		</section>

		<LandingRecipes />

		<section
			class="landing__cta"
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
