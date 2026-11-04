<script setup lang="ts">
import HelpContact from '@features/help/components/HelpContact.vue'
import { BaseBreadcrumb, BaseLink } from '@shared/ui'

import { ACCESSIBILITY_EMAIL } from '@shared/constants'

// What nibble does for accessibility and where it still has limits. Only what the app really
// does; when a part changes, change its line here as well.
const MEASURES = [
	{
		title: 'Tastatur',
		text: 'Alles lässt sich ohne Maus bedienen. Ein sichtbarer Rahmen zeigt, wo du gerade bist, und „Zum Inhalt springen“ führt an der Navigation vorbei.',
	},
	{
		title: 'Screenreader',
		text: 'Seitenwechsel werden angesagt, ebenso Meldungen wie „Gespeichert“ oder die Zahl der gefundenen Rezepte. Schaltflächen, die nur ein Symbol zeigen, haben eine Beschriftung für Screenreader.',
	},
	{
		title: 'Lesbarkeit',
		text: 'Text ist nie kleiner als 16 Pixel, die Kontraste richten sich nach WCAG 2.2, Stufe AA. Neben Farben steht eine Beschriftung, zum Beispiel bei den Makros.',
	},
	{
		title: 'Bedienung am Handy',
		text: 'Schaltflächen und Links sind mindestens 44 × 44 Pixel groß, Links im Fließtext ausgenommen. Die Seiten funktionieren ab 320 Pixel Breite.',
	},
	{
		title: 'Formulare',
		text: 'Jedes Feld hat eine sichtbare Beschriftung. Fehler stehen direkt am Feld, und der Fokus springt beim Absenden zum ersten Fehler.',
	},
	{
		title: 'Bewegung',
		text: 'Hast du in deinem System reduzierte Bewegung eingestellt, erscheinen Dialoge und Menüs ohne Animation.',
	},
]

const LIMITS = [
	{
		title: 'Barcode-Scanner',
		text: 'Der Scanner braucht die Kamera und den Blick auf den Strichcode. Du kannst stattdessen die Zahl unter dem Strichcode eintippen oder das Lebensmittel nach Namen suchen.',
	},
	{
		title: 'Diagramme',
		text: 'Der Gewichtsverlauf ist ein Diagramm. Dieselben Werte stehen darunter als Liste der Einträge, die Ringe für Kalorien und Makros haben eine Textbeschreibung.',
	},
	{
		title: 'Rezeptfotos',
		text: 'Fotos laden die Autorinnen und Autoren der Rezepte hoch. Sie haben keine eigene Bildbeschreibung; der Name des Rezepts steht direkt daneben.',
	},
]
</script>

<template>
	<main class="page page--compact">
		<BaseBreadcrumb
			:items="[{ label: 'Hilfe', routeName: 'help' }]"
			current="Barrierefreiheit"
		/>

		<div class="page__header">
			<div class="page__intro">
				<h1>
					Barrierefreiheit
				</h1>

				<p class="page__lead">
					nibble soll für alle gut nutzbar sein, auch mit Screenreader, Tastatur oder
					vergrößerter Schrift. Wir orientieren uns an den Richtlinien WCAG 2.2, Stufe AA.
				</p>
			</div>
		</div>

		<div class="content-column content-column--narrow gap-12">
			<section
				class="section"
				aria-labelledby="a11y-measures-title"
			>
				<h2 id="a11y-measures-title">
					Was nibble dafür tut
				</h2>

				<dl class="a11y-list">
					<div
						v-for="item in MEASURES"
						:key="item.title"
						class="a11y-list__item"
					>
						<dt class="a11y-list__title">
							{{ item.title }}
						</dt>

						<dd class="a11y-list__text">
							{{ item.text }}
						</dd>
					</div>
				</dl>
			</section>

			<section
				class="section"
				aria-labelledby="a11y-limits-title"
			>
				<div class="section__intro">
					<h2 id="a11y-limits-title">
						Wo es noch Grenzen gibt
					</h2>

					<p class="section__lead">
						Nicht alles ist für jede Situation gelöst. Hier steht, was wir wissen, und
						wie du trotzdem ans Ziel kommst.
					</p>
				</div>

				<dl class="a11y-list">
					<div
						v-for="item in LIMITS"
						:key="item.title"
						class="a11y-list__item"
					>
						<dt class="a11y-list__title">
							{{ item.title }}
						</dt>

						<dd class="a11y-list__text">
							{{ item.text }}
						</dd>
					</div>
				</dl>
			</section>

			<section
				class="section"
				aria-labelledby="a11y-report-title"
			>
				<div class="section__intro">
					<h2 id="a11y-report-title">
						Barriere gefunden?
					</h2>

					<p class="section__lead">
						Schreib uns an

						<BaseLink
							:href="`mailto:${ACCESSIBILITY_EMAIL}`"
							variant="inline"
						>
							{{ ACCESSIBILITY_EMAIL }}
						</BaseLink>, wo du nicht weiterkommst und mit welchem Gerät oder Hilfsmittel du nibble
						nutzt. Mehr zu den Daten, die wir dabei speichern, steht in der

						<BaseLink
							route-name="legal-privacy"
							variant="inline"
						>
							Datenschutzerklärung
						</BaseLink>.
					</p>
				</div>
			</section>

			<HelpContact />
		</div>
	</main>
</template>
