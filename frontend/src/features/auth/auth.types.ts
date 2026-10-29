import type { Sex } from '@features/calorie-calculator/calorie-calculator.types'

export interface Credentials {
	email: string
	password: string
}

/** Signed-in user as returned by /api/auth/me, plus consent */
export interface AuthUser {
	id: number
	email: string
	/** Only set after onboarding */
	username: string | null
	isEmailVerified: boolean
	hasCompletedOnboarding: boolean
	/** Consent from onboarding: without it there is no tracking and no saved meals */
	hasDataConsent: boolean
	/** When consent was last given or revoked (ISO timestamp), null if never decided */
	dataConsentChangedAt: string | null
	/** For recipe moderation */
	isStaff: boolean
	/** Time of permanent deletion (ISO) when a deletion has been requested */
	deletionScheduledFor: string | null
	/** Personal details, e.g. for the calorie calculator */
	profile: PersonalProfile
}

/** Details from the account's "Persönliches" area. null while nothing has been entered. */
export interface PersonalProfile {
	/** YYYY-MM-DD */
	birthDate: string | null
	heightCm: number | null
	sex: Sex | null
}

export type OnboardingStepResponse = 'username' | 'consent' | 'goal' | 'targets' | 'summary'

/** Response from Django (AccountState), fields in snake_case */
export interface AccountStateResponse {
	id: number
	email: string
	email_verified: boolean
	username: string | null
	/** true = consented, false = declined or revoked, null = not decided yet */
	privacy_consent: boolean | null
	onboarding: { completed: boolean; current_step: OnboardingStepResponse }
	is_staff: boolean
	deletion_scheduled_for: string | null
}

export interface ConsentStateResponse {
	accepted: boolean | null
	decided_at: string | null
	policy_version: string | null
}

/** Body data from /tracking/body, only readable with consent */
export interface BodyProfileResponse {
	birth_date: string | null
	height_cm: number | null
	sex: Sex | null
}

/** Result of opening the confirmation link from the email */
export type VerifyState = 'pending' | 'verified' | 'failed'
