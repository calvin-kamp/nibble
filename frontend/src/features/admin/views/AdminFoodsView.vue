<script setup lang="ts">
import type { MissingBarcode, ReportedFood } from '@features/admin/admin.types'

import { ChevronRightIcon, FlagIcon, PlusIcon, ScanBarcodeIcon } from '@lucide/vue'
import { computed, nextTick, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { BaseButton, BaseCard, BaseEmptyState, BaseIcon, BasePagination } from '@shared/ui'

import { fetchMissingBarcodes, fetchReportedFoods } from '@features/admin/admin.api'
import {
	FOOD_REPORT_REASON_LABELS,
	MISSING_BARCODES_PAGE_SIZE,
	REPORTED_FOODS_PAGE_SIZE,
} from '@features/admin/admin.constants'
import { formatTimestamp } from '@features/admin/admin.utils'
import { formatNumber } from '@shared/utils/number'

type FoodList = 'missing' | 'reported'

const route = useRoute()
const router = useRouter()

const LISTS: { value: FoodList; label: string; query: string | undefined }[] = [
	{ value: 'missing', label: 'Fehlende Barcodes', query: undefined },
	{ value: 'reported', label: 'Gemeldet', query: 'gemeldet' },
]

const list = computed<FoodList>(() => (route.query.liste === 'gemeldet' ? 'reported' : 'missing'))

const page = computed<number>({
	get: () => Math.max(Number(route.query.seite) || 1, 1),
	set: (value) =>
		router.push({ query: { ...route.query, seite: value > 1 ? String(value) : undefined } }),
})

const barcodes = ref<MissingBarcode[]>([])
const reported = ref<ReportedFood[]>([])
const total = ref<number>(0)
const loading = ref<boolean>(true)
const loadError = ref<boolean>(false)

watch(
	[list, page],
	async ([currentList, currentPage]) => {
		loading.value = true

		try {
			if (currentList === 'reported') {
				const result = await fetchReportedFoods(currentPage)

				reported.value = result.foods
				barcodes.value = []
				total.value = result.total
			} else {
				const result = await fetchMissingBarcodes(currentPage)

				barcodes.value = result.barcodes
				reported.value = []
				total.value = result.total
			}

			loadError.value = false
		} catch {
			barcodes.value = []
			reported.value = []
			total.value = 0
			loadError.value = true
		} finally {
			loading.value = false
		}
	},
	{ immediate: true },
)

const pageSize = computed<number>(() =>
	list.value === 'reported' ? REPORTED_FOODS_PAGE_SIZE : MISSING_BARCODES_PAGE_SIZE,
)

const resultLabel = computed<string>(() => {
	if (loading.value) return 'Wird geladen …'
	if (loadError.value) return 'Die Liste konnte nicht geladen werden. Lad die Seite neu.'

	if (list.value === 'reported') {
		if (!total.value) return 'Keine gemeldeten Lebensmittel'

		return total.value === 1
			? '1 gemeldetes Lebensmittel'
			: `${formatNumber(total.value)} gemeldete Lebensmittel`
	}

	if (!total.value) return 'Keine fehlenden Barcodes'

	return total.value === 1 ? '1 fehlender Barcode' : `${formatNumber(total.value)} fehlende Barcodes`
})

function lookupsLabel(lookups: number): string {
	return lookups === 1 ? '1-mal gesucht' : `${formatNumber(lookups)}-mal gesucht`
}

function reportsLabel(food: ReportedFood): string {
	const count = food.reportCount === 1 ? '1 Meldung' : `${formatNumber(food.reportCount)} Meldungen`
	const reasons = food.reasons.map((reason) => FOOD_REPORT_REASON_LABELS[reason]).join(', ')

	return `${count}: ${reasons}`
}

const resultCount = ref<HTMLElement | null>(null)

watch(page, async () => {
	await nextTick()
	resultCount.value?.focus()
})
</script>

<template>
	<main class="page">
		<div class="flex flex-col gap-3">
			<h1>
				Lebensmittel
			</h1>

			<p class="page__lead">
				Barcodes, zu denen die Suche nichts gefunden hat, und Lebensmittel, bei denen jemand
				einen Fehler gemeldet hat. Was du einträgst, steht sofort in nibble und landet auch
				bei Open Food Facts.
			</p>

			<BaseButton
				class="self-start"
				variant="outline"
				route-name="admin-food-generic"
			>
				<BaseIcon :icon="PlusIcon" />

				Lebensmittel ohne Barcode
			</BaseButton>
		</div>

		<section class="flex flex-col gap-6">
			<nav aria-label="Liste">
				<ul class="tabs">
					<li
						v-for="item in LISTS"
						:key="item.value"
					>
						<RouterLink
							:to="{ query: { liste: item.query } }"
							class="tabs__item"
							:aria-current="list === item.value ? 'page' : 'false'"
						>
							{{ item.label }}
						</RouterLink>
					</li>
				</ul>
			</nav>

			<div class="flex flex-col gap-4">
				<p
					ref="resultCount"
					class="font-semibold text-foreground/80 outline-none"
					role="status"
					tabindex="-1"
				>
					{{ resultLabel }}
				</p>

				<BaseCard v-if="barcodes.length">
					<ul
						class="data-list"
						:aria-busy="loading"
					>
						<li
							v-for="barcode in barcodes"
							:key="barcode.code"
						>
							<RouterLink
								:to="{ name: 'admin-food', params: { code: barcode.code } }"
								class="data-list__row data-list__row--link"
							>
								<span class="data-list__label">
									<span class="font-semibold text-foreground tabular-nums">
										{{ barcode.code }}
									</span>

									<span class="data-list__meta">
										{{ lookupsLabel(barcode.lookups) }}, zuletzt am

										<time :datetime="barcode.lastSearchedAt">
											{{ formatTimestamp(barcode.lastSearchedAt) }}
										</time>
									</span>
								</span>

								<BaseIcon
									class="text-muted-foreground"
									:icon="ChevronRightIcon"
								/>
							</RouterLink>
						</li>
					</ul>
				</BaseCard>

				<BaseCard v-else-if="reported.length">
					<ul
						class="data-list"
						:aria-busy="loading"
					>
						<li
							v-for="food in reported"
							:key="food.code"
						>
							<RouterLink
								:to="{ name: 'admin-food-correct', params: { code: food.code } }"
								class="data-list__row data-list__row--link"
							>
								<span class="data-list__label">
									<span class="font-semibold text-foreground">
										{{ food.name }}
									</span>

									<span class="data-list__meta">
										{{ food.brand ? `${food.brand} – ` : '' }}{{ reportsLabel(food) }}
									</span>
								</span>

								<BaseIcon
									class="text-muted-foreground"
									:icon="ChevronRightIcon"
								/>
							</RouterLink>
						</li>
					</ul>
				</BaseCard>

				<BaseEmptyState
					v-else-if="!loading && !loadError && list === 'missing'"
					:icon="ScanBarcodeIcon"
					title="Alles gefunden"
				>
					Sucht jemand einen Barcode, den nibble nicht kennt, taucht er hier auf.
				</BaseEmptyState>

				<BaseEmptyState
					v-else-if="!loading && !loadError"
					:icon="FlagIcon"
					title="Nichts gemeldet"
				>
					Meldet jemand falsche Werte bei einem Lebensmittel, taucht es hier auf.
				</BaseEmptyState>
			</div>

			<BasePagination
				v-if="total > pageSize"
				v-model:page="page"
				label="Seiten der Liste"
				:total="total"
				:items-per-page="pageSize"
			/>
		</section>
	</main>
</template>
