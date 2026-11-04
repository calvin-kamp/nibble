export interface PolicySection {
	id: string
	title: string
}

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
