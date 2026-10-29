/** Public totals for the landing page, up to 10 minutes old */
export interface PublicStats {
	/** Active accounts */
	users: number
	/** Approved recipes */
	recipes: number
	/** Foods in the Open Food Facts data set */
	foods: number
	/** Diary entries across all users */
	entries: number
}
