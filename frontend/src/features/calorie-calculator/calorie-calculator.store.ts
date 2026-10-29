import type { CalorieCalculatorValues } from '@features/calorie-calculator/calorie-calculator.types'

import { defineStore } from 'pinia'
import { ref } from 'vue'

// Calculator details that a guest carries through registration into onboarding. Kept in memory
// only, never in browser storage: a reload or a closed tab ends them, onboarding then starts
// without prefill.
export const usePendingCalculationStore = defineStore('pending-calculation', () => {
	const values = ref<CalorieCalculatorValues | null>(null)

	function save(calculated: CalorieCalculatorValues): void {
		values.value = { ...calculated }
	}

	function clear(): void {
		values.value = null
	}

	return { values, save, clear }
})
