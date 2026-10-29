import type {
	AccountStateResponse,
	AuthUser,
	BodyProfileResponse,
	ConsentStateResponse,
	Credentials,
	PersonalProfile,
} from '@features/auth/auth.types'

import { apiRequest } from '@shared/api/client'

const EMPTY_PROFILE: PersonalProfile = { birthDate: null, heightCm: null, sex: null }

export function toPersonalProfile(body: BodyProfileResponse): PersonalProfile {
	return { birthDate: body.birth_date, heightCm: body.height_cm, sex: body.sex }
}

export function toAuthUser(
	state: AccountStateResponse,
	consent: ConsentStateResponse | null,
	profile: PersonalProfile = EMPTY_PROFILE,
): AuthUser {
	return {
		id: state.id,
		email: state.email,
		username: state.username,
		isEmailVerified: state.email_verified,
		hasCompletedOnboarding: state.onboarding.completed,
		hasDataConsent: state.privacy_consent === true,
		dataConsentChangedAt: consent?.decided_at ?? null,
		isStaff: state.is_staff,
		deletionScheduledFor: state.deletion_scheduled_for,
		profile,
	}
}

/**
 * Adds the consent timestamp and the body data to the account state, since /auth/me returns
 * neither. Body data is health data and only exists with consent; without it the profile stays
 * empty.
 */
export async function withConsent(state: AccountStateResponse): Promise<AuthUser> {
	const [consent, body] = await Promise.all([
		apiRequest<ConsentStateResponse>('/privacy/consent').catch(() => null),
		state.privacy_consent === true
			? apiRequest<BodyProfileResponse>('/tracking/body').catch(() => null)
			: null,
	])

	return toAuthUser(state, consent, body ? toPersonalProfile(body) : EMPTY_PROFILE)
}

// The backend sets the tokens as httpOnly cookies; only the account state is returned here.
// Every function throws ApiError, e.g. for a wrong password (401 invalid_credentials) or an
// email address that is already registered (409 email_taken).

export async function login(credentials: Credentials): Promise<AuthUser> {
	const state = await apiRequest<AccountStateResponse>('/auth/login', {
		method: 'POST',
		body: credentials,
		skipRefresh: true,
	})

	return withConsent(state)
}

/** Also signs the user in and sends the email with the confirmation link */
export async function register(credentials: Credentials): Promise<AuthUser> {
	const state = await apiRequest<AccountStateResponse>('/auth/register', {
		method: 'POST',
		body: credentials,
		skipRefresh: true,
	})

	return toAuthUser(state, null)
}

export async function logout(): Promise<void> {
	await apiRequest('/auth/logout', { method: 'POST', skipRefresh: true })
}

/** Throws ApiError with status 401 when nobody is signed in */
export async function fetchCurrentUser(): Promise<AuthUser> {
	return withConsent(await apiRequest<AccountStateResponse>('/auth/me'))
}

/** The token comes from the link in the confirmation email */
export async function verifyEmail(token: string): Promise<void> {
	await apiRequest('/auth/email/verify', {
		method: 'POST',
		body: { token },
		skipRefresh: true,
	})
}

export async function resendVerificationEmail(): Promise<void> {
	await apiRequest('/auth/email/verification/resend', { method: 'POST' })
}

/** Always responds the same way, even if the address does not exist */
export async function requestPasswordReset(email: string): Promise<void> {
	await apiRequest('/auth/password/forgot', {
		method: 'POST',
		body: { email },
		skipRefresh: true,
	})
}

/** The token comes from the link in the email. The user has to sign in again afterwards. */
export async function resetPassword(token: string, newPassword: string): Promise<void> {
	await apiRequest('/auth/password/reset', {
		method: 'POST',
		body: { token, new_password: newPassword },
		skipRefresh: true,
	})
}
