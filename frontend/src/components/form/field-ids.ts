import type { MaybeRefOrGetter } from 'vue'

import { toValue, useId } from 'vue'

export function useFieldIds(hasDescription: MaybeRefOrGetter<boolean>) {
  const fieldId = useId()
  const descriptionId = `${fieldId}-description`
  const errorId = `${fieldId}-error`

  function describedBy(invalid: boolean): string | undefined {
    const ids: string[] = []

    if (invalid) ids.push(errorId)
    if (toValue(hasDescription)) ids.push(descriptionId)

    return ids.join(' ') || undefined
  }

  return { fieldId, descriptionId, errorId, describedBy }
}
