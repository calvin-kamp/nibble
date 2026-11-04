<script setup lang="ts">
import type { MealItem, SavedMeal } from '@features/meals/meals.types'

import { PencilIcon, PlusIcon, TrashIcon } from '@lucide/vue'
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import MealNotFound from '@features/meals/components/MealNotFound.vue'
import MacroList from '@features/tracking/components/MacroList.vue'
import NutritionCard from '@features/tracking/components/NutritionCard.vue'
import { BaseAlertDialog, BaseBreadcrumb, BaseButton, BaseCard, BaseIcon } from '@shared/ui'

import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { usePageTitle } from '@shared/composables/page-title'
import { useToast } from '@shared/composables/toast'

import { deleteMeal, fetchMeal } from '@features/meals/meals.api'
import { formatQuantity } from '@features/tracking/tracking.utils'
import { formatNumber } from '@shared/utils/number'

interface Props {
	id: string
}

const props = defineProps<Props>()

const router = useRouter()
const toast = useToast()
const { openEntry } = useTrackingDialogs()

const meal = ref<SavedMeal | null | undefined>(undefined)

usePageTitle(() => meal.value?.name)

watch(
	() => props.id,
	async (id) => {
		meal.value = undefined

		try {
			meal.value = await fetchMeal(id)
		} catch {
			meal.value = null
		}
	},
	{ immediate: true },
)

function itemDetail(item: MealItem): string {
	return [item.product.brand, formatQuantity(item.quantity)].filter(Boolean).join(' – ')
}

const deleteOpen = ref<boolean>(false)

async function confirmDelete(): Promise<void> {
	if (!meal.value) return

	const { name } = meal.value

	// Go to the list first, otherwise "Mahlzeit nicht gefunden" would flash on the page
	await router.push({ name: 'own-meals' })

	try {
		await deleteMeal(props.id)
		toast.show(`${name} gelöscht`, 'info')
	} catch {
		toast.show(
			'Die Mahlzeit konnte nicht gelöscht werden. Versuch es bitte noch einmal.',
			'danger',
		)
	}
}
</script>

<template>
	<main
		v-if="meal"
		class="page page--compact"
	>
		<BaseBreadcrumb
			:items="[{ label: 'Meine Mahlzeiten', routeName: 'own-meals' }]"
			:current="meal.name"
		/>

		<div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
			<h1 class="min-w-0 wrap-break-word">
				{{ meal.name }}
			</h1>

			<div class="flex shrink-0 gap-2 md:gap-3">
				<BaseButton
					class="max-md:w-11 max-md:px-0"
					variant="outline"
					route-name="meal-edit"
					:params="{ id: meal.id }"
				>
					<BaseIcon :icon="PencilIcon" />

					<span class="max-md:sr-only">
						Bearbeiten
					</span>
				</BaseButton>

				<BaseButton
					class="w-11 px-0"
					variant="danger-soft"
					aria-label="Mahlzeit löschen"
					@click="deleteOpen = true"
				>
					<BaseIcon :icon="TrashIcon" />
				</BaseButton>

				<BaseButton
					class="max-md:w-11 max-md:px-0"
					@click="openEntry('food', { savedMealId: meal.id })"
				>
					<BaseIcon :icon="PlusIcon" />

					<span class="max-md:sr-only">
						Eintragen
					</span>
				</BaseButton>
			</div>
		</div>

		<NutritionCard
			title="Nährwerte der Mahlzeit"
			:nutrition="meal"
		/>

		<BaseCard
			as="section"
			aria-labelledby="meal-items-title"
		>
			<div class="flex flex-col gap-2">
				<h2
					id="meal-items-title"
					class="card__title"
				>
					Lebensmittel
				</h2>

				<ul class="data-list">
					<li
						v-for="item in meal.items"
						:key="item.id"
						class="data-list__row flex-col items-stretch gap-2"
					>
						<div class="flex items-start justify-between gap-4">
							<span class="data-list__label">
								<span class="font-semibold text-foreground">
									{{
										item.product.name
									}}
								</span>

								<span class="data-list__meta">
									{{ itemDetail(item) }}
								</span>
							</span>

							<span class="data-list__value">
								{{ formatNumber(item.kcal) }} kcal
							</span>
						</div>

						<MacroList
							inline
							:macros="item"
						/>
					</li>
				</ul>
			</div>
		</BaseCard>

		<BaseAlertDialog
			v-model:open="deleteOpen"
			title="Mahlzeit löschen?"
			:description="`${meal.name} verschwindet aus deinen Mahlzeiten. Einträge im Tagebuch bleiben.`"
			confirm-label="Löschen"
			variant="danger"
			@confirm="confirmDelete"
		/>
	</main>

	<main
		v-else-if="meal === null"
		class="content-wrapper"
	>
		<MealNotFound />
	</main>

	<main
		v-else
		class="content-wrapper"
		aria-busy="true"
	/>
</template>
