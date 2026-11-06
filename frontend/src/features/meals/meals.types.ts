import type {
	FoodProduct,
	FoodQuantity,
	FoodUnit,
	FoodUnitResponse,
	MacrosResponse,
	ManualFood,
	Nutrition,
} from '@features/tracking/tracking.types'

/**
 * Item of a meal. A product is kept so the amount can still be changed; an own item ("Eigener
 * Posten") has only its name and values, without product and amount.
 */
export interface MealItem extends Nutrition {
	id: string
	name: string
	product?: FoodProduct
	quantity?: FoodQuantity
}

export interface SavedMeal extends Nutrition {
	id: string
	name: string
	items: MealItem[]
}

/** A product with amount, or an own item with name and values (own) */
export interface MealItemDraft {
	product?: FoodProduct
	amount?: number
	unit?: FoodUnit
	/** withMacros only lives in the form: macros typed in, or kcal alone with macros at 0 */
	own?: Partial<ManualFood> & { withMacros?: boolean }
}

export interface MealFormValues {
	name: string
	items: MealItemDraft[]
}

export interface MealItemResponse extends MacrosResponse {
	/** null for an own item */
	off_code: string | null
	food_name: string
	brand: string | null
	amount: number
	unit: FoodUnitResponse
	/** null for an own item */
	nutrition_per_100: MacrosResponse | null
	serving_quantity: number | null
}

export interface MealResponse {
	id: number
	name: string
	items: MealItemResponse[]
	totals: MacrosResponse
}
