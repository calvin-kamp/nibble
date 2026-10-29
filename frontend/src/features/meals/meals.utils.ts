import type { MealFormValues, MealItemDraft, SavedMeal } from '@features/meals/meals.types'
import type { Nutrition } from '@features/tracking/tracking.types'

import { nutritionFor, toQuantity } from '@features/tracking/tracking.utils'

const round1 = (value: number) => Math.round(value * 10) / 10

/** Sum of the nutrition values, macros to one decimal place */
export function sumNutrition(items: Nutrition[]): Nutrition {
	return items.reduce<Nutrition>(
		(total, item) => ({
			kcal: total.kcal + item.kcal,
			protein: round1(total.protein + item.protein),
			carbs: round1(total.carbs + item.carbs),
			fat: round1(total.fat + item.fat),
		}),
		{ kcal: 0, protein: 0, carbs: 0, fat: 0 },
	)
}

/** Nutrition values of a form item, null while the amount is missing */
export function draftNutrition(draft: MealItemDraft): Nutrition | null {
	if (!draft.amount || !draft.unit) return null

	return nutritionFor(draft.product, toQuantity(draft.product, draft.amount, draft.unit).base)
}

export function toFormValues(meal: SavedMeal): MealFormValues {
	return {
		name: meal.name,
		note: meal.note,
		items: meal.items.map((item) => ({
			product: item.product,
			amount: item.quantity.value,
			unit: item.quantity.unit,
		})),
	}
}
