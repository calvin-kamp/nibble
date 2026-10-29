import type {
	FoodProduct,
	FoodQuantity,
	FoodUnit,
	FoodUnitResponse,
	MacrosResponse,
	Nutrition,
} from '@features/tracking/tracking.types'

/** Item of a meal. The product is kept so the amount can still be changed. */
export interface MealItem extends Nutrition {
	id: string
	product: FoodProduct
	quantity: FoodQuantity
}

/**
 * Saved meal that can be logged again with one click, e.g. the usual breakfast.
 * Its nutrition values are the sum of its items.
 */
export interface SavedMeal extends Nutrition {
	id: string
	name: string
	note?: string
	items: MealItem[]
}

/** One item in the form */
export interface MealItemDraft {
	product: FoodProduct
	amount?: number
	unit?: FoodUnit
}

export interface MealFormValues {
	name: string
	note?: string
	items: MealItemDraft[]
}

export interface MealItemResponse extends MacrosResponse {
	off_code: string
	food_name: string
	brand: string | null
	amount: number
	unit: FoodUnitResponse
	nutrition_per_100: MacrosResponse
	serving_quantity: number | null
}

export interface MealResponse {
	id: number
	name: string
	/** Empty without a note */
	note: string
	items: MealItemResponse[]
	totals: MacrosResponse
}
