import type { WeekPage, WeekQuery } from '@features/tracking/tracking.types'
import type { ComputedRef, Ref } from 'vue'

import { computed, ref, shallowRef, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'

import { parseIsoDate, toIsoDate } from '@shared/utils/date'

/** The backend sends five weeks per page */
export const WEEKS_PER_PAGE = 5

/** More weeks than this are not loaded one by one; a range picks older ones instead */
export const MAX_LOADED_WEEKS = 20

export interface WeekRange {
	from: string
	to: string
}

interface WeekHistory<T> {
	weeks: Readonly<Ref<T[]>>
	loading: Readonly<Ref<boolean>>
	loadError: Readonly<Ref<boolean>>
	/** All weeks with entries in the range, loaded or not */
	total: Readonly<Ref<number>>
	/** From ?von=&bis= in the address, null without both */
	range: ComputedRef<WeekRange | null>
	/** Older weeks exist and fewer than MAX_LOADED_WEEKS are loaded */
	canLoadMore: ComputedRef<boolean>
	/** A range is set, or there are more weeks than MAX_LOADED_WEEKS: the range picker shows */
	showsRange: ComputedRef<boolean>
	loadMore: () => Promise<void>
	setRange: (range: WeekRange | null) => void
}

function dateParam(value: unknown): string | null {
	return typeof value === 'string' && parseIsoDate(value) && value <= toIsoDate() ? value : null
}

/**
 * Weeks with entries for the diary lists, newest first: five at once, five more per click up to
 * twenty, after that a range "von – bis" kept in the address. Reloads after every change of an
 * entry, keeping the number of weeks already shown.
 */
export function useWeekHistory<T>(
	fetchPage: (query: WeekQuery) => Promise<WeekPage<T>>,
): WeekHistory<T> {
	const route = useRoute()
	const router = useRouter()

	const weeks = shallowRef<T[]>([])
	const loading = ref<boolean>(true)
	const loadError = ref<boolean>(false)
	const nextBefore = ref<string | null>(null)
	const total = ref<number>(0)

	const range = computed<WeekRange | null>(() => {
		const from = dateParam(route.query.von)
		const to = dateParam(route.query.bis)

		return from && to && from <= to ? { from, to } : null
	})

	function query(before?: string): WeekQuery {
		return { before, from: range.value?.from, to: range.value?.to }
	}

	// Each load has a number, so an older response that arrives late is dropped
	let loadId = 0

	async function load(count: number): Promise<void> {
		const id = ++loadId
		loading.value = true

		try {
			const loaded: T[] = []
			let before: string | undefined
			let next: string | null = null
			let pageTotal = 0

			// One page after the other: each one needs the cursor of the page before
			do {
				// oxlint-disable-next-line no-await-in-loop
				const page = await fetchPage(query(before))

				loaded.push(...page.weeks)
				next = page.nextBefore
				pageTotal = page.total
				before = next ?? undefined
			} while (next && loaded.length < count)

			if (id !== loadId) return

			weeks.value = loaded
			nextBefore.value = next
			total.value = pageTotal
			loadError.value = false
		} catch {
			if (id === loadId) loadError.value = true
		} finally {
			if (id === loadId) loading.value = false
		}
	}

	async function loadMore(): Promise<void> {
		if (!nextBefore.value || loading.value) return

		const id = ++loadId
		loading.value = true

		try {
			const page = await fetchPage(query(nextBefore.value))

			if (id !== loadId) return

			weeks.value = [...weeks.value, ...page.weeks]
			nextBefore.value = page.nextBefore
			total.value = page.total
			loadError.value = false
		} catch {
			if (id === loadId) loadError.value = true
		} finally {
			if (id === loadId) loading.value = false
		}
	}

	watch(range, () => load(WEEKS_PER_PAGE), { immediate: true })
	watch(useTrackingChanges(), () => load(Math.max(weeks.value.length, WEEKS_PER_PAGE)))

	function setRange(next: WeekRange | null): void {
		router.replace({ query: { ...route.query, von: next?.from, bis: next?.to } })
	}

	return {
		weeks,
		loading,
		loadError,
		total,
		range,
		canLoadMore: computed(() => !!nextBefore.value && weeks.value.length < MAX_LOADED_WEEKS),
		// Known with the first page already, so the picker is there from the start
		showsRange: computed(() => !!range.value || total.value > MAX_LOADED_WEEKS),
		loadMore,
		setRange,
	}
}
