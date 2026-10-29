import type { MaybeRefOrGetter } from 'vue'

import { useId } from 'reka-ui'
import { toValue } from 'vue'

export interface FieldIds {
	id: string
	labelId: string
	hintId: string
	errorId: string
	/** For aria-describedby: hint and error, if present */
	describedBy: (errorMessage: string | undefined) => string | undefined
}

/** IDs that connect label, hint and error to the input */
export function useFieldIds(hint: MaybeRefOrGetter<string | undefined>): FieldIds {
	const id = useId(undefined, 'field')
	const hintId = `${id}-hint`
	const errorId = `${id}-error`

	function describedBy(errorMessage: string | undefined): string | undefined {
		const ids = [toValue(hint) ? hintId : null, errorMessage ? errorId : null]

		return ids.filter(Boolean).join(' ') || undefined
	}

	return { id, labelId: `${id}-label`, hintId, errorId, describedBy }
}
