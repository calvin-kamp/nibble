import type { MaybeRefOrGetter } from 'vue'

import { readonly, ref, toValue, watchEffect } from 'vue'

const APP_NAME = 'nibble'

// Text of the live region in App.vue. One list for the whole app, like the toasts.
const announcement = ref<string>('')

/** Document title, e.g. "Rezepte · nibble". Without a page name only the app name. */
export function setPageTitle(title: string | undefined): void {
	document.title = title ? `${title} · ${APP_NAME}` : APP_NAME
}

/** Tells screen readers which page is now shown, after a client-side navigation */
export function announcePage(title: string | undefined): void {
	announcement.value = ''

	// Cleared first, so the same text is announced again, e.g. from one recipe to the next.
	// A timeout rather than a frame, which never fires in a background tab.
	setTimeout(() => {
		announcement.value = `${title ?? APP_NAME} geladen`
	}, 100)
}

export function usePageAnnouncement() {
	return readonly(announcement)
}

/**
 * Replaces the generic title from the route with the loaded content, e.g. the recipe's name.
 * Until the content is there, the route's title stays.
 */
export function usePageTitle(title: MaybeRefOrGetter<string | undefined>): void {
	watchEffect(() => {
		const value = toValue(title)

		if (value) setPageTitle(value)
	})
}
