<script setup lang="ts">
import { DumbbellIcon, PlusIcon, Trash2Icon } from '@lucide/vue'
import { FieldArray as VeeFieldArray } from 'vee-validate'
import { nextTick, useTemplateRef } from 'vue'
import { Button } from '@/components/ui/button'
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty'
import { FieldGroup } from '@/components/ui/field'
import { FormNumberField, FormSelectField } from '@/components/form'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { exercises } from '../calorie-calculator.data'
import type { Workout } from '../calorie-calculator.types'

interface Props {
  fieldName: string
}

const props = defineProps<Props>()

const addButton = useTemplateRef<{ $el?: HTMLElement }>('addButton')

const deleteButtonEls = new Map<number, HTMLElement | undefined>()

function setDeleteButtonRef(index: number, componentOrEl: unknown): void {
  const instance = componentOrEl as { $el?: HTMLElement } | null
  deleteButtonEls.set(index, instance?.$el ?? undefined)
}

function emptyWorkout(): Workout {
  return { met: '', duration: 0, frequency: 0 }
}

async function focusAddButton(): Promise<void> {
  await nextTick()

  addButton.value?.$el?.focus()
}

async function focusDeleteButton(index: number): Promise<void> {
  await nextTick()

  deleteButtonEls.get(index)?.focus()
}

async function handleRemove(removedIndex: number, remainingCount: number): Promise<void> {
  if (remainingCount === 0) {
    await focusAddButton()
    return
  }

  const nextIndex = removedIndex >= remainingCount ? remainingCount - 1 : removedIndex

  await focusDeleteButton(nextIndex)
}
</script>

<template>
  <VeeFieldArray
    v-slot="{ fields, push, remove }"
    :name="props.fieldName"
  >
    <FieldGroup class="gap-3">
      <Empty
        v-if="fields.length === 0"
        class="border p-8"
      >
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <LucideIcon :icon="DumbbellIcon" />
          </EmptyMedia>

          <EmptyTitle>Kein Training eingetragen</EmptyTitle>

          <EmptyDescription>
            Wir rechnen dann nur mit Grundumsatz und Alltagsbewegung.
          </EmptyDescription>
        </EmptyHeader>

        <EmptyContent>
          <Button
            ref="addButton"
            type="button"
            variant="outline"
            @click="push(emptyWorkout())"
          >
            <LucideIcon :icon="PlusIcon" />

            Training hinzufügen
          </Button>
        </EmptyContent>
      </Empty>

      <template v-else>
        <div
          v-for="(field, index) in fields"
          :key="field.key"
          role="group"
          :aria-label="`${index + 1}. Training`"
          class="border-border flex flex-col gap-4 rounded-xl border p-4"
        >
          <div class="flex min-h-11 items-center justify-between gap-3">
            <p class="flex items-center gap-2 text-sm font-medium">
              <span
                class="bg-muted text-muted-foreground inline-flex size-5.5 items-center justify-center rounded-full text-xs font-semibold tabular-nums"
                aria-hidden="true"
              >
                {{ index + 1 }}.
              </span>

              Training
            </p>

            <Button
              :ref="(el) => setDeleteButtonRef(index, el)"
              type="button"
              variant="destructive"
              size="icon"
              :aria-label="`${index + 1}. Training entfernen`"
              @click="(remove(index), handleRemove(index, fields.length))"
            >
              <LucideIcon :icon="Trash2Icon" />
            </Button>
          </div>

          <FormSelectField
            :field-name="`${props.fieldName}[${index}].met`"
            label="Sportart"
            placeholder="Sportart wählen"
            :options="exercises"
          />

          <FieldGroup class="flex-row gap-4">
            <FormNumberField
              :field-name="`${props.fieldName}[${index}].duration`"
              label="Dauer"
              unit="min"
              :step="5"
              :max="600"
            />

            <FormNumberField
              :field-name="`${props.fieldName}[${index}].frequency`"
              label="Pro Woche"
              unit="mal"
              :max="7"
            />
          </FieldGroup>
        </div>

        <Button
          ref="addButton"
          type="button"
          variant="outline"
          class="w-full"
          @click="push(emptyWorkout())"
        >
          <LucideIcon :icon="PlusIcon" />

          Weiteres Training hinzufügen
        </Button>
      </template>
    </FieldGroup>
  </VeeFieldArray>
</template>
