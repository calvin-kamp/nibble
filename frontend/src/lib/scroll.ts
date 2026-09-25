import { nextTick } from 'vue'

/** Field arrays mark their add button when the list itself is invalid, e.g. empty */
const INVALID = '[aria-invalid="true"], [data-field-array-error]'

const FOCUSABLE = 'input, select, textarea, button, [tabindex]'

/** Jumps instead of gliding when the user asked for reduced motion */
export function scrollBehavior(): ScrollBehavior {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
}

/** Some invalid markers sit on a wrapper (e.g. a group), focus goes to the first control inside */
function focusableWithin(element: HTMLElement): HTMLElement {
  if (element.matches(FOCUSABLE)) return element

  return element.querySelector<HTMLElement>(FOCUSABLE) ?? element
}

/** Focuses the first invalid field of a form and scrolls it to the middle of the screen */
export async function revealFirstInvalidField(form: HTMLElement | null): Promise<void> {
  await nextTick()

  const invalid = form?.querySelector<HTMLElement>(INVALID)

  if (!invalid) return

  focusableWithin(invalid).focus({ preventScroll: true })

  invalid.scrollIntoView({ behavior: scrollBehavior(), block: 'center' })
}
