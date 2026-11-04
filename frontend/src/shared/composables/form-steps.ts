import type { ComputedRef, MaybeRefOrGetter, Ref } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

import { computed, nextTick, ref, toValue, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface FormStepsOptions {
	/** Step keys in order. They appear in the address like this, e.g. ?schritt=2. */
	keys: MaybeRefOrGetter<readonly string[]>
	enabled?: MaybeRefOrGetter<boolean>
	/**
	 * Furthest step reached so far. The address cannot take the user further, otherwise a reload
	 * could open a step with empty required fields.
	 */
	furthest?: Ref<number>
	onChange?: (index: number) => void
	queryKey?: string
	/**
	 * Finds the step for a key from the address. Defaults to an exact match; a flow whose steps
	 * change with the screen width can map a key that no longer exists to its replacement.
	 */
	indexOf?: (key: string) => number
}

export interface FormSteps {
	index: ComputedRef<number>
	key: ComputedRef<string>
	count: ComputedRef<number>
	isFirst: ComputedRef<boolean>
	isLast: ComputedRef<boolean>
	next: () => Promise<void>
	back: () => Promise<void>
	goTo: (index: number, options?: { focus?: boolean }) => Promise<void>
	/**
	 * Leaves the form after submitting. The steps are removed from history so Back does not land
	 * in the (then empty) form again.
	 */
	finish: (to: RouteLocationRaw) => Promise<void>
}

/**
 * Form steps in the address. Each step is a history entry, so the phone's back gesture goes to
 * the previous step instead of leaving the page.
 * The first step has no parameter in the address.
 */
export function useFormSteps(options: FormStepsOptions): FormSteps {
	const route = useRoute()
	const router = useRouter()

	const queryKey = options.queryKey ?? 'schritt'
	const furthest = options.furthest ?? ref<number>(0)

	const keys = computed<readonly string[]>(() => toValue(options.keys))
	const enabled = computed<boolean>(() => toValue(options.enabled) ?? true)
	const count = computed<number>(() => keys.value.length)

	const requestedIndex = computed<number>(() => {
		const value = route.query[queryKey]

		if (typeof value !== 'string') return 0

		return options.indexOf ? options.indexOf(value) : keys.value.indexOf(value)
	})

	const index = computed<number>(() => {
		const requested = requestedIndex.value < 0 ? furthest.value : requestedIndex.value

		return Math.min(requested, furthest.value, count.value - 1)
	})

	const key = computed<string>(() => keys.value[index.value]!)

	function location(target: number): RouteLocationRaw {
		return {
			query: { ...route.query, [queryKey]: target > 0 ? keys.value[target] : undefined },
		}
	}

	watch(
		[requestedIndex, index, enabled],
		() => {
			if (enabled.value && requestedIndex.value !== index.value)
				router.replace(location(index.value))
		},
		{ immediate: true },
	)

	let skipFocus = false

	watch(index, async (current) => {
		if (!enabled.value) return

		await nextTick()

		if (!skipFocus) options.onChange?.(current)

		skipFocus = false
	})

	async function next(): Promise<void> {
		const target = Math.min(index.value + 1, count.value - 1)

		furthest.value = Math.max(furthest.value, target)
		await router.push(location(target))
	}

	// Coming from the previous step goes back in history. Otherwise (e.g. after a reload)
	// the entry is replaced, so Back does not leave the page.
	async function back(): Promise<void> {
		const target = location(Math.max(index.value - 1, 0))
		const previous = window.history.state?.back

		if (previous && previous === router.resolve(target).fullPath) router.back()
		else await router.replace(target)
	}

	async function goTo(target: number, { focus = true } = {}): Promise<void> {
		if (target === index.value) return

		skipFocus = !focus
		furthest.value = Math.max(furthest.value, target)
		await router.replace(location(target))
		await nextTick()
	}

	async function finish(to: RouteLocationRaw): Promise<void> {
		const depth = enabled.value ? index.value : 0

		if (depth > 0) {
			await new Promise<void>((resolve) => {
				const stop = router.afterEach(() => {
					stop()
					resolve()
				})

				router.go(-depth)
			})
		}

		await router.replace(to)
	}

	return {
		index,
		key,
		count,
		isFirst: computed<boolean>(() => index.value === 0),
		isLast: computed<boolean>(() => index.value === count.value - 1),
		next,
		back,
		goTo,
		finish,
	}
}
