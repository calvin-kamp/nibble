import type { EntryPreset, TrackingEntryKind } from '@features/tracking/tracking.types'
import type { Ref } from 'vue'

import { ref } from 'vue'

// One state for the whole app: sidebar, bottom navigation and the today card open the same
// dialogs, which are mounted once in App.vue.
const chooserOpen = ref<boolean>(false)
const entry = ref<TrackingEntryKind | null>(null)
const preset = ref<EntryPreset>({})

// The button that opened everything. The dialogs have no DialogTrigger, so focus is
// explicitly returned there after closing.
let returnFocusTo: HTMLElement | null = null

export function useTrackingDialogs(): {
	chooserOpen: Ref<boolean>
	entry: Ref<TrackingEntryKind | null>
	preset: Ref<EntryPreset>
	openChooser: () => void
	openEntry: (kind: TrackingEntryKind, entryPreset?: EntryPreset) => void
	restoreFocus: (event: Event) => void
} {
	function rememberTrigger(): void {
		returnFocusTo =
			document.activeElement instanceof HTMLElement ? document.activeElement : null
	}

	function openChooser(): void {
		rememberTrigger()
		preset.value = {}
		chooserOpen.value = true
	}

	/** From the chooser or directly, e.g. via "Gewicht eintragen" on the dashboard */
	function openEntry(kind: TrackingEntryKind, entryPreset: EntryPreset = {}): void {
		if (!chooserOpen.value) rememberTrigger()

		preset.value = entryPreset
		chooserOpen.value = false
		entry.value = kind
	}

	/** For the dialogs' @close-auto-focus. If the chooser switches to an entry, focus stays there. */
	function restoreFocus(event: Event): void {
		event.preventDefault()

		if (chooserOpen.value || entry.value) return

		// The trigger may be gone by now, e.g. a button that only shows while nothing is logged
		const main = document.querySelector<HTMLElement>('main')
		const target = returnFocusTo?.isConnected ? returnFocusTo : main

		if (target === main && main) main.tabIndex = -1

		target?.focus()
		returnFocusTo = null
	}

	return { chooserOpen, entry, preset, openChooser, openEntry, restoreFocus }
}
