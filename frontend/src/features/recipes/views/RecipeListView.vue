<script setup lang="ts">
import type { RecipeListView, RecipeSummary } from '@features/recipes/recipes.types'

import {
	BookmarkIcon,
	ChefHatIcon,
	PlusIcon,
	SearchIcon,
	SearchXIcon,
	SlidersHorizontalIcon,
	XIcon,
} from '@lucide/vue'
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

import RecipeActiveFilters from '@features/recipes/components/RecipeActiveFilters.vue'
import RecipeCard from '@features/recipes/components/RecipeCard.vue'
import RecipeFilterBar from '@features/recipes/components/RecipeFilterBar.vue'
import RecipeFilters from '@features/recipes/components/RecipeFilters.vue'
import {
	BaseActions,
	BaseButton,
	BaseDrawer,
	BaseIcon,
	BasePagination,
	BaseSelect,
	BaseEmptyState,
} from '@shared/ui'

import { useRecipeFilters } from '@features/recipes/composables/recipe-filters'
import { useBreakpoint } from '@shared/composables/breakpoint'

import { useAuthStore } from '@features/auth/auth.store'
import { searchRecipes } from '@features/recipes/recipes.api'
import {
	EMPTY_FILTERS,
	RECIPES_PAGE_SIZE as PAGE_SIZE,
	SORT_OPTIONS,
	VIEW_QUERY,
} from '@features/recipes/recipes.constants'
import { countActiveFilters } from '@features/recipes/recipes.utils'

const auth = useAuthStore()

const { filters, page, view, sort, reset } = useRecipeFilters()

const TABS: { view: RecipeListView; label: string; intro: string; searchLabel: string }[] = [
	{
		view: 'all',
		label: 'Alle',
		intro: 'Gesunde Alternativen zu deinen Lieblingsgerichten, mit Nährwerten für jede Portion.',
		searchLabel: 'Rezepte suchen',
	},
	{
		view: 'own',
		label: 'Eigene',
		intro: 'Rezepte, die du selbst angelegt hast. Nur du kannst sie bearbeiten.',
		searchLabel: 'In eigenen Rezepten suchen',
	},
	{
		view: 'saved',
		label: 'Gespeichert',
		intro: 'Rezepte, die du dir gemerkt hast, alle an einem Ort.',
		searchLabel: 'In gespeicherten Rezepten suchen',
	},
]

const activeView = computed<RecipeListView>(() => (auth.isLoggedIn ? view.value : 'all'))
const activeTab = computed(() => TABS.find((tab) => tab.view === activeView.value)!)

// Own and saved collections are small. They only get the search; filters would quickly turn
// a handful of recipes into an empty list.
const isCollection = computed<boolean>(() => activeView.value !== 'all')

const visible = ref<RecipeSummary[]>([])
const total = ref<number>(0)
const loading = ref<boolean>(true)
const loadError = ref<boolean>(false)

const activeFilters = computed(() =>
	isCollection.value ? { ...EMPTY_FILTERS, query: filters.value.query } : filters.value,
)

let latestRequest = 0

// As a key, so only real changes trigger a request, not every new address
const requestKey = computed<string>(() =>
	JSON.stringify([activeView.value, activeFilters.value, page.value, sort.value]),
)

watch(
	requestKey,
	async () => {
		const request = ++latestRequest

		loading.value = true
		loadError.value = false

		try {
			const result = await searchRecipes(
				activeView.value,
				activeFilters.value,
				page.value,
				sort.value,
			)

			if (request !== latestRequest) return

			visible.value = result.recipes
			total.value = result.total
		} catch {
			if (request !== latestRequest) return

			visible.value = []
			total.value = 0
			loadError.value = true
		} finally {
			if (request === latestRequest) loading.value = false
		}
	},
	{ immediate: true },
)

// An empty collection is recognized by getting nothing back without a search
const isEmptyCollection = computed<boolean>(
	() =>
		isCollection.value &&
		!loading.value &&
		!loadError.value &&
		!filters.value.query &&
		total.value === 0,
)

function tabLocation(tab: RecipeListView) {
	return { query: { ansicht: VIEW_QUERY[tab] } }
}

const pageCount = computed<number>(() => Math.max(Math.ceil(total.value / PAGE_SIZE), 1))

const activeCount = computed<number>(() => countActiveFilters(filters.value))

const countLabel = computed<string>(() => {
	const count = total.value

	if (!count) return 'Keine Rezepte'

	return count === 1 ? '1 Rezept' : `${count} Rezepte`
})

const resultLabel = computed<string>(() => {
	if (loading.value) return 'Rezepte werden geladen …'
	if (loadError.value) return 'Die Rezepte konnten nicht geladen werden. Lad die Seite bitte neu.'

	return countLabel.value
})

const search = ref<string>(filters.value.query)
let searchTimer: ReturnType<typeof setTimeout> | undefined

watch(search, (value) => {
	clearTimeout(searchTimer)
	searchTimer = setTimeout(() => (filters.value = { ...filters.value, query: value }), 300)
})

watch(
	() => filters.value.query,
	(query) => {
		if (query !== search.value.trim()) search.value = query
	},
)

onBeforeUnmount(() => clearTimeout(searchTimer))

function applySearch(): void {
	clearTimeout(searchTimer)
	filters.value = { ...filters.value, query: search.value }
}

const searchInput = ref<HTMLInputElement | null>(null)

// Own clear button instead of the browser's, which looks different in every browser and is
// missing in Firefox
function clearSearch(): void {
	search.value = ''
	applySearch()
	searchInput.value?.focus()
}

const { isDesktop } = useBreakpoint()

const drawerOpen = ref<boolean>(false)

// Without a DrawerTrigger the drawer does not know where it came from, so on close focus is
// explicitly returned to the filter button.
const filterButton = ref<InstanceType<typeof BaseButton> | null>(null)

function onDrawerCloseAutoFocus(event: Event): void {
	event.preventDefault()

	const element = filterButton.value?.$el as HTMLElement | undefined

	element?.focus()
}

const resultCount = ref<HTMLElement | null>(null)

watch(page, async () => {
	await nextTick()
	resultCount.value?.focus()
})
</script>

<template>
	<main class="page">
		<div class="page__header">
			<div class="page__intro">
				<h1>
					Rezepte
				</h1>

				<p class="page__lead">
					{{ activeTab.intro }}
				</p>
			</div>

			<BaseButton
				v-if="auth.isLoggedIn"
				route-name="recipe-create"
			>
				<BaseIcon :icon="PlusIcon" />

				Rezept anlegen
			</BaseButton>
		</div>

		<nav
			v-if="auth.isLoggedIn"
			aria-label="Ansicht"
		>
			<ul class="tabs">
				<li
					v-for="tab in TABS"
					:key="tab.view"
				>
					<RouterLink
						:to="tabLocation(tab.view)"
						class="tabs__item"
						:aria-current="activeView === tab.view ? 'page' : 'false'"
					>
						{{ tab.label }}
					</RouterLink>
				</li>
			</ul>
		</nav>

		<section
			v-if="!isEmptyCollection"
			class="flex flex-col gap-3"
			:aria-label="isCollection ? 'Suche' : 'Suche und Filter'"
		>
			<div class="flex flex-wrap items-center gap-3">
				<form
					class="relative flex-1 min-w-0 xl:flex-none xl:w-full xl:max-w-md"
					role="search"
					@submit.prevent="applySearch"
				>
					<label
						for="recipe-search"
						class="sr-only"
					>
						{{ activeTab.searchLabel }}
					</label>

					<BaseIcon
						class="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
						:icon="SearchIcon"
					/>

					<input
						id="recipe-search"
						ref="searchInput"
						v-model="search"
						class="field__input pl-12 pr-14 rounded-sm"
						type="search"
						:placeholder="activeTab.searchLabel"
						autocomplete="off"
						@keydown.esc="search && clearSearch()"
					/>

					<button
						v-if="search"
						type="button"
						class="field__action absolute right-0.5 top-1/2 -translate-y-1/2"
						aria-label="Suche leeren"
						@click="clearSearch"
					>
						<BaseIcon
							:icon="XIcon"
							:size="18"
						/>
					</button>
				</form>

				<template v-if="!isCollection">
					<RecipeFilterBar
						v-if="isDesktop"
						v-model="filters"
					/>

					<BaseButton
						v-else
						ref="filterButton"
						class="min-h-12 rounded-sm"
						variant="outline"
						aria-haspopup="dialog"
						:aria-expanded="drawerOpen"
						aria-controls="recipe-filter-drawer"
						@click="drawerOpen = true"
					>
						<BaseIcon :icon="SlidersHorizontalIcon" />

						<span class="max-sm:sr-only">
							Filter
						</span>

						<span
							v-if="activeCount"
							class="inline-grid place-items-center min-w-6 h-6 px-1.5 rounded-full bg-primary text-md tabular-nums text-primary-foreground"
						>
							{{ activeCount }}

							<span class="sr-only">
								aktiv
							</span>
						</span>
					</BaseButton>
				</template>
			</div>

			<RecipeActiveFilters
				v-if="!isCollection"
				v-model="filters"
				@cleared="searchInput?.focus()"
			/>
		</section>

		<BaseDrawer
			v-if="!isDesktop && !isCollection"
			id="recipe-filter-drawer"
			v-model:open="drawerOpen"
			class="max-h-[85svh]"
			title="Filter"
			@close-auto-focus="onDrawerCloseAutoFocus"
		>
			<RecipeFilters v-model="filters" />

			<template #footer>
				<BaseActions>
					<BaseButton @click="drawerOpen = false">
						{{ total ? `${countLabel} anzeigen` : 'Keine Rezepte gefunden' }}
					</BaseButton>

					<BaseButton
						variant="ghost"
						:disabled="!activeCount"
						@click="reset"
					>
						Zurücksetzen
					</BaseButton>
				</BaseActions>
			</template>
		</BaseDrawer>

		<div class="flex flex-col gap-10">
			<div class="flex flex-col gap-4">
				<div
					v-if="!isEmptyCollection"
					class="flex flex-wrap items-center justify-between gap-x-6 gap-y-3"
				>
					<p
						ref="resultCount"
						class="font-semibold text-foreground/80 outline-none"
						role="status"
						tabindex="-1"
					>
						{{ resultLabel }}
					</p>

					<div class="flex items-center gap-3">
						<label
							for="recipe-sort"
							class="field__label shrink-0"
						>
							Sortieren nach
						</label>

						<BaseSelect
							id="recipe-sort"
							v-model="sort"
							class="w-44"
							:options="SORT_OPTIONS"
						/>
					</div>
				</div>

				<ul
					v-if="visible.length"
					class="grid grid-cols-12 gap-4"
					:aria-busy="loading"
				>
					<li
						v-for="(recipe, index) in visible"
						:key="recipe.id"
						class="col-span-12 md:col-span-6 lg:col-span-4"
					>
						<RecipeCard
							:recipe="recipe"
							:index="(page - 1) * PAGE_SIZE + index"
							:heading-level="2"
						/>
					</li>
				</ul>

				<BaseEmptyState
					v-else-if="isEmptyCollection"
					:icon="activeView === 'own' ? ChefHatIcon : BookmarkIcon"
					:title="
						activeView === 'own'
							? 'Noch keine eigenen Rezepte'
							: 'Noch nichts gespeichert'
					"
				>
					{{
						activeView === 'own'
							? 'Rezepte, die du anlegst, findest du hier.'
							: 'Speichere Rezepte, die dir gefallen. Hier hast du sie dann alle beisammen.'
					}}

					<template #actions>
						<BaseButton
							v-if="activeView === 'own'"
							route-name="recipe-create"
						>
							<BaseIcon :icon="PlusIcon" />

							Rezept anlegen
						</BaseButton>

						<BaseButton
							v-else
							variant="outline"
							:query="{}"
							route-name="recipe-list"
						>
							Alle Rezepte ansehen
						</BaseButton>
					</template>
				</BaseEmptyState>

				<BaseEmptyState
					v-else-if="
						!loading && !loadError && !isCollection && !activeCount && !filters.query
					"
					:icon="ChefHatIcon"
					title="Noch keine Rezepte"
				>
					Sobald die ersten Rezepte freigegeben sind, findest du sie hier.

					<template
						v-if="auth.isLoggedIn"
						#actions
					>
						<BaseButton route-name="recipe-create">
							<BaseIcon :icon="PlusIcon" />

							Rezept anlegen
						</BaseButton>
					</template>
				</BaseEmptyState>

				<BaseEmptyState
					v-else-if="!loading && !loadError"
					:icon="SearchXIcon"
					title="Nichts gefunden"
				>
					{{
						isCollection
							? 'Probier ein anderes Suchwort.'
							: 'Probier ein anderes Suchwort oder nimm einen Filter heraus.'
					}}

					<template #actions>
						<BaseButton @click="reset">
							{{
								isCollection
									? 'Suche zurücksetzen'
									: 'Suche und Filter zurücksetzen'
							}}
						</BaseButton>
					</template>
				</BaseEmptyState>
			</div>

			<BasePagination
				v-if="pageCount > 1"
				v-model:page="page"
				label="Seiten der Rezeptliste"
				:total="total"
				:items-per-page="PAGE_SIZE"
			/>
		</div>
	</main>
</template>
