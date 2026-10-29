<script setup lang="ts">
import PolicySection from '@features/legal/components/PolicySection.vue'
import { BaseLink } from '@shared/ui'

import { MIN_AGE, OPERATOR, TERMS_VERSION } from '@features/legal/legal.constants'
import { formatLongDate, parseIsoDate } from '@shared/utils/date'

// Terms of use for the free service: accounts, user recipes, health notice and liability
const SECTIONS = {
	scope: { id: 'geltungsbereich', title: '1. Geltungsbereich' },
	service: { id: 'leistungen', title: '2. Leistungen von Nibble' },
	health: { id: 'gesundheit', title: '3. Keine medizinische Beratung' },
	account: { id: 'konto', title: '4. Registrierung und Konto' },
	recipes: { id: 'rezepte', title: '5. Eigene Rezepte und Bilder' },
	conduct: { id: 'regeln', title: '6. Verbotene Inhalte und Nutzung' },
	foods: { id: 'lebensmitteldaten', title: '7. Lebensmitteldaten' },
	liability: { id: 'haftung', title: '8. Haftung' },
	termination: { id: 'kuendigung', title: '9. Kündigung und Löschung' },
	changes: { id: 'aenderungen', title: '10. Änderungen dieser Bedingungen' },
	final: { id: 'schlussbestimmungen', title: '11. Schlussbestimmungen' },
}

const revisionLabel = formatLongDate(parseIsoDate(TERMS_VERSION)!)
</script>

<template>
	<main class="content-wrapper pt-6 pb-10">
		<article class="legal">
			<div class="legal__header">
				<h1>Nutzungs&shy;bedingungen (AGB)</h1>

				<p class="font-bold">
					Stand: <time :datetime="TERMS_VERSION">{{ revisionLabel }}</time>
				</p>
			</div>

			<PolicySection :section="SECTIONS.scope">
				<p>
					Diese Bedingungen gelten für die Nutzung der Webanwendung Nibble unter
					{{ OPERATOR.website }}. Anbieter ist {{ OPERATOR.name }}, {{ OPERATOR.street }},
					{{ OPERATOR.postalCode }} {{ OPERATOR.city }} (im Folgenden „wir“). Mit dem
					Erstellen eines Kontos erkennst du diese Bedingungen an.
				</p>

				<p>
					Wie wir mit deinen Daten umgehen, steht in der

					<BaseLink
						route-name="legal-privacy"
						variant="inline"
					>
						Datenschutzerklärung
					</BaseLink>

					.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.service">
				<p>
					Nibble ist kostenlos. Ohne Konto kannst du Rezepte ansehen und den
					Kalorienrechner nutzen. Mit Konto kommen unter anderem das Ernährungstagebuch,
					der Gewichtsverlauf, eigene Mahlzeiten und eigene Rezepte dazu.
				</p>

				<p>
					Einen Anspruch auf bestimmte Funktionen oder eine ständige Verfügbarkeit gibt es
					nicht. Wir entwickeln Nibble weiter und können Funktionen ändern, ergänzen oder
					einstellen. Wartungen kündigen wir nach Möglichkeit vorher an.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.health">
				<p>
					Kalorienbedarf, Makronährstoffe und Nährwerte in Nibble sind Schätzungen zur
					Orientierung. Sie ersetzen keine ärztliche oder ernährungsfachliche Beratung.
				</p>

				<p>
					Bist du schwanger oder stillst, hast du eine Erkrankung, nimmst Medikamente, die
					den Stoffwechsel beeinflussen, oder hast du eine Essstörung oder hattest eine,
					sprich bitte vor einer Ernährungsumstellung mit einer Ärztin oder einem Arzt.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.account">
				<p>
					Ein Konto darfst du ab {{ MIN_AGE }} Jahren anlegen. Jede Person darf nur ein
					Konto führen, und es ist nicht übertragbar.
				</p>

				<p>
					Halte dein Passwort geheim. Vermutest du, dass jemand anderes Zugriff auf dein
					Konto hat, ändere es sofort in den Einstellungen und schreib uns an
					<BaseLink
						:href="`mailto:${OPERATOR.email}`"
						variant="inline"
					>
						{{ OPERATOR.email }}</BaseLink
					>.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.recipes">
				<p>
					Du kannst eigene Rezepte mit Bildern einreichen. Du versicherst, dass du die
					Rechte an Text und Bildern hast und dass auf Bildern erkennbare Personen mit der
					Veröffentlichung einverstanden sind.
				</p>

				<p>
					Für freigegebene Rezepte räumst du uns ein einfaches, unentgeltliches, räumlich
					unbeschränktes Recht ein, Text und Bilder in Nibble zu speichern, öffentlich
					anzuzeigen und dafür technisch anzupassen, etwa Bilder zu verkleinern oder
					zuzuschneiden. Das Recht besteht auch nach der Löschung deines Kontos fort; das
					Rezept erscheint dann ohne Bezug zu dir. Deine Urheberrechte bleiben bei dir.
				</p>

				<p>
					Wir prüfen jedes Rezept und jede Änderung vor der Veröffentlichung. Einen
					Anspruch auf Freigabe gibt es nicht. Wir können Rezepte ablehnen oder entfernen,
					etwa wenn sie gegen diese Bedingungen verstoßen oder offensichtlich falsche
					Nährwerte enthalten.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.conduct">
				<p>Nicht erlaubt sind insbesondere:</p>

				<ul class="legal__list">
					<li>
						rechtswidrige, beleidigende, diskriminierende oder pornografische Inhalte,
					</li>

					<li>Werbung und Links zu kommerziellen Angeboten,</li>

					<li>
						Inhalte, die fremde Urheber-, Marken- oder Persönlichkeitsrechte verletzen,
					</li>

					<li>
						Rezepte oder Hinweise, die zu gesundheitsgefährdendem Essverhalten
						auffordern, etwa zu extremem Fasten oder sehr niedriger Kalorienzufuhr,
					</li>

					<li>
						automatisiertes Auslesen von Inhalten und Versuche, Sicherheitsmaßnahmen zu
						umgehen oder den Betrieb zu stören.
					</li>
				</ul>
			</PolicySection>

			<PolicySection :section="SECTIONS.foods">
				<p>
					Die Lebensmitteldaten stammen aus der freien Datenbank Open Food Facts, in die
					jede und jeder Daten eintragen kann. Wir sortieren offensichtlich fehlerhafte
					Werte aus, können aber nicht für die Richtigkeit jedes Produkts einstehen.
					Maßgeblich sind die Angaben auf der Verpackung.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.liability">
				<p>
					Wir haften unbeschränkt für Vorsatz und grobe Fahrlässigkeit, für Schäden aus
					der Verletzung von Leben, Körper oder Gesundheit sowie nach dem
					Produkthaftungsgesetz.
				</p>

				<p>
					Bei leichter Fahrlässigkeit haften wir nur, wenn wir eine wesentliche Pflicht
					verletzen, deren Erfüllung die Nutzung von Nibble überhaupt erst ermöglicht und
					auf deren Einhaltung du vertrauen darfst. Die Haftung ist dann auf den
					vorhersehbaren, typischen Schaden begrenzt. Im Übrigen ist die Haftung für
					leichte Fahrlässigkeit ausgeschlossen.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.termination">
				<p>
					Du kannst dein Konto jederzeit in den Einstellungen löschen. Wie die Löschung
					abläuft, steht in der Datenschutzerklärung.
				</p>

				<p>
					Wir können die Nutzung mit einer Frist von vier Wochen per E-Mail beenden. Bei
					schweren oder wiederholten Verstößen gegen diese Bedingungen können wir dein
					Konto sofort sperren oder löschen.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.changes">
				<p>
					Ändern sich Funktionen von Nibble oder rechtliche Anforderungen, passen wir
					diese Bedingungen an. Über Änderungen informieren wir dich mindestens vier
					Wochen vorher per E-Mail. Bist du nicht einverstanden, kannst du dein Konto bis
					dahin löschen.
				</p>
			</PolicySection>

			<PolicySection :section="SECTIONS.final">
				<p>
					Es gilt deutsches Recht unter Ausschluss des UN-Kaufrechts. Zwingende
					Verbraucherschutzvorschriften des Landes, in dem du lebst, bleiben unberührt.
				</p>

				<p>
					Ist eine Bestimmung unwirksam, bleiben die übrigen wirksam. Anbieterangaben
					findest du im

					<BaseLink
						route-name="legal-notice"
						variant="inline"
					>
						Impressum
					</BaseLink>

					.
				</p>
			</PolicySection>
		</article>
	</main>
</template>
