import type { PublicStats } from '@features/landing/landing.types'

import { apiRequest } from '@shared/api/client'

export async function fetchPublicStats(): Promise<PublicStats> {
	return apiRequest<PublicStats>('/stats')
}
