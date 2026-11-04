import type { HelpTopic } from '@features/help/help.types'

import { MIN_AGE, OPERATOR } from '@features/legal/legal.constants'
import { SUPPORT_EMAIL } from '@shared/constants'

// Questions and answers of /hilfe. They describe what the app does today; when a feature
// changes, change its answer here as well. The topic ids are linked from the footer.
export const HELP_TOPICS: HelpTopic[] = [
	{
		id: 'erste-schritte',
		title: 'Erste Schritte',
		lead: 'Was du ohne Konto nutzen kannst und wie die Einrichtung abläuft.',
		questions: [
			{
				id: 'ohne-konto',
				question: 'Brauche ich ein Konto?',
				answer: [
					'Rezepte lesen und den Kalorienrechner nutzen kannst du ohne Konto. Für das Tagebuch, dein Ziel, den Gewichtsverlauf und eigene oder gespeicherte Rezepte brauchst du ein kostenloses Konto.',
				],
				links: [
					{ label: 'Konto anlegen', routeName: 'auth-register' },
					{ label: 'Zum Kalorienrechner', routeName: 'calorie-calculator' },
				],
			},
			{
				id: 'einrichtung',
				question: 'Was passiert bei der Einrichtung?',
				answer: [
					'Nach der Registrierung wählst du einen Benutzernamen und entscheidest, ob nibble deine Gesundheitsdaten speichern darf. Mit Einwilligung folgen Körperdaten, dein Ziel (abnehmen, Gewicht halten oder zunehmen) und dein Tagesbedarf. Die Körperdaten sind freiwillig, du kannst sie überspringen.',
					'Gespeichert wird erst am Ende und nur mit deiner Einwilligung. Brichst du ab, kannst du die Einrichtung später fortsetzen.',
				],
			},
			{
				id: 'tagesbedarf',
				question: 'Wie berechnet nibble meinen Tagesbedarf?',
				answer: [
					'Der Rechner nimmt deinen Grundumsatz nach Mifflin-St Jeor und rechnet Alltag und Schritte, dein Training und den Energieaufwand der Verdauung dazu. Für dein Ziel ziehen wir 15 % ab, lassen den Wert gleich oder legen 10 % drauf. Jeden Posten siehst du im Ergebnis einzeln.',
					'Unter einem BMI von 18,5 oder unter 18 Jahren rechnet nibble kein Defizit. Wir sind keine Ärzte: Bei Vorerkrankungen oder sehr niedrigen Werten sprich bitte mit einer Ärztin oder einem Arzt.',
				],
				links: [{ label: 'Bedarf berechnen', routeName: 'calorie-calculator' }],
			},
			{
				id: 'bedarf-aendern',
				question: 'Kann ich meinen Tagesbedarf später ändern?',
				answer: [
					'Ja, in den Einstellungen unter „Ernährung“: dein Ziel sowie Protein, Kohlenhydrate und Fett in Gramm, die Kalorien ergeben sich daraus. Der neue Wert gilt ab heute, frühere Tage behalten ihre Werte.',
				],
				links: [
					{ label: 'Zu den Ernährungseinstellungen', routeName: 'account-nutrition' },
				],
			},
		],
	},
	{
		id: 'tagebuch',
		title: 'Tagebuch und Scanner',
		lead: 'Essen und Gewicht eintragen, per Barcode oder Suche.',
		questions: [
			{
				id: 'essen-eintragen',
				question: 'Wie trage ich Essen ein?',
				answer: [
					'Tipp auf „Eintrag hinzufügen“: am Handy das Plus in der unteren Leiste, am Desktop der Button in der Seitenleiste. Wähle „Essen“, dann Mahlzeit und Datum. Such das Lebensmittel nach Name oder Barcode, gib die Menge mit Einheit an (g, ml, Portion oder Packung) und speichere.',
					'Statt eines Lebensmittels kannst du auch eine deiner gespeicherten Mahlzeiten wählen. Sie wird als eine Portion eingetragen.',
				],
				links: [{ label: 'Zum Ernährungstagebuch', routeName: 'diary-food' }],
			},
			{
				id: 'scanner',
				question: 'Der Scanner erkennt den Barcode nicht. Was kann ich tun?',
				answer: [
					'Erlaube deinem Browser den Zugriff auf die Kamera und halte den Strichcode ruhig in den Rahmen. Erkannt werden EAN- und UPC-Codes.',
					'Klappt es trotzdem nicht, tipp die Zahl unter dem Strichcode ins Suchfeld. Die Erkennung läuft nur in deinem Browser, Kamerabilder verlassen dein Gerät nicht.',
				],
			},
			{
				id: 'zukunft',
				question: 'Kann ich Einträge für morgen vorplanen?',
				answer: [
					'Nein. Das Tagebuch nimmt Einträge für heute und vergangene Tage an, damit es zeigt, was du wirklich gegessen hast.',
				],
			},
			{
				id: 'gewicht',
				question: 'Wie oft sollte ich mein Gewicht eintragen?',
				answer: [
					'So oft du magst, höchstens einmal am Tag: Ein neuer Eintrag ersetzt den des gleichen Tages. Am besten wiegst du dich morgens vor dem Frühstück. Der Verlauf zeigt den Schnitt der letzten 7 Tage, damit Schwankungen von Tag zu Tag nicht täuschen.',
				],
				links: [{ label: 'Zum Gewichtsverlauf', routeName: 'diary-weight' }],
			},
			{
				id: 'mahlzeiten',
				question: 'Was sind „Meine Mahlzeiten“?',
				answer: [
					'Eine Mahlzeit ist eine Kombination von Lebensmitteln, die du oft isst, etwa dein übliches Frühstück. Du legst sie einmal an und trägst sie danach mit einem Klick ein. Änderst oder löschst du eine Mahlzeit, bleiben die Einträge im Tagebuch, wie sie waren.',
				],
				links: [{ label: 'Zu meinen Mahlzeiten', routeName: 'own-meals' }],
			},
		],
	},
	{
		id: 'rezepte',
		title: 'Rezepte',
		lead: 'Rezepte finden, speichern und selbst veröffentlichen.',
		questions: [
			{
				id: 'pruefung',
				question: 'Warum ist mein Rezept noch nicht zu sehen?',
				answer: [
					'Neue Rezepte und Änderungen an veröffentlichten Rezepten prüft unser Team, bevor sie live gehen. Bis dahin siehst nur du die neue Fassung; bei einer Änderung bleibt so lange die alte online.',
					'Wird ein Rezept nicht freigegeben, bekommst du eine E-Mail und siehst die Begründung auf der Rezeptseite.',
				],
			},
			{
				id: 'speichern',
				question: 'Wie speichere ich ein Rezept?',
				answer: [
					'Auf der Rezeptseite über „Rezept speichern“. Gespeicherte Rezepte findest du in der Rezeptliste unter „Gespeichert“ und auf deiner Übersicht. Speichern lassen sich freigegebene Rezepte.',
				],
				links: [{ label: 'Zu den Rezepten', routeName: 'recipe-list' }],
			},
			{
				id: 'naehrwerte',
				question: 'Woher kommen die Nährwerte eines Rezepts?',
				answer: [
					'Wer das Rezept einreicht, gibt Protein, Kohlenhydrate und Fett pro Portion an. nibble berechnet daraus die Kalorien.',
				],
			},
		],
	},
	{
		id: 'datenschutz',
		title: 'Datenschutz und Konto',
		lead: 'Einwilligung, Export, Löschen und Zugangsdaten.',
		questions: [
			{
				id: 'einwilligung',
				question: 'Warum fragt nibble nach einer Einwilligung?',
				answer: [
					`Gewicht, Körperdaten und Tagebuch sind Gesundheitsdaten. Die speichern wir nur, wenn du ausdrücklich einwilligst und mindestens ${MIN_AGE} Jahre alt bist. Ohne Einwilligung gibt es kein Tagebuch, Rezepte und Rechner kannst du weiter nutzen.`,
					'Du kannst die Einwilligung jederzeit in den Einstellungen widerrufen. Die Daten werden dann sofort gelöscht.',
				],
				links: [{ label: 'Zu den Datenschutzeinstellungen', routeName: 'account-privacy' }],
			},
			{
				id: 'export',
				question: 'Wie bekomme ich meine Daten?',
				answer: [
					'In den Einstellungen unter „Datenschutz“ lädst du die Daten deines Kontos als JSON-Datei herunter.',
				],
				links: [{ label: 'Daten exportieren', routeName: 'account-privacy' }],
			},
			{
				id: 'konto-loeschen',
				question: 'Wie lösche ich mein Konto?',
				answer: [
					'In den Einstellungen unter „Konto löschen“, mit deinem Passwort. Die Löschung wird für in 7 Tagen vorgemerkt. Bis dahin kannst du sie nach dem Anmelden abbrechen. Exportiere deine Daten am besten vorher.',
				],
				links: [{ label: 'Zur Kontolöschung', routeName: 'account-delete' }],
			},
			{
				id: 'passwort',
				question: 'Ich habe mein Passwort vergessen.',
				answer: [
					'Gib auf der Seite „Passwort vergessen“ deine E-Mail-Adresse ein. Gehört sie zu einem Konto, bekommst du einen Link, mit dem du ein neues Passwort setzt.',
					`Kommt keine E-Mail an, schau im Spam-Ordner nach oder schreib uns an ${SUPPORT_EMAIL}.`,
				],
				links: [
					{ label: 'Passwort zurücksetzen', routeName: 'auth-password-forgot' },
					{ label: SUPPORT_EMAIL, href: `mailto:${SUPPORT_EMAIL}` },
				],
			},
			{
				id: 'datenschutz-kontakt',
				question: 'Wen frage ich zum Datenschutz?',
				answer: [
					`Fragen zu deinen Daten und zu deiner Einwilligung beantworten wir unter ${OPERATOR.privacyEmail}. Was wir speichern und wie lange, steht in der Datenschutzerklärung.`,
				],
				links: [
					{ label: OPERATOR.privacyEmail, href: `mailto:${OPERATOR.privacyEmail}` },
					{ label: 'Zur Datenschutzerklärung', routeName: 'legal-privacy' },
				],
			},
		],
	},
]
