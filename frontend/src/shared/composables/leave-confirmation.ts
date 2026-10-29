import type { MaybeRefOrGetter, Ref } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

import { ref, toValue } from 'vue'
import { useRouter } from 'vue-router'

/**
 * Confirmation before leaving a form with changes via "Abbrechen" or a back link.
 * Deliberately not on reload, closing the tab or the back gesture: nobody expects an
 * interruption there.
 */
export function useLeaveConfirmation(isDirty: MaybeRefOrGetter<boolean>): {
	open: Ref<boolean>
	leave: (to: RouteLocationRaw) => void
	confirm: () => void
	interceptLink: (event: MouseEvent) => void
} {
	const router = useRouter()

	const open = ref<boolean>(false)
	let target: RouteLocationRaw | null = null

	function leave(to: RouteLocationRaw): void {
		if (!toValue(isDirty)) {
			router.push(to)
			return
		}

		target = to
		open.value = true
	}

	function confirm(): void {
		if (target) router.push(target)

		target = null
	}

	/**
	 * For links, e.g. in the breadcrumbs, as @click.capture on the surrounding element. Prevents
	 * navigation before RouterLink starts it. Ctrl-click for a new tab stays allowed.
	 */
	function interceptLink(event: MouseEvent): void {
		const link = (event.target as HTMLElement).closest('a')
		const opensNewTab = event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey

		if (!link || opensNewTab || !toValue(isDirty)) return

		event.preventDefault()
		leave(link.pathname + link.search + link.hash)
	}

	return { open, leave, confirm, interceptLink }
}
