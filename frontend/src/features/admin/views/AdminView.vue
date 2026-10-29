<script setup lang="ts">
import type { SubmissionStatus, SubmissionSummary } from '@features/admin/admin.types'
import type { PublicStats } from '@features/landing/landing.types'

import { ChevronRightIcon, InboxIcon } from '@lucide/vue'
import { computed, nextTick, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { BaseCard, BaseEmptyState, BaseIcon, BasePagination } from '@shared/ui'

import { fetchSubmissions } from '@features/admin/admin.api'
import {
	STATUS_QUERY,
	SUBMISSION_KIND_LABELS,
	SUBMISSION_STATUS_LABELS,
	SUBMISSIONS_PAGE_SIZE,
} from '@features/admin/admin.constants'
import { formatTimestamp, statusFromQuery } from '@features/admin/admin.utils'
import { fetchPublicStats } from '@features/landing/landing.api'
import { formatNumber } from '@shared/utils/number'

const route = useRoute()
const router = useRouter()

const STATUSES: SubmissionStatus[] = ['pending', 'approved', 'rejected']

const EMPTY_STATES: Record<SubmissionStatus, { title: string; text: string }> = {
	pending: {
		title: 'Alles erledigt',
		text: 'Neue Rezepte und Änderungen tauchen hier auf, sobald jemand etwas einreicht.',
	},
	approved: { title: 'Noch nichts freigegeben', text: 'Freigegebene Einreichungen stehen hier.' },
	rejected: { title: 'Noch nichts abgelehnt', text: 'Abgelehnte Einreichungen stehen hier.' },
}

// Status and page live in the address, so Back and reloading keep the place
const status = computed<SubmissionStatus>(() => statusFromQuery(route.query))

const page = computed<number>({
	get: () => Math.max(Number(route.query.seite) || 1, 1),
	set: (value) =>
		router.push({ query: { ...route.query, seite: value > 1 ? String(value) : undefined } }),
})

function statusLocation(value: SubmissionStatus) {
	return { query: { status: STATUS_QUERY[value] } }
}

const submissions = ref<SubmissionSummary[]>([])
const total = ref<number>(0)
const loading = ref<boolean>(true)
const loadError = ref<boolean>(false)

watch(
	[status, page],
	async ([currentStatus, currentPage]) => {
		loading.value = true

		try {
			const result = await fetchSubmissions(currentStatus, currentPage)

			submissions.value = result.submissions
			total.value = result.total
			loadError.value = false
		} catch {
			submissions.value = []
			total.value = 0
			loadError.value = true
		} finally {
			loading.value = false
		}
	},
	{ immediate: true },
)

const resultLabel = computed<string>(() => {
	if (loading.value) return 'Einreichungen werden geladen …'
	if (loadError.value) return 'Die Einreichungen konnten nicht geladen werden. Lad die Seite neu.'
	if (!total.value) return 'Keine Einreichungen'

	return total.value === 1 ? '1 Einreichung' : `${formatNumber(total.value)} Einreichungen`
})

// After paging, start at the top with the count, which screen readers announce
const resultCount = ref<HTMLElement | null>(null)

watch(page, async () => {
	await nextTick()
	resultCount.value?.focus()
})

// Totals as on the landing page, up to 10 minutes old
const stats = ref<PublicStats | null>(null)

fetchPublicStats()
	.then((result) => (stats.value = result))
	.catch(() => (stats.value = null))

const statItems = computed(() =>
	stats.value
		? [
				{ label: 'Aktive Konten', value: stats.value.users },
				{ label: 'Freigegebene Rezepte', value: stats.value.recipes },
				{ label: 'Lebensmittel', value: stats.value.foods },
				{ label: 'Tagebucheinträge', value: stats.value.entries },
			]
		: [],
)
</script>

<template>
	<main class="content-wrapper flex flex-col gap-8 pt-6 pb-10">
		<div class="flex flex-col gap-3">
			<h1>Verwaltung</h1>

			<p class="max-w-3xl text-lg text-muted">
				Neue Rezepte und Änderungen an freigegebenen Rezepten warten hier auf deine Prüfung.
				Die älteste Einreichung steht oben.
			</p>
		</div>

		<section
			v-if="statItems.length"
			aria-labelledby="admin-stats-title"
		>
			<h2
				id="admin-stats-title"
				class="sr-only"
			>
				Zahlen
			</h2>

			<dl class="grid grid-cols-12 gap-4">
				<div
					v-for="item in statItems"
					:key="item.label"
					class="flex flex-col gap-1 col-span-6 p-4 rounded-lg bg-surface md:px-5 xl:col-span-3"
				>
					<dt class="text-sm text-muted">
						{{ item.label }}
					</dt>

					<dd class="font-display text-3xl font-extrabold tabular-nums">
						{{ formatNumber(item.value) }}
					</dd>
				</div>
			</dl>
		</section>

		<section
			class="flex flex-col gap-6"
			aria-labelledby="admin-submissions-title"
		>
			<h2 id="admin-submissions-title">Rezept-Einreichungen</h2>

			<nav aria-label="Status">
				<ul class="tabs">
					<li
						v-for="item in STATUSES"
						:key="item"
					>
						<RouterLink
							:to="statusLocation(item)"
							class="tabs__item"
							:aria-current="status === item ? 'page' : 'false'"
						>
							{{ SUBMISSION_STATUS_LABELS[item] }}
						</RouterLink>
					</li>
				</ul>
			</nav>

			<div class="flex flex-col gap-4">
				<p
					ref="resultCount"
					class="font-semibold text-ink-soft outline-none"
					role="status"
					tabindex="-1"
				>
					{{ resultLabel }}
				</p>

				<BaseCard v-if="submissions.length">
					<ul
						class="data-list"
						:aria-busy="loading"
					>
						<li
							v-for="submission in submissions"
							:key="submission.id"
						>
							<RouterLink
								:to="{ name: 'admin-submission', params: { id: submission.id } }"
								class="data-list__row data-list__row--link"
							>
								<span class="data-list__label">
									<span class="font-semibold text-ink">{{
										submission.title
									}}</span>

									<span class="data-list__meta">
										{{ SUBMISSION_KIND_LABELS[submission.kind] }} ·
										{{
											submission.author
												? `von ${submission.author}`
												: 'Konto gelöscht'
										}}
										·
										<time :datetime="submission.submittedAt">
											{{ formatTimestamp(submission.submittedAt) }}
										</time>
									</span>
								</span>

								<BaseIcon
									class="text-muted"
									:icon="ChevronRightIcon"
								/>
							</RouterLink>
						</li>
					</ul>
				</BaseCard>

				<BaseEmptyState
					v-else-if="!loading && !loadError"
					:icon="InboxIcon"
					:title="EMPTY_STATES[status].title"
				>
					{{ EMPTY_STATES[status].text }}
				</BaseEmptyState>
			</div>

			<BasePagination
				v-if="total > SUBMISSIONS_PAGE_SIZE"
				v-model:page="page"
				label="Seiten der Einreichungen"
				:total="total"
				:items-per-page="SUBMISSIONS_PAGE_SIZE"
			/>
		</section>
	</main>
</template>
