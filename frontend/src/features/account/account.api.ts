import type {
	GoalResponse,
	GoalStateResponse,
	NutritionSettings,
} from '@features/account/account.types'
import type { AuthUser, BodyProfileResponse, PersonalProfile } from '@features/auth/auth.types'
import type { Goal } from '@features/calorie-calculator/calorie-calculator.types'

import { fetchCurrentUser, toPersonalProfile } from '@features/auth/auth.api'
import { PRIVACY_POLICY_VERSION } from '@features/legal/legal.constants'
import { apiRequest } from '@shared/api/client'

// Every function throws ApiError, e.g. for a wrong password (400 with errors.current_password)
// or a username that is already taken (409 username_taken).

const GOAL_TO_API: Record<Goal, GoalResponse> = { diet: 'lose', maintain: 'maintain', gain: 'gain' }

const GOAL_FROM_API: Record<GoalResponse, Goal> = {
	lose: 'diet',
	maintain: 'maintain',
	gain: 'gain',
}

export function toApiGoal(goal: Goal): GoalResponse {
	return GOAL_TO_API[goal]
}

export async function updateUsername(username: string): Promise<AuthUser> {
	await apiRequest('/profile', { method: 'PATCH', body: { username } })

	return fetchCurrentUser()
}

/**
 * Sends the confirmation link to the new address and a notice to the current one. The new
 * address only applies once the link has been opened, see confirmEmailChange.
 */
export async function changeEmail(email: string, password: string): Promise<void> {
	await apiRequest('/auth/email/change', { method: 'POST', body: { email, password } })
}

/** The token comes from the link in the email to the new address; works without signing in */
export async function confirmEmailChange(token: string): Promise<void> {
	await apiRequest('/auth/email/change/confirm', {
		method: 'POST',
		body: { token },
		skipRefresh: true,
	})
}

/** The current session receives new cookies, every other session is signed out */
export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
	await apiRequest('/auth/password/change', {
		method: 'POST',
		body: { current_password: currentPassword, new_password: newPassword },
	})
}

/**
 * Revoking deletes all health data in the backend immediately, so always ask first. Every
 * decision is added to the backend's consent history with the policy version, revoking too.
 */
export async function updateDataConsent(consent: boolean): Promise<AuthUser> {
	await apiRequest('/privacy/consent', {
		method: 'PUT',
		body: { accepted: consent, policy_version: PRIVACY_POLICY_VERSION },
	})

	return fetchCurrentUser()
}

/**
 * Personal details, individually or together. Health data, so the backend only stores them with
 * consent (403 consent_required otherwise) and deletes them on revoke.
 */
export async function updateProfile(
	user: AuthUser,
	patch: Partial<PersonalProfile>,
): Promise<AuthUser> {
	const body = await apiRequest<BodyProfileResponse>('/tracking/body', {
		method: 'PATCH',
		body: {
			...('birthDate' in patch && { birth_date: patch.birthDate }),
			...('heightCm' in patch && { height_cm: patch.heightCm }),
			...('sex' in patch && { sex: patch.sex }),
		},
	})

	return { ...user, profile: toPersonalProfile(body) }
}

/** null until daily needs have been saved */
export async function fetchNutritionSettings(): Promise<NutritionSettings | null> {
	const { goal, targets } = await apiRequest<GoalStateResponse>('/tracking/goal')

	if (!targets) return null

	return {
		needs: {
			kcal: targets.kcal,
			protein: targets.protein,
			carbs: targets.carbs,
			fat: targets.fat,
		},
		goal: goal ? GOAL_FROM_API[goal] : null,
	}
}

/** Applies from today, earlier days keep their values */
export async function saveNutritionSettings(settings: NutritionSettings): Promise<void> {
	const { kcal, protein, carbs, fat } = settings.needs

	await apiRequest('/tracking/goal', {
		method: 'PATCH',
		body: {
			...(settings.goal && { goal: GOAL_TO_API[settings.goal] }),
			targets: { kcal, protein, carbs, fat },
		},
	})
}

/** All data as a JSON file, see ExportDocument in the backend's openapi.yaml */
export async function exportData(): Promise<Blob> {
	const data = await apiRequest<unknown>('/account/export')

	return new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
}

/**
 * Requests deletion. It becomes final after 7 days and can be cancelled from the account until
 * then. Returns the time of deletion.
 */
export async function requestAccountDeletion(password: string): Promise<string> {
	const { scheduled_for } = await apiRequest<{ scheduled_for: string }>('/account/deletion', {
		method: 'POST',
		body: { password },
	})

	return scheduled_for
}

export async function cancelAccountDeletion(): Promise<AuthUser> {
	await apiRequest('/account/deletion', { method: 'DELETE' })

	return fetchCurrentUser()
}
