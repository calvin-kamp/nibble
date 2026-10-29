<script setup lang="ts">
import type { RecipeListView, RecipeSummary } from '@features/recipes/recipes.types'

import {
	BookmarkIcon,
	ChefHatIcon,
	PlusIcon,
	SearchIcon,
	SearchXIcon,
	SlidersHorizontalIcon,
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
	BaseEmptyState,
} from '@shared/ui'

import { useRecipeFilters } from '@features/recipes/composables/recipe-filters'
import { useBreakpoint } from '@shared/composables/breakpoint'

import { useAuthStore } from '@features/auth/auth.store'
import { searchRecipes } from '@features/recipes/recipes.api'
import {
	EMPTY_FILTERS,
	RECIPES_PAGE_SIZE as PAGE_SIZE,
	VIEW_QUERY,
} from '@features/recipes/recipes.constants'
import { countActiveFilters } from '@features/recipes/recipes.utils'

const auth = useAuthStore()

const { filters, page, view, reset } = useRecipeFilters()

// Own and saved recipes require signing in; guests always see all of them
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

// Filtering and paging happen in the backend; only the current page lives here
const visible = ref<RecipeSummary[]>([])
const total = ref<number>(0)
const loading = ref<boolean>(true)
const loadError = ref<boolean>(false)

// Collections only have the search, see isCollection
const activeFilters = computed(() =>
	isCollection.value ? { ...EMPTY_FILTERS, query: filters.value.query } : filters.value,
)

// Discard older responses once newer filters are set
let latestRequest = 0

// As a key, so only real changes trigger a request, not every new address
const requestKey = computed<string>(() =>
	JSON.stringify([activeView.value, activeFilters.value, page.value]),
)

watch(
	requestKey,
	async () => {
		const request = ++latestRequest

		loading.value = true
		loadError.value = false

		try {
			const result = await searchRecipes(activeView.value, activeFilters.value, page.value)

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

/** Every view starts on page 1 without search or filters */
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

// The search only writes to the address after a short pause, so the list and the announced
// match count do not change with every letter
const search = ref<string>(filters.value.query)
let searchTimer: ReturnType<typeof setTimeout> | undefined

watch(search, (value) => {
	clearTimeout(searchTimer)
	searchTimer = setTimeout(() => (filters.value = { ...filters.value, query: value }), 300)
})

// If the search changes from outside (reset, browser Back), sync the field
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

// From desktop up the filters sit below the search as a bar with popovers, below that in the drawer
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

// After paging, start at the top with the match count, which screen readers announce
const resultCount = ref<HTMLElement | null>(null)

watch(page, async () => {
	await nextTick()
	resultCount.value?.focus()
})
</script>

<template>
	<main class="content-wrapper flex flex-col gap-6 pt-6 pb-10">
		<div class="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
			<div class="flex flex-col gap-3">
				<h1>Rezepte</h1>

				<p class="max-w-3xl text-lg text-muted">{{ activeTab.intro }}</p>
			</div>

			<!-- Creating recipes requires an account -->
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

		<!-- An empty collection needs no search; it only explains how it fills up -->
		<section
			v-if="!isEmptyCollection"
			class="flex flex-col gap-3"
			:aria-label="isCollection ? 'Suche' : 'Suche und Filter'"
		>
			<div class="flex flex-wrap items-center gap-3">
				<!-- The label is for screen readers only; the magnifier and placeholder explain the field -->
				<form
					class="relative flex-1 min-w-0 xl:flex-none xl:w-full xl:max-w-md"
					role="search"
					@submit.prevent="applySearch"
				>
					<label
						for="recipe-search"
						class="sr-only"
						>{{ activeTab.searchLabel }}</label
					>

					<BaseIcon
						class="absolute left-4 top-1/2 -translate-y-1/2 text-muted pointer-events-none"
						:icon="SearchIcon"
					/>

					<input
						id="recipe-search"
						ref="searchInput"
						v-model="search"
						class="field__input pl-12 rounded-sm"
						type="search"
						:placeholder="activeTab.searchLabel"
						autocomplete="off"
					/>
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

						<span class="max-sm:sr-only">Filter</span>

						<span
							v-if="activeCount"
							class="inline-grid place-items-center min-w-6 h-6 px-1.5 rounded-full bg-brand text-sm tabular-nums text-on-brand"
						>
							{{ activeCount }}
							<span class="sr-only">aktiv</span>
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
						>Zurücksetzen</BaseButton
					>
				</BaseActions>
			</template>
		</BaseDrawer>

		<div class="flex flex-col gap-10">
			<div class="flex flex-col gap-4">
				<!-- Live region: the new match count is announced after every filter -->
				<p
					v-if="!isEmptyCollection"
					ref="resultCount"
					class="font-semibold text-ink-soft outline-none"
					role="status"
					tabindex="-1"
				>
					{{ resultLabel }}
				</p>

				<ul
					v-if="visible.length"
					class="grid grid-cols-12 gap-4"
					:aria-busy="loading"
				>
					<li
						v-for="(recipe, index) in visible"
						:key="recipe.id"
						class="col-span-12 md:col-span-6 xl:col-span-4"
					>
						<RecipeCard
							:recipe="recipe"
							:index="(page - 1) * PAGE_SIZE + index"
							:heading-level="2"
						/>
					</li>
				</ul>

				<!-- Empty own or saved list without search or filters: explain how it fills up -->
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

				<!-- Empty without search or filters: no recipe has been approved yet -->
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
