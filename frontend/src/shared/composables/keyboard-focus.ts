import type { Ref } from 'vue'

import { ref } from 'vue'

// Inputs that open no on-screen keyboard
const NO_KEYBOARD_TYPES = new Set([
	'button',
	'checkbox',
	'color',
	'file',
	'hidden',
	'image',
	'radio',
	'range',
	'reset',
	'submit',
])

function opensKeyboard(element: Element | null): boolean {
	if (element instanceof HTMLTextAreaElement) return true
	if (element instanceof HTMLInputElement) return !NO_KEYBOARD_TYPES.has(element.type)

	return element instanceof HTMLElement && element.isContentEditable
}

const typing = ref<boolean>(opensKeyboard(document.activeElement))

document.addEventListener('focusin', (event) => {
	typing.value = opensKeyboard(event.target as Element | null)
})

// Moving from one field to the next fires focusout first; relatedTarget is the next field
document.addEventListener('focusout', (event) => {
	typing.value = opensKeyboard(event.relatedTarget as Element | null)
})

/**
 * Whether a field that opens the on-screen keyboard has focus. On phones the keyboard then
 * takes half the screen, and fixed bars at the bottom would cover the field.
 */
export function useKeyboardFocus(): Readonly<Ref<boolean>> {
	return typing
}
