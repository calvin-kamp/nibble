import type { MaybeRefOrGetter } from 'vue'

import { readonly, ref, toValue, watchEffect } from 'vue'

const APP_NAME = 'nibble'

/** Public address, for canonical links and social previews. index.html has the same values. */
export const SITE_URL = 'https://www.nibble-tracking.de'

const DEFAULT_TITLE = `${APP_NAME} – Ernährungstagebuch und Rezepte`

const DEFAULT_DESCRIPTION =
	'Ernährungstagebuch, Kalorienrechner und Rezepte mit Nährwerten. Lebensmittel per Barcode scannen, Gewicht im 7-Tage-Schnitt verfolgen. Kostenlos und ohne Werbung.'

const announcement = ref<string>('')

function setMeta(attribute: 'name' | 'property', key: string, content: string): void {
	let tag = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${key}"]`)

	if (!tag) {
		tag = document.createElement('meta')
		tag.setAttribute(attribute, key)
		document.head.append(tag)
	}

	tag.content = content
}

export function setPageTitle(title: string | undefined): void {
	document.title = title ? `${title} – ${APP_NAME}` : DEFAULT_TITLE

	setMeta('property', 'og:title', document.title)
	setMeta('name', 'twitter:title', document.title)
}

export function setPageDescription(description: string | undefined): void {
	const text = description ?? DEFAULT_DESCRIPTION

	setMeta('name', 'description', text)
	setMeta('property', 'og:description', text)
	setMeta('name', 'twitter:description', text)
}

/**
 * Canonical address without query or hash, so filters and form steps count as one page.
 * Pages behind the login are kept out of search results.
 */
export function setPageAddress(path: string, indexable: boolean): void {
	const url = `${SITE_URL}${path === '/' ? '/' : path.replace(/\/$/, '')}`
	let link = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')

	if (!link) {
		link = document.createElement('link')
		link.rel = 'canonical'
		document.head.append(link)
	}

	link.href = url
	setMeta('property', 'og:url', url)
	setMeta('name', 'robots', indexable ? 'index, follow' : 'noindex, nofollow')
}

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

export function usePageTitle(title: MaybeRefOrGetter<string | undefined>): void {
	watchEffect(() => {
		const value = toValue(title)

		if (value) setPageTitle(value)
	})
}

export function usePageDescription(description: MaybeRefOrGetter<string | undefined>): void {
	watchEffect(() => {
		const value = toValue(description)

		if (value) setPageDescription(value)
	})
}
