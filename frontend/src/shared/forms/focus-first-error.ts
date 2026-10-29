import { nextTick } from 'vue'

const FOCUSABLE = 'input, textarea, select, button, [tabindex]:not([tabindex="-1"])'

/**
 * After a failed submit, moves focus to the first invalid field in the form. If there is none
 * (the error is not tied to an input), to the first input.
 */
export async function focusFirstError(event: Event | undefined): Promise<void> {
	const form = (event?.target as HTMLElement | null)?.closest('form')

	await nextTick()

	// For groups such as radios the container carries aria-invalid; only the option inside is focusable
	const invalid = form?.querySelector<HTMLElement>('[aria-invalid="true"]')
	const target = invalid?.matches(FOCUSABLE)
		? invalid
		: (invalid?.querySelector<HTMLElement>(FOCUSABLE) ??
			form?.querySelector<HTMLElement>('input, textarea, [role="combobox"]'))

	target?.focus()
}
