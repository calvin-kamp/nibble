import type { RecipeSummary } from '@features/recipes/recipes.types'
import type { Ref } from 'vue'

import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { recipeParams } from '@features/recipes/recipes.utils'

/**
 * If the name in the path is wrong (title changed, link shortened), the page switches to the
 * correct address. replace, so Back does not land on the old address again.
 */
export function useCanonicalRecipeRoute(recipe: Ref<RecipeSummary | null | undefined>): void {
	const route = useRoute()
	const router = useRouter()

	watch(
		recipe,
		(current) => {
			if (!current) return

			const params = recipeParams(current)

			if (route.params.slug === params.slug) return

			router.replace({ name: route.name, params, query: route.query, hash: route.hash })
		},
		{ immediate: true },
	)
}
