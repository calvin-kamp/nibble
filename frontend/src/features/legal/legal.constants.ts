import type { Operator, PolicySection } from '@features/legal/legal.types'

/**
 * Who runs Nibble. Impressum, privacy policy and terms all read from here, so the details are
 * entered once. Optional fields stay empty strings and are then left out of the pages.
 */
export const OPERATOR: Operator = {
	name: 'Calvin Kamp',
	street: 'Elsternweg 2',
	postalCode: '58119',
	city: 'Hagen',
	country: 'Deutschland',
	// General contact for the Impressum; § 5 DDG asks for a fast electronic way to reach you.
	// Swap in a general mailbox if there is one besides the privacy address.
	email: 'datenschutz@nibble-tracking.de',
	// Recommended as the second direct channel next to the email address
	phone: '',
	// Only if you have one (§ 27a UStG)
	vatId: '',
	privacyEmail: 'datenschutz@nibble-tracking.de',
	website: 'https://nibble-tracking.de',
}

/** Date of the terms on /agb, shown there as "Stand". Change it together with the text. */
export const TERMS_VERSION = '2026-10-28'

/**
 * Date of the privacy policy revision on /datenschutz, also the version recorded with every
 * consent decision. The page shows it as "Stand", so a new revision cannot ship without a new
 * version: change the text in PrivacyPolicyView and this date together.
 */
export const PRIVACY_POLICY_VERSION = '2026-10-27'

/** Nibble is for people aged 16 and up, see sections 5 and 20 of the privacy policy */
export const MIN_AGE = 16

// Wording of the consent checkbox in onboarding and in the account. It belongs to the policy
// revision above, so new wording needs a new version as well. The age confirmation is part of
// it: below 16, consent needs the parents' approval (Art. 8 GDPR).
export const CONSENT_LABEL =
	`Ich bin mindestens ${MIN_AGE} Jahre alt und willige ausdrücklich ein, dass Nibble meine ` +
	'Gesundheitsdaten speichert: Geburtsdatum, Geschlecht, Größe, Gewicht, mein Ernährungsziel ' +
	'mit Kalorien- und Makronährstoffzielen, Tagebucheinträge sowie eigene Mahlzeiten mit ' +
	'Notizen. Ich kann die Einwilligung jederzeit in den Einstellungen widerrufen; die Daten ' +
	'werden dann sofort gelöscht.'

// Headings of the privacy policy, in order, for the table of contents and the sections
export const PRIVACY_POLICY_SECTIONS = {
	general: { id: 'allgemeine-hinweise', title: '1. Allgemeine Hinweise' },
	controller: { id: 'verantwortlicher', title: '2. Verantwortlicher' },
	hosting: { id: 'hosting', title: '3. Hosting und Serverprotokolle' },
	account: { id: 'benutzerkonto', title: '4. Registrierung und Benutzerkonto' },
	health: { id: 'gesundheitsdaten', title: '5. Gesundheitsdaten und Einwilligung' },
	calculator: { id: 'kalorienrechner', title: '6. Kalorienrechner' },
	diary: { id: 'tagebuch', title: '7. Ernährungstagebuch, Gewicht und eigene Mahlzeiten' },
	recipes: { id: 'rezepte', title: '8. Rezepte und hochgeladene Inhalte' },
	foods: { id: 'open-food-facts', title: '9. Lebensmitteldaten von Open Food Facts' },
	cookies: { id: 'cookies', title: '10. Cookies und lokale Speicherung' },
	email: { id: 'e-mail', title: '11. E-Mail-Kommunikation' },
	contact: { id: 'kontakt', title: '12. Kontaktaufnahme' },
	export: { id: 'datenexport', title: '13. Datenexport' },
	deletion: { id: 'kontoloeschung', title: '14. Löschung des Benutzerkontos' },
	recipients: { id: 'empfaenger', title: '15. Empfänger und Auftragsverarbeiter' },
	transfer: { id: 'drittlaender', title: '16. Datenübermittlung in Drittländer' },
	retention: { id: 'speicherdauer', title: '17. Speicherdauer im Überblick' },
	security: { id: 'datensicherheit', title: '18. Datensicherheit' },
	rights: { id: 'rechte', title: '19. Deine Rechte' },
	minimumAge: { id: 'mindestalter', title: '20. Mindestalter' },
	automated: { id: 'automatisierte-entscheidungen', title: '21. Automatisierte Entscheidungen' },
	changes: { id: 'aenderungen', title: '22. Änderungen dieser Datenschutzerklärung' },
} satisfies Record<string, PolicySection>
