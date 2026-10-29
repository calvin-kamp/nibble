import type {
	Recipe,
	RecipeContent,
	RecipeDetailResponse,
	RecipeFilterValues,
	RecipeFormValues,
	RecipeInputResponse,
	RecipeListItemResponse,
	RecipeListView,
	RecipePage,
	RecipeSummary,
} from '@features/recipes/recipes.types'

import { kcalOf } from '@features/recipes/recipes.utils'
import { apiRequest, toQuery, type Paginated } from '@shared/api/client'

// Recipes live in the backend; new and changed ones go into moderation first. Every
// function throws ApiError, e.g. 404 for unknown recipes or other users' unapproved ones.

function toSummary(recipe: RecipeListItemResponse | RecipeDetailResponse): RecipeSummary {
	const { kcal, protein, carbs, fat } = recipe.nutrition_per_serving

	return {
		id: String(recipe.id),
		title: recipe.name,
		diet: recipe.diet ?? 'omnivore',
		durationMinutes: recipe.prep_time_minutes,
		kcalPerServing: Math.round(kcal),
		protein,
		carbs,
		fat,
		freeFrom: recipe.intolerances,
		equipment: recipe.equipment,
		mealTypes: recipe.meal_types,
		tags: recipe.properties,
		imageUrl: recipe.image_url ?? undefined,
		isSaved: recipe.is_saved,
		status: recipe.status,
		hasPendingRevision:
			'has_pending_revision' in recipe
				? recipe.has_pending_revision
				: recipe.pending_revision?.status === 'pending',
	}
}

export function toRecipeContent(recipe: RecipeInputResponse): RecipeContent {
	const { kcal, protein, carbs, fat } = recipe.nutrition_per_serving

	return {
		title: recipe.name,
		description: recipe.description || undefined,
		diet: recipe.diet ?? 'omnivore',
		durationMinutes: recipe.prep_time_minutes,
		servings: recipe.servings,
		kcalPerServing: Math.round(kcal),
		protein,
		carbs,
		fat,
		freeFrom: recipe.intolerances,
		equipment: recipe.equipment,
		mealTypes: recipe.meal_types,
		ingredients: recipe.ingredients.map(({ name, amount, unit }) => ({ name, amount, unit })),
		steps: recipe.steps
			.toSorted((a, b) => a.step_number - b.step_number)
			.map((step) => step.text),
	}
}

function toRecipe(recipe: RecipeDetailResponse): Recipe {
	const revision = recipe.pending_revision

	return {
		...toSummary(recipe),
		...toRecipeContent(recipe),
		isOwn: recipe.is_own === true,
		rejectionReason: recipe.rejection_reason,
		pendingRevision: revision
			? {
					status: revision.status,
					rejectionReason: revision.rejection_reason,
					imageUrl: revision.image_url ?? undefined,
					content: toRecipeContent(revision.content),
				}
			: null,
	}
}

function toInput(values: RecipeFormValues): RecipeInputResponse {
	return {
		name: values.title.trim(),
		description: values.description.trim(),
		prep_time_minutes: values.durationMinutes,
		diet: values.diet === 'omnivore' ? null : values.diet,
		intolerances: values.freeFrom,
		equipment: values.equipment,
		meal_types: values.mealTypes,
		servings: values.servings,
		nutrition_per_serving: {
			kcal: kcalOf(values),
			protein: values.protein,
			carbs: values.carbs,
			fat: values.fat,
		},
		// The form has already removed empty rows, so every ingredient has an amount
		ingredients: values.ingredients.map(({ name, amount, unit }) => ({
			name: name.trim(),
			amount: amount!,
			unit,
		})),
		steps: values.steps.map((text, index) => ({ step_number: index + 1, text: text.trim() })),
	}
}

/**
 * One page of the recipe list. Own and saved recipes require signing in; own recipes include
 * those not yet approved.
 */
export async function searchRecipes(
	view: RecipeListView,
	filters: RecipeFilterValues,
	page: number,
): Promise<RecipePage> {
	const query = toQuery({
		page: page > 1 ? page : undefined,
		q: filters.query.trim(),
		diet: filters.diet === 'omnivore' ? undefined : filters.diet,
		intolerances: filters.freeFrom,
		properties: filters.tags,
		equipment: filters.equipment,
		mine: view === 'own',
		saved: view === 'saved',
	})
	const { count, results } = await apiRequest<Paginated<RecipeListItemResponse>>(
		`/recipes${query}`,
	)

	return { recipes: results.map(toSummary), total: count }
}

export async function fetchRecipe(id: string): Promise<Recipe> {
	return toRecipe(await apiRequest<RecipeDetailResponse>(`/recipes/${id}`))
}

/** Upload, replace or remove the image, depending on what the form contains */
async function syncImage(
	recipe: RecipeDetailResponse,
	image: RecipeFormValues['image'],
): Promise<RecipeDetailResponse> {
	if (image instanceof File) {
		const body = new FormData()

		body.append('image', image)

		return apiRequest<RecipeDetailResponse>(`/recipes/${recipe.id}/image`, {
			method: 'PUT',
			body,
		})
	}

	const current = recipe.pending_revision ? recipe.pending_revision.image_url : recipe.image_url

	if (image === null && current) {
		return apiRequest<RecipeDetailResponse>(`/recipes/${recipe.id}/image`, { method: 'DELETE' })
	}

	return recipe
}

/** The recipe then waits for approval; until then only the author can see it */
export async function createRecipe(values: RecipeFormValues): Promise<Recipe> {
	const created = await apiRequest<RecipeDetailResponse>('/recipes', {
		method: 'POST',
		body: toInput(values),
	})

	return toRecipe(await syncImage(created, values.image))
}

/** For approved recipes the change becomes a proposal; the old version stays live */
export async function updateRecipe(id: string, values: RecipeFormValues): Promise<Recipe> {
	const updated = await apiRequest<RecipeDetailResponse>(`/recipes/${id}`, {
		method: 'PUT',
		body: toInput(values),
	})

	return toRecipe(await syncImage(updated, values.image))
}

export async function deleteRecipe(id: string): Promise<void> {
	await apiRequest(`/recipes/${id}`, { method: 'DELETE' })
}

/** Any approved recipe can be saved, including the user's own */
export async function setRecipeSaved(id: string, saved: boolean): Promise<void> {
	await apiRequest(`/recipes/${id}/saved`, { method: saved ? 'PUT' : 'DELETE' })
}
