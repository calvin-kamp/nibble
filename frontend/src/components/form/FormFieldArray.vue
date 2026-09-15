<script setup lang="ts">
import { FieldArray } from 'vee-validate'
import { PlusIcon, Trash2Icon } from '@lucide/vue'
import { UiButton, UiEmptyState, UiIcon } from '@components/ui'
import { computed, nextTick, useTemplateRef } from 'vue'

interface Props {
  fieldName: string
  entryLabel: string
  newEntry: () => unknown
  emptyTitle?: string
  emptyText?: string
  addLabel?: string
  addMoreLabel?: string
  max?: number
}

const props = withDefaults(defineProps<Props>(), {
  emptyTitle: undefined,
  emptyText: undefined,
  addLabel: undefined,
  addMoreLabel: undefined,
  max: undefined,
})

defineSlots<{
  default(props: { index: number; path: string }): unknown
  media(): unknown
}>()

const addButton = useTemplateRef<{ $el?: HTMLElement }>('addButton')

const removeButtons = new Map<number, HTMLElement | undefined>()

const addLabel = computed<string>(() => props.addLabel ?? `${props.entryLabel} hinzufügen`)

const addMoreLabel = computed<string>(() => props.addMoreLabel ?? addLabel.value)

function setRemoveButtonRef(index: number, instance: unknown): void {
  removeButtons.set(index, (instance as { $el?: HTMLElement } | null)?.$el ?? undefined)
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
</script>

<template>
  <FieldArray
    v-slot="{ fields, push, remove }"
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

        <slot
          :index="index"
          :path="`${props.fieldName}[${index}]`"
        />
      </div>

      <UiButton
        v-if="props.max === undefined || fields.length < props.max"
        ref="addButton"
        type="button"
        @click="push(props.newEntry())"
      >
        <UiIcon :icon="PlusIcon" />
        {{ addMoreLabel }}
      </UiButton>
    </template>
  </FieldArray>
</template>
