import type { AuthUser } from '@features/auth/auth.types'
import type {
	OnboardingData,
	OnboardingProgress,
	OnboardingStateResponse,
	OnboardingStep,
} from '@features/onboarding/onboarding.types'

import { toApiGoal } from '@features/account/account.api'
import { fetchCurrentUser } from '@features/auth/auth.api'
import { PRIVACY_POLICY_VERSION } from '@features/legal/legal.constants'
import { saveWeightEntry } from '@features/tracking/tracking.api'
import { apiRequest } from '@shared/api/client'
import { toIsoDate } from '@shared/utils/date'

// The backend only knows the coarse steps (username, consent, goal, targets, summary). What the
// user entered on the way lives in memory (onboarding store) and is saved on completion. The
// functions throw on errors.

// Step keys as they appear in the address, see OnboardingFlow
const RESUME_STEP: Record<OnboardingStep, string> = {
	username: 'benutzername',
	consent: 'datenschutz',
	goal: 'ziel',
	targets: 'bedarf',
	summary: 'fertig',
}

/**
 * Where to continue after a reload, when nothing is left in memory: at the backend's step, with
 * the username and consent the account already has. Everything else is entered again.
 */
export async function loadOnboardingProgress(user: AuthUser): Promise<OnboardingProgress> {
	const state = await apiRequest<OnboardingStateResponse>('/onboarding')

	return {
		step: RESUME_STEP[state.current_step],
		consentAnswered: user.dataConsentChangedAt !== null,
		data: { username: user.username ?? '', consent: user.hasDataConsent },
	}
}

/** The user's own username counts as available. Throws ApiError, e.g. for an invalid format. */
export async function isUsernameAvailable(username: string): Promise<boolean> {
	const { available } = await apiRequest<{ available: boolean }>(
		`/profile/username-availability?username=${encodeURIComponent(username)}`,
	)

	return available
}

/**
 * Saves username, consent, body data, goal and daily needs via the individual endpoints and completes
 * onboarding. The backend advances step by step on its own.
 * Throws ApiError, e.g. 409 username_taken for a username that is already taken.
 */
export async function completeOnboarding(data: OnboardingData): Promise<AuthUser> {
	await apiRequest('/profile', { method: 'PATCH', body: { username: data.username } })

	await apiRequest('/privacy/consent', {
		method: 'PUT',
		body: { accepted: data.consent, policy_version: PRIVACY_POLICY_VERSION },
	})

	// Health data, so only now that the consent is saved
	const { birthDate, sex, heightCm, weightKg } = (data.consent && data.body) || {}

	if (birthDate || sex || heightCm) {
		await apiRequest('/tracking/body', {
			method: 'PATCH',
			body: {
				...(birthDate && { birth_date: birthDate }),
				...(sex && { sex }),
				...(heightCm && { height_cm: heightCm }),
			},
		})
	}

	// The first entry in the weight diary
	if (weightKg) await saveWeightEntry({ date: toIsoDate(), kg: weightKg })

	if (data.consent && (data.goal || data.needs)) {
		const { kcal, protein, carbs, fat } = data.needs ?? {}

		await apiRequest('/tracking/goal', {
			method: 'PATCH',
			body: {
				...(data.goal && { goal: toApiGoal(data.goal) }),
				...(data.needs && { targets: { kcal, protein, carbs, fat } }),
			},
		})
	}

	// Without daily needs ("später"), the backend stays at the targets step
	const state = await apiRequest<OnboardingStateResponse>('/onboarding')

	if (state.current_step !== 'summary') {
		await apiRequest('/onboarding', { method: 'PATCH', body: { current_step: 'summary' } })
	}

	await apiRequest('/onboarding/complete', { method: 'POST' })

	return fetchCurrentUser()
}
