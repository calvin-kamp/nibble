import type { Sex } from '@features/calorie-calculator/calorie-calculator.types'

export interface Credentials {
	email: string
	password: string
}

/** Body of /auth/register: the checkbox covers the terms and the minimum age */
export interface RegisterRequest extends Credentials {
	terms_accepted: true
}

export interface AuthUser {
	id: number
	email: string
	username: string | null
	isEmailVerified: boolean
	hasCompletedOnboarding: boolean
	hasDataConsent: boolean
	/** When consent was last given or revoked (ISO timestamp), null if never decided */
	dataConsentChangedAt: string | null
	isStaff: boolean
	/** Time of permanent deletion (ISO) when a deletion has been requested */
	deletionScheduledFor: string | null
	profile: PersonalProfile
}

export interface PersonalProfile {
	/** YYYY-MM-DD */
	birthDate: string | null
	heightCm: number | null
	sex: Sex | null
}

export type OnboardingStepResponse = 'username' | 'consent' | 'goal' | 'targets' | 'summary'

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

export type VerifyState = 'pending' | 'verified' | 'failed'
