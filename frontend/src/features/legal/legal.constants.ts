import type { Operator, PolicySection } from '@features/legal/legal.types'

import { CONTACT_EMAIL } from '@shared/constants'

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
	// General contact for the Impressum and the terms; § 5 DDG asks for a fast electronic way
	// to reach you. The same mailbox as "Alles andere" on the help pages.
	email: CONTACT_EMAIL,
	// Recommended as the second direct channel next to the email address
	phone: '',
	// Only if you have one (§ 27a UStG)
	vatId: '',
	privacyEmail: 'datenschutz@nibble-tracking.de',
	website: 'https://www.nibble-tracking.de',
}

/**
 * Date of the terms on /agb, shown there as "Stand". Change it together with the text and
 * TERMS_VERSION in the backend settings, which is recorded with every new profile.
 */
export const TERMS_VERSION = '2026-10-28'

/**
 * Date of the privacy policy revision on /datenschutz, also the version recorded with every
 * consent decision. The page shows it as "Stand", so a new revision cannot ship without a new
 * version: change the text in PrivacyPolicyView and this date together, and
 * PRIVACY_POLICY_VERSION in the backend settings, which is recorded with every new profile.
 */
export const PRIVACY_POLICY_VERSION = '2026-11-04'

/** Nibble is for people aged 16 and up, see sections 5 and 21 of the privacy policy */
export const MIN_AGE = 16

// Wording of the consent checkbox. It belongs to the policy revision above, so new wording
// needs a new version as well.
const CONSENT_TEXT =
	'willige ausdrücklich ein, dass Nibble meine Gesundheitsdaten speichert: Geburtsdatum, ' +
	'Geschlecht, Größe, Gewicht, mein Ernährungsziel mit Kalorien- und Makronährstoffzielen, ' +
	'Tagebucheinträge sowie eigene Mahlzeiten. Ich kann die Einwilligung jederzeit ' +
	'in den Einstellungen widerrufen; die Daten werden dann sofort gelöscht.'

// In the onboarding with the age confirmation: below 16, consent needs the parents' approval
// (Art. 8 GDPR).
export const ONBOARDING_CONSENT_LABEL = `Ich bin mindestens ${MIN_AGE} Jahre alt und ${CONSENT_TEXT}`

// In the account without it: the minimum age is confirmed at registration (terms, section 4),
// so asking again there would suggest it is checked anew.
export const CONSENT_LABEL = `Ich ${CONSENT_TEXT}`

export const PRIVACY_POLICY_SECTIONS = {
	general: { id: 'allgemeine-hinweise', title: '1. Allgemeine Hinweise' },
	controller: { id: 'verantwortlicher', title: '2. Verantwortlicher' },
	hosting: { id: 'hosting', title: '3. Hosting und Serverprotokolle' },
	account: { id: 'benutzerkonto', title: '4. Registrierung und Benutzerkonto' },
	health: { id: 'gesundheitsdaten', title: '5. Gesundheitsdaten und Einwilligung' },
	calculator: { id: 'kalorienrechner', title: '6. Kalorienrechner' },
	diary: { id: 'tagebuch', title: '7. Ernährungstagebuch, Gewicht und eigene Mahlzeiten' },
	scanner: { id: 'barcode-scanner', title: '8. Barcode-Scanner und Kamera' },
	recipes: { id: 'rezepte', title: '9. Rezepte und hochgeladene Inhalte' },
	foods: { id: 'open-food-facts', title: '10. Lebensmitteldaten von Open Food Facts' },
	cookies: { id: 'cookies', title: '11. Cookies und lokale Speicherung' },
	email: { id: 'e-mail', title: '12. E-Mail-Kommunikation' },
	contact: { id: 'kontakt', title: '13. Kontaktaufnahme' },
	export: { id: 'datenexport', title: '14. Datenexport' },
	deletion: { id: 'kontoloeschung', title: '15. Löschung des Benutzerkontos' },
	recipients: { id: 'empfaenger', title: '16. Empfänger und Auftragsverarbeiter' },
	transfer: { id: 'drittlaender', title: '17. Datenübermittlung in Drittländer' },
	retention: { id: 'speicherdauer', title: '18. Speicherdauer im Überblick' },
	security: { id: 'datensicherheit', title: '19. Datensicherheit' },
	rights: { id: 'rechte', title: '20. Deine Rechte' },
	minimumAge: { id: 'mindestalter', title: '21. Mindestalter' },
	automated: { id: 'automatisierte-entscheidungen', title: '22. Automatisierte Entscheidungen' },
	changes: { id: 'aenderungen', title: '23. Änderungen dieser Datenschutzerklärung' },
} satisfies Record<string, PolicySection>
