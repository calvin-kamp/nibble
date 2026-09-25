<script setup lang="ts">
import { FieldArray, useFieldError } from 'vee-validate'
import { ChevronDownIcon, ChevronUpIcon, CircleAlertIcon, PlusIcon, Trash2Icon } from '@lucide/vue'
import { UiButton, UiEmptyState, UiIcon } from '@components/ui'
import { computed, nextTick, ref, toRef, useId, useTemplateRef } from 'vue'

type MoveDirection = 'up' | 'down'

interface Props {
  fieldName: string
  entryLabel: string
  newEntry: () => unknown
  emptyTitle?: string
  emptyText?: string
  addLabel?: string
  addMoreLabel?: string
  max?: number
  reorderable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  emptyTitle: undefined,
  emptyText: undefined,
  addLabel: undefined,
  addMoreLabel: undefined,
  max: undefined,
  reorderable: false,
})

defineSlots<{
  default(props: { index: number; path: string }): unknown
  media(): unknown
}>()

const error = useFieldError(toRef(props, 'fieldName'))

const errorId = useId()

const addButton = useTemplateRef<{ $el?: HTMLElement }>('addButton')

const removeButtons = new Map<number, HTMLElement | undefined>()

/** Keyed by "<index>-<direction>", so focus can follow an entry after it moved */
const moveButtons = new Map<string, HTMLElement | undefined>()

const announcement = ref<string>('')

const addLabel = computed<string>(() => props.addLabel ?? `${props.entryLabel} hinzufügen`)

const addMoreLabel = computed<string>(() => props.addMoreLabel ?? addLabel.value)

function toElement(instance: unknown): HTMLElement | undefined {
  return (instance as { $el?: HTMLElement } | null)?.$el ?? undefined
}

function setRemoveButtonRef(index: number, instance: unknown): void {
  removeButtons.set(index, toElement(instance))
}

function setMoveButtonRef(index: number, direction: MoveDirection, instance: unknown): void {
  moveButtons.set(`${index}-${direction}`, toElement(instance))
}

async function moveFocusAfterRemove(removedIndex: number, remainingCount: number): Promise<void> {
  await nextTick()

  if (remainingCount === 0) {
    addButton.value?.$el?.focus()
    return
  }

  const nextIndex = removedIndex >= remainingCount ? remainingCount - 1 : removedIndex

  removeButtons.get(nextIndex)?.focus()
}

async function moveEntry(
  swap: (indexA: number, indexB: number) => void,
  index: number,
  direction: MoveDirection,
  count: number,
): Promise<void> {
  const target = direction === 'up' ? index - 1 : index + 1

  swap(index, target)

  announcement.value = `${index + 1}. ${props.entryLabel} ist jetzt ${target + 1}. ${props.entryLabel}.`

  await nextTick()

  // At the edge the same button is disabled, so focus goes to the opposite one.
  const atEdge = direction === 'up' ? target === 0 : target === count - 1
  const focusDirection: MoveDirection = atEdge ? (direction === 'up' ? 'down' : 'up') : direction

  moveButtons.get(`${target}-${focusDirection}`)?.focus()
}
</script>

<template>
  <FieldArray
    v-slot="{ fields, push, remove, swap }"
    :name="props.fieldName"
  >
    <UiEmptyState
      v-if="!fields.length"
      :title="props.emptyTitle"
      :description="props.emptyText"
    >
      <template
        v-if="$slots.media"
        #media
      >
        <slot name="media" />
      </template>

      <UiButton
        ref="addButton"
        type="button"
        :aria-describedby="error ? errorId : undefined"
        :data-field-array-error="error ? '' : undefined"
        @click="push(props.newEntry())"
      >
        <UiIcon :icon="PlusIcon" />
        {{ addLabel }}
      </UiButton>
    </UiEmptyState>

    <template v-else>
      <div
        v-for="(field, index) in fields"
        :key="field.key"
        role="group"
        :aria-label="`${index + 1}. ${props.entryLabel}`"
        class="flex flex-col gap-4 p-4 border border-border rounded-xl"
      >
        <div class="flex min-h-11 items-center justify-between gap-3">
          <p class="flex items-center gap-2 font-medium">
            <span
              class="inline-flex size-6 shrink-0 items-center justify-center bg-muted rounded-full text-muted-foreground text-sm font-semibold tabular-nums"
              aria-hidden="true"
            >
              {{ index + 1 }}
            </span>

            {{ props.entryLabel }}
          </p>

          <div class="flex items-center gap-4">
            <template v-if="props.reorderable && fields.length > 1">
              <UiButton
                :ref="(el) => setMoveButtonRef(index, 'up', el)"
                type="button"
                variant="ghost"
                size="icon-sm"
                :disabled="index === 0"
                :aria-label="`${index + 1}. ${props.entryLabel} nach oben verschieben`"
                @click="moveEntry(swap, index, 'up', fields.length)"
              >
                <UiIcon
                  :icon="ChevronUpIcon"
                  :size="18"
                />
              </UiButton>

              <UiButton
                :ref="(el) => setMoveButtonRef(index, 'down', el)"
                type="button"
                variant="ghost"
                size="icon-sm"
                :disabled="index === fields.length - 1"
                :aria-label="`${index + 1}. ${props.entryLabel} nach unten verschieben`"
                @click="moveEntry(swap, index, 'down', fields.length)"
              >
                <UiIcon
                  :icon="ChevronDownIcon"
                  :size="18"
                />
              </UiButton>
            </template>

            <UiButton
              :ref="(el) => setRemoveButtonRef(index, el)"
              type="button"
              variant="destructive"
              size="icon"
              :aria-label="`${index + 1}. ${props.entryLabel} entfernen`"
              @click="(remove(index), moveFocusAfterRemove(index, fields.length - 1))"
            >
              <UiIcon
                :icon="Trash2Icon"
                :size="18"
              />
            </UiButton>
          </div>
        </div>

        <slot
          :index="index"
          :path="`${props.fieldName}[${index}]`"
        />
      </div>

      <UiButton
        v-if="props.max === undefined || fields.length < props.max"
        ref="addButton"
        type="button"
        :aria-describedby="error ? errorId : undefined"
        :data-field-array-error="error ? '' : undefined"
        @click="push(props.newEntry())"
      >
        <UiIcon :icon="PlusIcon" />
        {{ addMoreLabel }}
      </UiButton>
    </template>

    <div
      v-if="error"
      :id="errorId"
      role="alert"
      class="flex items-start gap-1 text-destructive text-sm"
    >
      <span class="flex h-5 items-center">
        <UiIcon :icon="CircleAlertIcon" />
      </span>

      <span>{{ error }}</span>
    </div>

    <p
      v-if="props.reorderable"
      aria-live="polite"
      class="sr-only"
    >
      {{ announcement }}
    </p>
  </FieldArray>
</template>
