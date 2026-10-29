export interface PolicySection {
	/** Jump mark, e.g. /datenschutz#cookies */
	id: string
	title: string
}

/** Provider details for Impressum, privacy policy and terms */
export interface Operator {
	name: string
	street: string
	postalCode: string
	city: string
	country: string
	email: string
	/** Empty: not shown */
	phone: string
	/** VAT identification number; empty: not shown */
	vatId: string
	privacyEmail: string
	website: string
}
