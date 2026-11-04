import type { HelpGuide } from '@features/help/help.types'

// The guide on /hilfe/anleitung: the app's main tasks, step by step. Button and field names
// are quoted exactly as they appear in the app; when one changes, change it here as well.
export const HELP_GUIDES: HelpGuide[] = [
	{
		id: 'loslegen',
		title: 'Loslegen',
		lead: 'Konto anlegen und nibble in wenigen Schritten einrichten.',
		steps: [
			'Tipp auf „Registrieren“, gib deine E-Mail-Adresse und ein Passwort mit mindestens 8 Zeichen ein und wähl „Konto erstellen“.',
			'Bestätige deine E-Mail-Adresse über den Link, den wir dir schicken.',
			'In der Einrichtung wählst du einen Benutzernamen und entscheidest, ob nibble deine Gesundheitsdaten speichern darf. Ohne diese Einwilligung gibt es kein Tagebuch.',
			'Mit Einwilligung folgen Körperdaten, dein Ziel und dein Tagesbedarf. Was du nicht angeben möchtest, überspringst du.',
		],
		links: [{ label: 'Konto anlegen', routeName: 'auth-register' }],
	},
	{
		id: 'tagesbedarf',
		title: 'Tagesbedarf berechnen',
		lead: 'Der Kalorienrechner zeigt jeden Posten einzeln. Du brauchst dafür kein Konto.',
		steps: [
			'Öffne den Kalorienrechner und gib Geschlecht, Alter, Größe und Gewicht an.',
			'Trag ein, wie viele Schritte du am Tag ungefähr gehst.',
			'Füg dein Training hinzu: Sportart, Dauer und wie oft pro Woche. Das ist optional.',
			'Wähl dein Ziel und tipp auf „Bedarf berechnen“.',
			'Mit Konto und Einwilligung übernimmst du das Ergebnis über „Als Tagesbedarf übernehmen“.',
		],
		links: [{ label: 'Zum Kalorienrechner', routeName: 'calorie-calculator' }],
	},
	{
		id: 'essen',
		title: 'Essen eintragen',
		lead: 'Per Suche, Barcode oder als gespeicherte Mahlzeit.',
		steps: [
			'Tipp auf „Eintrag hinzufügen“: am Handy auf das Plus in der unteren Leiste, am Desktop auf den Button in der Seitenleiste. Wähl „Essen eintragen“.',
			'Wähl Mahlzeit und Datum. Einträge für die Zukunft sind nicht möglich.',
			'Such im Feld „Name, Marke oder Barcode“ nach dem Lebensmittel oder scanne den Barcode mit dem Kamera-Symbol.',
			'Gib Menge und Einheit an. Die Nährwerte darunter rechnen mit.',
			'Tipp auf „Eintragen“. Den Eintrag findest du unter Tagebuch, Essen.',
		],
		links: [{ label: 'Zum Ernährungstagebuch', routeName: 'diary-food' }],
	},
	{
		id: 'gewicht',
		title: 'Gewicht eintragen',
		lead: 'Ein Eintrag pro Tag, der Verlauf zeigt den Schnitt der letzten 7 Tage.',
		steps: [
			'Tipp auf „Eintrag hinzufügen“ und wähl „Gewicht eintragen“.',
			'Gib Gewicht und Datum an und tipp auf „Speichern“. Ein neuer Eintrag ersetzt den des gleichen Tages.',
			'Unter Tagebuch, Gewicht wählst du den Zeitraum für den Verlauf und siehst alle Einträge.',
		],
		links: [{ label: 'Zum Gewichtsverlauf', routeName: 'diary-weight' }],
	},
	{
		id: 'mahlzeiten',
		title: 'Mahlzeiten speichern',
		lead: 'Was du oft isst, trägst du danach mit einem Klick ein.',
		steps: [
			'Öffne „Meine Mahlzeiten“ und tipp auf „Mahlzeit anlegen“.',
			'Gib einen Namen ein und füg die Lebensmittel mit ihren Mengen hinzu.',
			'Tipp auf „Mahlzeit speichern“.',
			'Beim Eintragen wählst du im Reiter „Mahlzeiten“ die gespeicherte Mahlzeit aus. Sie zählt als eine Portion.',
		],
		links: [{ label: 'Zu meinen Mahlzeiten', routeName: 'own-meals' }],
	},
	{
		id: 'rezepte',
		title: 'Rezepte finden und teilen',
		lead: 'Suchen, filtern, speichern und eigene Rezepte veröffentlichen.',
		steps: [
			'In „Rezepte“ suchst du nach Namen, filterst nach Ernährungsform, Unverträglichkeiten, Küchengeräten und Eigenschaften und sortierst nach neuesten oder beliebtesten.',
			'Auf einer Rezeptseite merkst du dir ein Rezept über „Rezept speichern“. Du findest es unter „Gespeichert“.',
			'Für ein eigenes Rezept tippst du auf „Rezept anlegen“ und füllst Grunddaten, Nährwerte, Eigenschaften, Zutaten und Zubereitung aus.',
			'Mit „Rezept speichern“ reichst du es ein. Nach der Prüfung durch unser Team ist es für alle sichtbar.',
		],
		links: [{ label: 'Zu den Rezepten', routeName: 'recipe-list' }],
	},
	{
		id: 'konto',
		title: 'Konto und Daten verwalten',
		lead: 'Alles zu Profil, Zielen und Datenschutz steht in den Einstellungen.',
		steps: [
			'Unter „Anmeldedaten“ änderst du Benutzername, E-Mail-Adresse und Passwort.',
			'Unter „Persönliches“ und „Ernährung“ passt du Körperdaten, Ziel und Tagesbedarf an.',
			'Unter „Datenschutz“ erteilst oder widerrufst du die Einwilligung und lädst deine Daten herunter.',
			'Unter „Konto löschen“ merkst du die Löschung vor. Sie wird nach 7 Tagen ausgeführt, bis dahin kannst du sie abbrechen.',
		],
		links: [{ label: 'Zu den Einstellungen', routeName: 'account' }],
	},
]
