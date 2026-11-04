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

export interface SavedMeal extends Nutrition {
	id: string
	name: string
	items: MealItem[]
}

export interface MealItemDraft {
	product: FoodProduct
	amount?: number
	unit?: FoodUnit
}

export interface MealFormValues {
	name: string
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
	items: MealItemResponse[]
	totals: MacrosResponse
}
