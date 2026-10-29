<script setup lang="ts">
import type { MealItem, SavedMeal } from '@features/meals/meals.types'

import { PencilIcon, PlusIcon, TrashIcon } from '@lucide/vue'
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import MealNotFound from '@features/meals/components/MealNotFound.vue'
import NutritionCard from '@features/tracking/components/NutritionCard.vue'
import {
	BaseAlertDialog,
	BaseBreadcrumb,
	BaseButton,
	BaseCard,
	BaseIcon,
	BaseLink,
} from '@shared/ui'

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

// undefined: still loading, null: does not exist
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

/** Brand and amount, e.g. "Hofmühle · 60 g" */
function itemDetail(item: MealItem): string {
	return [item.product.brand, formatQuantity(item.quantity)].filter(Boolean).join(' · ')
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
	<!-- Same structure as a recipe page: title with actions, nutrition values full width,
       below that the foods as a card on the left and the note on the right -->
	<main
		v-if="meal"
		class="content-wrapper flex flex-col gap-6 pt-4 pb-10"
	>
		<BaseBreadcrumb
			:items="[{ label: 'Meine Mahlzeiten', routeName: 'own-meals' }]"
			:current="meal.name"
		/>

		<!-- Buttons to the right of the title. Icon-only on phones; the text stays as the label for
         screen readers. -->
		<div class="flex items-start justify-between gap-4">
			<h1 class="min-w-0 wrap-break-word">{{ meal.name }}</h1>

			<div class="flex shrink-0 gap-2 md:gap-3">
				<BaseButton
					class="max-md:w-11 max-md:px-0"
					variant="outline"
					route-name="meal-edit"
					:params="{ id: meal.id }"
				>
					<BaseIcon :icon="PencilIcon" />

					<span class="max-md:sr-only">Bearbeiten</span>
				</BaseButton>

				<BaseButton
					class="max-md:w-11 max-md:px-0"
					@click="openEntry('food', { savedMealId: meal.id })"
				>
					<BaseIcon :icon="PlusIcon" />

					<span class="max-md:sr-only">Eintragen</span>
				</BaseButton>
			</div>
		</div>

		<NutritionCard
			title="Nährwerte der Mahlzeit"
			:nutrition="meal"
		/>

		<div class="grid grid-cols-12 gap-10 xl:items-start xl:gap-6">
			<BaseCard
				as="section"
				class="col-span-12 xl:col-span-5"
				aria-labelledby="meal-items-title"
			>
				<div class="flex flex-col gap-2">
					<h2
						id="meal-items-title"
						class="text-2xl"
					>
						Lebensmittel
					</h2>

					<ul class="data-list">
						<li
							v-for="item in meal.items"
							:key="item.id"
							class="data-list__row"
						>
							<span class="data-list__label">
								{{ item.product.name }}
								<span class="data-list__meta">{{ itemDetail(item) }}</span>
							</span>

							<span class="data-list__value">{{ formatNumber(item.kcal) }} kcal</span>
						</li>
					</ul>
				</div>
			</BaseCard>

			<section
				class="flex flex-col items-start gap-8 col-span-12 xl:col-span-7 xl:pt-5"
				aria-labelledby="meal-note-title"
			>
				<div class="flex flex-col items-start gap-4">
					<h2
						id="meal-note-title"
						class="text-2xl"
					>
						Notiz
					</h2>

					<p
						v-if="meal.note"
						class="max-w-prose text-base/relaxed "
					>
						{{ meal.note }}
					</p>

					<p
						v-else
						class="text-muted"
					>
						Noch keine Notiz. Unter
						<BaseLink
							route-name="meal-edit"
							:params="{ id: meal.id }"
							>Bearbeiten</BaseLink
						>
						kannst du z. B. festhalten, wie du sie zubereitest.
					</p>
				</div>

				<!-- Rarely needed, so it sits quietly at the end. A confirmation guards against accidents. -->
				<BaseButton
					class="-ml-6 text-danger"
					variant="ghost"
					@click="deleteOpen = true"
				>
					<BaseIcon :icon="TrashIcon" />
					Mahlzeit löschen
				</BaseButton>
			</section>
		</div>

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
