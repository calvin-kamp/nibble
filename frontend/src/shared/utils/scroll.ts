/**
 * Distance a jump mark keeps from the top: the fixed header (hidden: height 0) plus the
 * target's own scroll-margin. Window scrolling by coordinates ignores both on its own.
 */
export function jumpMarkOffset(target: HTMLElement): number {
	const header = document.querySelector<HTMLElement>('.site-header')

	return (header?.offsetHeight ?? 0) + parseFloat(getComputedStyle(target).scrollMarginTop || '0')
}

function prefersReducedMotion(): boolean {
	return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Scrolls to the element with this id and moves focus there, so keyboard and screen reader
 * users continue reading at the section. Smooth unless reduced motion is asked for.
 */
export function scrollToJumpMark(id: string, smooth = true): void {
	const target = document.getElementById(id)

	if (!target) return

	const top = target.getBoundingClientRect().top + window.scrollY - jumpMarkOffset(target)

	window.scrollTo({ top, behavior: smooth && !prefersReducedMotion() ? 'smooth' : 'auto' })
	target.focus({ preventScroll: true })
}
