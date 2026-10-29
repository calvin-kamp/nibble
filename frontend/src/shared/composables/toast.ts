import type { Ref } from 'vue'

import { ref } from 'vue'

export type ToastVariant = 'success' | 'info' | 'danger'

export interface Toast {
	id: number
	message: string
	variant: ToastVariant
}

// One list for the whole app. It lives outside the pages, so messages survive a page change,
// e.g. "Rezept veröffentlicht" on the way to the detail page.
const toasts = ref<Toast[]>([])
let nextId = 0

export function useToast(): {
	toasts: Ref<Toast[]>
	show: (message: string, variant?: ToastVariant) => void
	dismiss: (id: number) => void
} {
	function show(message: string, variant: ToastVariant = 'success'): void {
		toasts.value.push({ id: nextId++, message, variant })
	}

	function dismiss(id: number): void {
		toasts.value = toasts.value.filter((toast) => toast.id !== id)
	}

	return { toasts, show, dismiss }
}
