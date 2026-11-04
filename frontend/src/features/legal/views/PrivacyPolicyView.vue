<script setup lang="ts">
import { useRoute } from 'vue-router'

import OperatorAddress from '@features/legal/components/OperatorAddress.vue'
import PolicySection from '@features/legal/components/PolicySection.vue'
import { BaseLink } from '@shared/ui'

import {
	MIN_AGE,
	OPERATOR,
	PRIVACY_POLICY_VERSION,
	PRIVACY_POLICY_SECTIONS,
} from '@features/legal/legal.constants'
import { formatLongDate, parseIsoDate } from '@shared/utils/date'
import { scrollToJumpMark } from '@shared/utils/scroll'

const route = useRoute()

const S = PRIVACY_POLICY_SECTIONS

const COOKIES = [
	{
		name: 'access_token',
		purpose: 'Anmeldung; nicht per JavaScript auslesbar (HttpOnly)',
		lifetime: '15 Minuten',
	},
	{
		name: 'refresh_token',
		purpose:
			'Erneuerung der Anmeldung; nicht per JavaScript auslesbar (HttpOnly), wird nur an die Anmeldeschnittstelle gesendet',
		lifetime: '7 Tage, verlängert sich bei Nutzung',
	},
	{
		name: 'csrftoken',
		purpose: 'Schutz vor gefälschten Anfragen (CSRF)',
		lifetime: 'bis zu 1 Jahr',
	},
	{
		name: 'sessionid',
		purpose: 'Anmeldung im Verwaltungsbereich, nur für Administratoren',
		lifetime: '2 Wochen',
	},
]

const revisionLabel = formatLongDate(parseIsoDate(PRIVACY_POLICY_VERSION)!)

// How many days the daily database backups are kept (sections 15 and 18)
const DATABASE_BACKUP_DAYS = 7
// How long the deletion log keeps an entry (DELETION_LOG_RETENTION in the backend)
const DELETION_LOG_DAYS = 30
</script>

<template>
	<main class="page">
		<article class="legal">
			<div class="legal__header">
				<h1>
					Datenschutzerklärung
				</h1>

				<p class="font-bold">
					Stand: <time :datetime="PRIVACY_POLICY_VERSION">
						{{ revisionLabel }}
					</time>
				</p>
			</div>

			<nav
				class="legal__toc"
				aria-labelledby="privacy-toc-title"
			>
				<h2
					id="privacy-toc-title"
					class="legal__toc-title"
				>
					Inhalt
				</h2>

				<ol class="legal__toc-list">
					<li
						v-for="section in S"
						:key="section.id"
					>
						<BaseLink
							route-name="legal-privacy"
							:hash="`#${section.id}`"
							@click="route.hash === `#${section.id}` && scrollToJumpMark(section.id)"
						>
							{{ section.title }}
						</BaseLink>
					</li>
				</ol>
			</nav>

			<PolicySection :section="S.general">
				<p>
					Der Schutz deiner personenbezogenen Daten ist uns wichtig. In dieser
					Datenschutzerklärung erfährst du, welche personenbezogenen Daten bei der Nutzung
					von Nibble verarbeitet werden, zu welchen Zwecken, auf welcher Rechtsgrundlage,
					wie lange sie gespeichert werden und welche Rechte du hast.
				</p>

				<p>
					Nibble ist eine Webanwendung zur Unterstützung der persönlichen
					Ernährungsplanung. Sie bietet unter anderem einen Kalorienrechner, ein
					Ernährungstagebuch, eine Gewichtsverlaufserfassung, eigene Mahlzeiten und eine
					Rezeptsammlung.
				</p>

				<p>
					Wir verarbeiten deine Daten im Einklang mit der Datenschutz-Grundverordnung
					(DSGVO), dem Bundesdatenschutzgesetz (BDSG) und dem
					Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz (TDDDG).
				</p>
			</PolicySection>

			<PolicySection :section="S.controller">
				<p>
					Verantwortlich für die Datenverarbeitung ist:
				</p>

				<OperatorAddress />

				<p>
					<strong>
						E-Mail:
					</strong>

					<BaseLink
						:href="`mailto:${OPERATOR.privacyEmail}`"
						variant="inline"
					>
						{{ OPERATOR.privacyEmail }}
					</BaseLink>

					<br />

					<strong>
						Website:
					</strong>

					<BaseLink
						:href="OPERATOR.website"
						variant="inline"
					>
						{{ OPERATOR.website }}
					</BaseLink>
				</p>
			</PolicySection>

			<PolicySection :section="S.hosting">
				<p>
					Nibble wird auf einem virtuellen Server (VPS) bei folgendem Anbieter betrieben:
				</p>

				<p class="legal__address">
					Hostinger International Ltd.<br />

					61 Lordou Vironos str.<br />

					6023 Larnaca<br />

					Zypern
				</p>

				<p>
					<strong>
						Serverstandort:
					</strong> Rechenzentrum in Düsseldorf, Deutschland.
				</p>

				<p>
					Mit Hostinger besteht ein Vertrag zur Auftragsverarbeitung gemäß Art. 28 DSGVO.
				</p>

				<p>
					Bei jedem Aufruf von Nibble werden technisch erforderliche Informationen in
					Serverprotokollen erfasst:
				</p>

				<ul class="legal__list">
					<li>
						IP-Adresse
					</li>

					<li>
						Datum und Uhrzeit des Zugriffs
					</li>

					<li>
						Aufgerufene Adresse (ohne Suchbegriffe und sonstige Parameter)
					</li>

					<li>
						HTTP-Statuscode und übertragene Datenmenge
					</li>

					<li>
						Referrer-URL, sofern übermittelt
					</li>

					<li>
						Browsertyp, Browserversion und Betriebssystem
					</li>
				</ul>

				<p>
					Die Verarbeitung dient der Bereitstellung von Nibble, der Gewährleistung der
					Systemsicherheit und der Fehleranalyse. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f
					DSGVO. Unser berechtigtes Interesse besteht im sicheren und zuverlässigen
					Betrieb der Anwendung.
				</p>

				<p>
					Die Serverprotokolle werden nach spätestens 14 Tagen gelöscht.
				</p>
			</PolicySection>

			<PolicySection :section="S.account">
				<p>
					Für das Speichern eigener Inhalte ist ein Benutzerkonto erforderlich. Dabei
					verarbeiten wir:
				</p>

				<ul class="legal__list">
					<li>
						E-Mail-Adresse
					</li>

					<li>
						Benutzername (wird anderen Nutzern nicht angezeigt)
					</li>

					<li>
						Passwort in gehashter Form; das Passwort selbst wird nicht gespeichert
					</li>

					<li>
						Status der E-Mail-Bestätigung
					</li>

					<li>
						Zeitpunkt der Registrierung und der letzten Anmeldung
					</li>

					<li>
						Stand des Onboardings
					</li>

					<li>
						Gegebenenfalls das Datum einer beantragten Kontolöschung
					</li>

					<li>
						Verlauf deiner Datenschutz-Einwilligungen: jeweils Entscheidung, Zeitpunkt
						und Version dieser Datenschutzerklärung
					</li>

					<li>
						Zeitpunkt und Version der AGB, die du bei der Registrierung akzeptiert und
						mit der Bestätigung deines Mindestalters abgegeben hast
					</li>
				</ul>

				<p>
					Die Verarbeitung der Kontodaten erfolgt zur Bereitstellung deines Kontos gemäß
					Art. 6 Abs. 1 lit. b DSGVO. Soweit Daten der Absicherung des Kontos dienen (zum
					Beispiel der Zeitpunkt der letzten Anmeldung), beruht dies auf Art. 6 Abs. 1
					lit. f DSGVO. Den Einwilligungsverlauf speichern wir, weil wir nachweisen
					müssen, dass und wann du eingewilligt hast (Art. 6 Abs. 1 lit. c DSGVO in
					Verbindung mit Art. 7 Abs. 1 DSGVO). Zeitpunkt und Version der AGB speichern wir
					als Nachweis deiner Zustimmung und deiner Altersbestätigung (Art. 6 Abs. 1 lit.
					b und lit. c DSGVO in Verbindung mit Art. 7 Abs. 1 DSGVO).
				</p>

				<p>
					Die Kontodaten werden gespeichert, solange dein Konto besteht, und mit der
					Löschung des Kontos entfernt (siehe Abschnitt 15).
				</p>
			</PolicySection>

			<PolicySection :section="S.health">
				<p>
					Einige Funktionen von Nibble verarbeiten Angaben, die Rückschlüsse auf deinen
					Gesundheitszustand zulassen und damit Gesundheitsdaten im Sinne von Art. 9 Abs.
					1 DSGVO sein können. Diese Daten speichern wir

					<strong>
						ausschließlich mit deiner ausdrücklichen Einwilligung
					</strong>:
				</p>

				<ul class="legal__list">
					<li>
						Geburtsdatum, Geschlecht und Körpergröße
					</li>

					<li>
						Körpergewicht und Gewichtsverlauf
					</li>

					<li>
						Ernährungsziel (Abnehmen, Gewicht halten, Zunehmen) sowie Kalorien- und
						Makronährstoffziele einschließlich ihres Verlaufs
					</li>

					<li>
						Einträge im Ernährungstagebuch: Lebensmittel, Mengen, Nährwerte, Datum und
						Mahlzeit
					</li>

					<li>
						Eigene Mahlzeiten
					</li>
				</ul>

				<p>
					Rechtsgrundlage ist deine Einwilligung gemäß Art. 6 Abs. 1 lit. a in Verbindung
					mit Art. 9 Abs. 2 lit. a DSGVO. Die Einwilligung ist freiwillig. Ohne sie kannst
					du Rezepte und den Kalorienrechner weiterhin nutzen; das Speichern der oben
					genannten Daten ist dann technisch gesperrt.
				</p>

				<p>
					Nibble richtet sich ausschließlich an Personen ab {{ MIN_AGE }} Jahren (siehe
					Abschnitt 21). Mit der Einwilligung bestätigst du dein Alter noch einmal (Art. 8
					DSGVO).
				</p>

				<p>
					Du kannst deine Einwilligung jederzeit in den Einstellungen unter „Datenschutz“
					widerrufen. Mit dem Widerruf werden alle oben genannten Daten

					<strong>
						sofort und endgültig gelöscht
					</strong>. Die Rechtmäßigkeit der bis zum
					Widerruf erfolgten Verarbeitung bleibt unberührt. Der Eintrag über deinen
					Widerruf bleibt im Einwilligungsverlauf erhalten (siehe Abschnitt 4).
				</p>
			</PolicySection>

			<PolicySection :section="S.calculator">
				<p>
					Der Kalorienrechner berechnet aus deinen Angaben zu Geschlecht, Alter,
					Körpergröße, Körpergewicht, Schritten, Training und Ziel einen Orientierungswert
					für deinen Kalorien- und Makronährstoffbedarf.
				</p>

				<p>
					Die Berechnung findet vollständig in deinem Browser statt. Deine Eingaben werden
					dabei weder an unseren Server übertragen noch im Browser gespeichert; sie gehen
					beim Neuladen oder Schließen der Seite verloren. Rufst du die Registrierung
					direkt aus dem Rechner auf, werden die Eingaben bis zum Onboarding im
					Arbeitsspeicher der geöffneten Seite mitgeführt.
				</p>

				<p>
					Erst wenn du – mit erteilter Einwilligung – das Ergebnis übernimmst oder deine
					Körperdaten speicherst, werden Ziel, Kalorien- und Makronährstoffziele
					beziehungsweise Geburtsdatum, Geschlecht und Körpergröße in deinem Konto
					gespeichert (siehe Abschnitt 5).
				</p>

				<p>
					Nutzt du den Rechner im Onboarding, übernehmen wir beim Abschluss außerdem
					Geschlecht, Körpergröße und Körpergewicht aus dem Rechner in deine Körperdaten;
					das Gewicht wird der erste Eintrag in deinem Gewichtsverlauf. Die
					Zusammenfassung zeigt dir diese Angaben vorher an.
				</p>

				<p>
					Das Alter aus dem Rechner sowie Angaben zu Schritten und Training werden nie
					gespeichert. Aus den gespeicherten Zielwerten lassen sich jedoch begrenzte
					Rückschlüsse auf dein Aktivitätsniveau ziehen.
				</p>

				<p>
					Die berechneten Werte sind allgemeine Orientierungswerte und ersetzen keine
					medizinische oder ernährungsmedizinische Beratung.
				</p>
			</PolicySection>

			<PolicySection :section="S.diary">
				<p>
					Mit erteilter Einwilligung kannst du Lebensmittel und eigene Mahlzeiten im
					Tagebuch eintragen, dein Gewicht erfassen und eigene Mahlzeiten anlegen. Die
					Einträge werden deinem Konto zugeordnet, damit du deinen Verlauf einsehen
					kannst.
				</p>

				<p>
					Beim Eintragen eines Lebensmittels werden dessen Name, Marke und Nährwerte als
					Kopie im Eintrag gespeichert, damit spätere Änderungen der Produktdaten deine
					Einträge nicht verändern.
				</p>

				<p>
					Du kannst deine Einträge jederzeit bearbeiten oder löschen. Rechtsgrundlage ist
					deine Einwilligung (siehe Abschnitt 5).
				</p>
			</PolicySection>

			<PolicySection :section="S.scanner">
				<p>
					Beim Eintragen kannst du den Barcode eines Lebensmittels mit der Kamera scannen.
					Die Kamera nutzen wir nur, wenn du sie in deinem Browser freigibst, und nur
					während des Scannens.
				</p>

				<p>
					Die Auswertung läuft vollständig auf deinem Gerät. Es werden keine Bilder
					übertragen oder gespeichert. Die Scanner-Bibliothek wird von unserem eigenen
					Server geladen.
				</p>

				<p>
					Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO, für den Zugriff auf die Kamera §
					25 Abs. 2 Nr. 2 TDDDG.
				</p>
			</PolicySection>

			<PolicySection :section="S.recipes">
				<p>
					Als registrierter Nutzer kannst du eigene Rezepte erstellen, einreichen und
					Rezepte auf deiner Merkliste speichern. Dabei verarbeiten wir:
				</p>

				<ul class="legal__list">
					<li>
						Rezeptinhalte: Name, Beschreibung, Zutaten, Mengen, Zubereitungsschritte,
						Zubereitungszeit, Portionen, Nährwerte und Kategorien
					</li>

					<li>
						Hochgeladene Rezeptbilder
					</li>

					<li>
						Zuordnung des Rezepts zu deinem Konto
					</li>

					<li>
						Status der Einreichung (offen, freigegeben, abgelehnt), gegebenenfalls mit
						Ablehnungsgrund
					</li>

					<li>
						Deine Merkliste gespeicherter Rezepte
					</li>
				</ul>

				<p>
					Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO.
				</p>

				<p>
					<strong>
						Moderation:
					</strong> Eingereichte Rezepte und Änderungen werden vor der
					Veröffentlichung von Administratoren geprüft. Diese sehen dabei den Inhalt und
					deinen Benutzernamen. Über Freigabe oder Ablehnung informieren wir dich per
					E-Mail, sofern du deine Adresse bestätigt hast; eine Ablehnung enthält die
					Begründung. Du findest das Ergebnis außerdem bei deinen Rezepten. Bilder sind
					bis zur Freigabe nur für dich und die Moderation abrufbar.
				</p>

				<p>
					<strong>
						Veröffentlichung:
					</strong> Freigegebene Rezepte sind öffentlich, auch
					ohne Anmeldung, abrufbar. Dein Benutzername wird dabei nicht angezeigt oder
					übermittelt.
				</p>

				<p>
					<strong>
						Bilder:
					</strong> Beim Hochladen entfernen wir automatisch eingebettete
					Metadaten wie EXIF-Informationen, insbesondere Kameradaten und Standortangaben
					(GPS).
				</p>

				<p>
					<strong>
						Nach Löschung deines Kontos:
					</strong> Bereits freigegebene Rezepte
					bleiben ohne Zuordnung zu deiner Person bestehen, damit die Rezeptsammlung
					vollständig bleibt. Rechtsgrundlage ist unser berechtigtes Interesse an einer
					beständigen Rezeptsammlung gemäß Art. 6 Abs. 1 lit. f DSGVO. Nicht freigegebene
					Rezepte und offene Änderungen werden mit dem Konto gelöscht. Enthält ein
					freigegebenes Rezept dennoch Angaben, die dich identifizierbar machen (etwa ein
					Foto von dir), entfernen wir es auf Anfrage.
				</p>
			</PolicySection>

			<PolicySection :section="S.foods">
				<p>
					Die Lebensmittelsuche nutzt Produktdaten der freien Datenbank Open Food Facts
					(<BaseLink
						href="https://world.openfoodfacts.org"
						variant="inline"
					>
						https://world.openfoodfacts.org
					</BaseLink>). Unser Server lädt diese Daten einmal wöchentlich herunter und speichert sie
					in der Nibble-Datenbank.
				</p>

				<p>
					Dein Browser stellt keine Anfragen an Open Food Facts, und es werden keine Daten
					über dich an Open Food Facts übermittelt. Deine Suchanfragen werden
					ausschließlich auf unserem Server verarbeitet und nicht gespeichert.
				</p>
			</PolicySection>

			<PolicySection :section="S.cookies">
				<p>
					Nibble verwendet ausschließlich technisch unbedingt erforderliche Cookies:
				</p>

				<!-- display: block on phones drops the table semantics in some browsers, the roles keep them -->
				<!-- eslint-disable vuejs-accessibility/no-redundant-roles -->
				<div class="legal__table-wrapper">
					<table
						class="legal__table legal__table--stacked"
						role="table"
						:aria-labelledby="S.cookies.id"
					>
						<thead role="rowgroup">
							<tr role="row">
								<th
									scope="col"
									role="columnheader"
								>
									Name
								</th>

								<th
									scope="col"
									role="columnheader"
								>
									Zweck
								</th>

								<th
									scope="col"
									role="columnheader"
								>
									Laufzeit
								</th>
							</tr>
						</thead>

						<tbody role="rowgroup">
							<tr
								v-for="cookie in COOKIES"
								:key="cookie.name"
								role="row"
							>
								<th
									scope="row"
									role="rowheader"
								>
									<code>
										{{ cookie.name }}
									</code>
								</th>

								<td
									role="cell"
									data-label="Zweck"
								>
									{{ cookie.purpose }}
								</td>

								<td
									role="cell"
									data-label="Laufzeit"
								>
									{{ cookie.lifetime }}
								</td>
							</tr>
						</tbody>
					</table>
					<!-- eslint-enable vuejs-accessibility/no-redundant-roles -->
				</div>

				<p>
					Alle Cookies werden nur über verschlüsselte Verbindungen übertragen. Beim
					Abmelden werden die Anmelde-Cookies entfernt.
				</p>

				<p>
					Darüber hinaus speichert Nibble keine Daten im Browser (kein Local Storage, kein
					Session Storage). Wir setzen keine Analyse-, Werbe- oder Tracking-Technologien
					ein und binden keine externen Inhalte wie Schriftarten oder Skripte von
					Drittanbietern ein.
				</p>

				<p>
					Rechtsgrundlage für das Speichern und Auslesen dieser Cookies ist § 25 Abs. 2
					Nr. 2 TDDDG; eine Einwilligung ist dafür nicht erforderlich. Die anschließende
					Verarbeitung zur Anmeldung erfolgt gemäß Art. 6 Abs. 1 lit. b DSGVO, der
					CSRF-Schutz gemäß Art. 6 Abs. 1 lit. f DSGVO.
				</p>
			</PolicySection>

			<PolicySection :section="S.email">
				<p>
					Nibble versendet E-Mails, die für dein Konto und die Nutzung der Anwendung
					erforderlich sind:
				</p>

				<ul class="legal__list">
					<li>
						Bestätigung deiner E-Mail-Adresse
					</li>

					<li>
						Zurücksetzen des Passworts
					</li>

					<li>
						Hinweis auf eine Passwortänderung
					</li>

					<li>
						Änderung deiner E-Mail-Adresse: Bestätigungslink an die neue Adresse,
						Hinweis an die alte
					</li>

					<li>
						Bestätigung einer beantragten Kontolöschung und Hinweis, sobald das Konto
						gelöscht ist
					</li>

					<li>
						Freigabe oder Ablehnung eingereichter Rezepte, bei Ablehnung mit Begründung
					</li>

					<li>
						Hinweise auf neue Einreichungen (nur an Administratoren)
					</li>
				</ul>

				<p>
					Bestätigungslinks und Links zum Zurücksetzen des Passworts schicken wir immer.
					Reine Hinweise (Passwortänderung, Hinweis an die alte Adresse, Kontolöschung,
					Ergebnis einer Einreichung) gehen nur an eine bestätigte E-Mail-Adresse. So
					erhält niemand Nachrichten zu einem fremden Konto, wenn sich jemand mit seiner
					Adresse registriert oder vertippt hat.
				</p>

				<p>
					Dabei werden deine E-Mail-Adresse und der Inhalt der jeweiligen Nachricht
					verarbeitet. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO, bei
					sicherheitsbezogenen Nachrichten zusätzlich Art. 6 Abs. 1 lit. f DSGVO.
					Newsletter oder Werbe-E-Mails versenden wir nicht.
				</p>
				<!-- CHECK: adjust if another mail service is set up -->
				<p>
					<strong>
						E-Mail-Dienstleister:
					</strong> Hostinger International Ltd., 61 Lordou
					Vironos str., 6023 Larnaca, Zypern.
				</p>
			</PolicySection>

			<PolicySection :section="S.contact">
				<p>
					Wenn du uns per E-Mail kontaktierst, verarbeiten wir deine E-Mail-Adresse, den
					Inhalt deiner Nachricht und gegebenenfalls deinen Namen, um deine Anfrage zu
					bearbeiten.
				</p>

				<p>
					Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO bei Anfragen zu deinem Konto,
					sonst Art. 6 Abs. 1 lit. f DSGVO. Wir löschen die Nachrichten, sobald deine
					Anfrage abschließend bearbeitet ist und keine gesetzlichen
					Aufbewahrungspflichten entgegenstehen.
				</p>
			</PolicySection>

			<PolicySection :section="S.export">
				<p>
					Du kannst in den Einstellungen jederzeit einen Export aller zu deinem Konto
					gespeicherten Daten als JSON-Datei herunterladen. Er enthält Konto- und
					Profildaten, den Einwilligungsverlauf, Körperdaten, Ziele, Gewichts- und
					Tagebucheinträge, eigene Mahlzeiten, deine Rezepte und Einreichungen
					einschließlich Ablehnungsgründen sowie deine Merkliste.
				</p>

				<p>
					Rechtsgrundlage ist Art. 6 Abs. 1 lit. c DSGVO in Verbindung mit Art. 15 und
					Art. 20 DSGVO.
				</p>
			</PolicySection>

			<PolicySection :section="S.deletion">
				<p>
					Du kannst die Löschung deines Kontos in den Einstellungen beantragen. Ab dem
					Antrag läuft eine Frist von sieben Tagen, in der du den Antrag zurücknehmen
					kannst. Hast du deine E-Mail-Adresse bestätigt, informieren wir dich über den
					Antrag per E-Mail.
				</p>

				<p>
					Nach Ablauf der Frist wird dein Konto mit allen zugehörigen Daten gelöscht. Die
					Löschung läuft einmal täglich und erfolgt spätestens am Tag nach Fristablauf. Zu
					freigegebenen Rezepten siehe Abschnitt 9.
				</p>

				<div class="legal__subsection">
					<h3 class="legal__subheading">
						Datensicherungen
					</h3>

					<p>
						Hostinger sichert einmal wöchentlich den gesamten Server. Es werden zwei
						Stände vorgehalten, gespeichert in Rechenzentren in Frankreich und Litauen.
						Ältere Stände werden automatisch ersetzt. Zusätzlich sichern wir die
						Datenbank täglich und bewahren diese Sicherungen

						{{ DATABASE_BACKUP_DAYS }} Tage auf.
					</p>

					<p>
						Gelöschte Daten können in diesen Sicherungen bis zum Ablauf der jeweiligen
						Frist noch enthalten sein. Danach werden sie automatisch überschrieben.
						Müssen wir eine Sicherung wiederherstellen, wenden wir deine Löschung erneut
						an.
					</p>

					<p>
						Dafür führen wir ein Löschprotokoll. Es enthält nur die interne Nummer
						deines Kontos und die Zeitpunkte von Registrierung, Löschantrag,
						Abbruch und Löschung, keine E-Mail-Adresse und keine weiteren Angaben.
						Eine Kopie neuer Einträge geht einmal täglich per E-Mail an uns, damit
						sie auch nach dem Wiederherstellen des ganzen Servers vorliegt. Wir
						löschen die Einträge nach {{ DELETION_LOG_DAYS }} Tagen, wenn keine
						Sicherung dein Konto mehr enthalten kann. Rechtsgrundlage ist Art. 6
						Abs. 1 lit. c DSGVO in Verbindung mit Art. 17 DSGVO.
					</p>
				</div>

				<p>
					Unabhängig davon kannst du jederzeit dein Recht auf Löschung nach Art. 17 DSGVO
					geltend machen.
				</p>
			</PolicySection>

			<PolicySection :section="S.recipients">
				<p>
					Wir geben deine Daten nicht an Dritte weiter und verkaufen sie nicht. Zugriff
					haben nur:
				</p>

				<ul class="legal__list">
					<li>
						<strong>
							Hostinger
						</strong> als Anbieter von Server und E-Mail-Postfach, auf
						Grundlage eines Vertrags zur Auftragsverarbeitung gemäß Art. 28 DSGVO
					</li>

					<li>
						<strong>
							Administratoren von Nibble
						</strong>, soweit dies für Betrieb und
						Moderation erforderlich ist
					</li>
				</ul>
			</PolicySection>

			<PolicySection :section="S.transfer">
				<p>
					Die Daten werden auf dem Server im oben genannten Rechenzentrum gespeichert.
					Hostinger setzt für einzelne Leistungen Unterauftragsverarbeiter ein, die
					teilweise ihren Sitz außerhalb der EU haben, insbesondere in den USA. Soweit
					dabei personenbezogene Daten übermittelt werden, geschieht dies auf Grundlage
					der EU-Standardvertragsklauseln gemäß Art. 46 Abs. 2 lit. c DSGVO.
				</p>
			</PolicySection>

			<PolicySection :section="S.retention">
				<div class="legal__table-wrapper">
					<table
						class="legal__table"
						:aria-labelledby="S.retention.id"
					>
						<thead>
							<tr>
								<th scope="col">
									Daten
								</th>

								<th scope="col">
									Speicherdauer
								</th>
							</tr>
						</thead>

						<tbody>
							<tr>
								<th scope="row">
									Kontodaten, Rezepte, Merkliste
								</th>

								<td>
									bis zur Löschung des Kontos
								</td>
							</tr>

							<tr>
								<th scope="row">
									Gesundheitsdaten (Abschnitt 5)
								</th>

								<td>
									bis zum Widerruf der Einwilligung oder zur Löschung des Kontos
								</td>
							</tr>

							<tr>
								<th scope="row">
									Einwilligungsverlauf
								</th>

								<td>
									bis zur Löschung des Kontos
								</td>
							</tr>

							<tr>
								<th scope="row">
									Serverprotokolle
								</th>

								<td>
									höchstens 14 Tage
								</td>
							</tr>

							<tr>
								<th scope="row">
									Zähler zur Missbrauchsabwehr (IP-Adresse, gehashte
									E-Mail-Adresse)
								</th>

								<td>
									höchstens 1 Stunde
								</td>
							</tr>

							<tr>
								<th scope="row">
									Gesperrte Anmelde-Token
								</th>

								<td>
									bis zum Ablauf, höchstens 7 Tage
								</td>
							</tr>

							<tr>
								<th scope="row">
									Datensicherungen
								</th>

								<td>
									Serversicherung: zwei wöchentliche Stände, also bis zu zwei
									Wochen; Datenbanksicherung: {{ DATABASE_BACKUP_DAYS }} Tage
								</td>
							</tr>

							<tr>
								<th scope="row">
									Löschprotokoll
								</th>

								<td>
									{{ DELETION_LOG_DAYS }} Tage ab dem Eintrag
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</PolicySection>

			<PolicySection :section="S.security">
				<p>
					Wir schützen deine Daten mit technischen und organisatorischen Maßnahmen,
					insbesondere:
				</p>

				<ul class="legal__list">
					<li>
						durchgehend verschlüsselte Übertragung (HTTPS)
					</li>

					<li>
						Speicherung von Passwörtern ausschließlich als Hash
					</li>

					<li>
						Anmelde-Cookies, die nicht per JavaScript auslesbar sind, kurze
						Token-Laufzeiten und Sperrung alter Token bei Erneuerung, Abmeldung und
						Passwortänderung
					</li>

					<li>
						Begrenzung von Anfragen zur Abwehr von Missbrauch: Dafür werden IP-Adresse
						beziehungsweise ein Hash der E-Mail-Adresse höchstens eine Stunde lang
						zwischengespeichert (Art. 6 Abs. 1 lit. f DSGVO)
					</li>

					<li>
						Zugriffsbeschränkungen auf Server und Verwaltungsbereich
					</li>
				</ul>
			</PolicySection>

			<PolicySection :section="S.rights">
				<p>
					Du hast nach Maßgabe der gesetzlichen Voraussetzungen das Recht auf:
				</p>

				<ul class="legal__list">
					<li>
						Auskunft über deine gespeicherten Daten (Art. 15 DSGVO)
					</li>

					<li>
						Berichtigung unrichtiger Daten (Art. 16 DSGVO)
					</li>

					<li>
						Löschung (Art. 17 DSGVO)
					</li>

					<li>
						Einschränkung der Verarbeitung (Art. 18 DSGVO)
					</li>

					<li>
						Datenübertragbarkeit (Art. 20 DSGVO)
					</li>

					<li>
						Widerruf erteilter Einwilligungen mit Wirkung für die Zukunft (Art. 7 Abs. 3
						DSGVO)
					</li>
				</ul>

				<p>
					Zur Ausübung deiner Rechte genügt eine E-Mail an

					<BaseLink
						:href="`mailto:${OPERATOR.privacyEmail}`"
						variant="inline"
					>
						{{ OPERATOR.privacyEmail }}
					</BaseLink>.
				</p>

				<div class="legal__subsection">
					<h3 class="legal__subheading">
						Widerspruchsrecht (Art. 21 DSGVO)
					</h3>

					<p>
						<strong>
							Soweit wir Daten auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO
							verarbeiten, kannst du aus Gründen, die sich aus deiner besonderen
							Situation ergeben, jederzeit Widerspruch gegen diese Verarbeitung
							einlegen. Wir verarbeiten die Daten dann nicht mehr, es sei denn, wir
							können zwingende schutzwürdige Gründe nachweisen, die deine Interessen
							überwiegen, oder die Verarbeitung dient der Geltendmachung, Ausübung
							oder Verteidigung von Rechtsansprüchen.
						</strong>
					</p>
				</div>

				<div class="legal__subsection">
					<h3 class="legal__subheading">
						Beschwerderecht
					</h3>

					<p>
						Du hast das Recht, dich bei einer Datenschutzaufsichtsbehörde zu beschweren
						(Art. 77 DSGVO). Zuständig für uns ist:
					</p>

					<p class="legal__address">
						Landesbeauftragte für Datenschutz und Informationsfreiheit
						Nordrhein-Westfalen<br />

						Kavalleriestraße 2–4<br />

						40213 Düsseldorf<br />

						<BaseLink
							href="https://www.ldi.nrw.de"
							variant="inline"
						>
							https://www.ldi.nrw.de
						</BaseLink>
					</p>
				</div>
			</PolicySection>

			<PolicySection :section="S.minimumAge">
				<p>
					Nibble richtet sich ausschließlich an Personen ab {{ MIN_AGE }} Jahren. Unter

					{{ MIN_AGE }} Jahren ist kein Konto vorgesehen.
				</p>

				<p>
					Die Bestätigung gibst du bei der Registrierung ab. Wir speichern dazu Zeitpunkt
					und Version der AGB (siehe Abschnitt 4). In die Speicherung von Gesundheitsdaten
					(Abschnitt 5) willigst du zusätzlich im Onboarding ein.
				</p>
			</PolicySection>

			<PolicySection :section="S.automated">
				<p>
					Nibble berechnet aus deinen Angaben Orientierungswerte für Kalorien- und
					Nährstoffbedarf. Diese dienen nur deiner Information und Planung. Eine
					automatisierte Entscheidung mit rechtlicher Wirkung oder ähnlich erheblicher
					Beeinträchtigung im Sinne von Art. 22 DSGVO findet nicht statt.
				</p>
			</PolicySection>

			<PolicySection :section="S.changes">
				<p>
					Wir passen diese Datenschutzerklärung an, wenn sich Funktionen von Nibble oder
					rechtliche Anforderungen ändern. Die aktuelle Fassung findest du jederzeit unter

					<BaseLink
						route-name="legal-privacy"
						variant="inline"
					>
						{{ OPERATOR.website }}/datenschutz
					</BaseLink>. Betrifft eine Änderung deine Einwilligung,
					informieren wir dich in der Anwendung.
				</p>
			</PolicySection>
		</article>
	</main>
</template>
