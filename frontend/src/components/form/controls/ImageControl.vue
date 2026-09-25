<script setup lang="ts">
import { ImageIcon, ImageUpIcon, Trash2Icon } from '@lucide/vue'
import { UiButton, UiIcon } from '@components/ui'
import { computed, nextTick, onBeforeUnmount, ref, useTemplateRef, watch } from 'vue'

interface Props {
  accept?: string
}

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<Props>(), {
  accept: 'image/jpeg,image/png,image/webp',
})

/** File: new selection · string: URL of an already saved image */
const modelValue = defineModel<File | string | null>()

const fileInput = useTemplateRef<HTMLInputElement>('fileInput')
const selectButton = useTemplateRef<{ $el?: HTMLElement }>('selectButton')
const replaceButton = useTemplateRef<{ $el?: HTMLElement }>('replaceButton')

const isDragging = ref<boolean>(false)
const previewUrl = ref<string | null>(null)

const fileName = computed<string>(() =>
  modelValue.value instanceof File ? modelValue.value.name : 'Aktuelles Bild',
)

/** Object URLs hold the file in memory until revoked, saved URLs need no cleanup */
function revokePreview(): void {
  if (previewUrl.value?.startsWith('blob:')) URL.revokeObjectURL(previewUrl.value)
}

watch(
  modelValue,
  (image) => {
    revokePreview()

    previewUrl.value = image instanceof File ? URL.createObjectURL(image) : (image ?? null)
  },
  { immediate: true },
)

onBeforeUnmount(revokePreview)

function openPicker(): void {
  fileInput.value?.click()
}

async function setFile(file: File | null): Promise<void> {
  modelValue.value = file

  await nextTick()

  // The pressed button is gone after the switch, focus goes to its counterpart.
  const target = file ? replaceButton.value : selectButton.value

  target?.$el?.focus()
}

function onChange(event: Event): void {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  // Reset, so picking the same file again still fires a change.
  input.value = ''

  if (file) void setFile(file)
}

function onDrop(event: DragEvent): void {
  isDragging.value = false

  const file = event.dataTransfer?.files[0]

  if (file) void setFile(file)
}
</script>

<template>
  <div
    v-if="modelValue && previewUrl"
    class="flex w-full flex-col border rounded-xl"
  >
    <img
      :src="previewUrl"
      alt=""
      class="w-full aspect-video bg-muted rounded-t-xl object-cover"
    />

    <div class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 border-t">
      <p class="min-w-0 flex-1 break-all text-muted-foreground text-sm">{{ fileName }}</p>

      <div class="flex flex-wrap gap-2">
        <UiButton
          ref="replaceButton"
          v-bind="$attrs"
          type="button"
          variant="ghost"
          @click="openPicker"
        >
          <UiIcon
            :icon="ImageUpIcon"
            :size="18"
          />
          Bild ersetzen
        </UiButton>

        <UiButton
          type="button"
          variant="destructive"
          @click="setFile(null)"
        >
          <UiIcon
            :icon="Trash2Icon"
            :size="18"
          />
          Bild entfernen
        </UiButton>
      </div>
    </div>
  </div>

  <!-- Dragging is only a shortcut, the area stays usable through "Bild auswählen" (WCAG 2.5.7) -->
  <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
  <div
    v-else
    :class="[
      'flex w-full aspect-video flex-col items-center justify-center gap-4 p-6 text-center',
      'border border-dashed rounded-xl',
      'transition-interactive',
      isDragging && 'bg-primary/5 border-primary border-solid',
      $attrs['aria-invalid'] && 'border-destructive',
    ]"
    @dragover.prevent="isDragging = true"
    @dragleave="isDragging = false"
    @drop.prevent="onDrop"
  >
    <span
      class="flex size-12 items-center justify-center bg-muted rounded-full text-muted-foreground"
    >
      <UiIcon
        :icon="ImageIcon"
        :size="24"
      />
    </span>

    <UiButton
      ref="selectButton"
      v-bind="$attrs"
      type="button"
      @click="openPicker"
    >
      Bild auswählen
    </UiButton>

    <p class="hidden text-muted-foreground text-sm pointer-fine:block">oder hierher ziehen</p>
  </div>

  <!-- eslint-disable-next-line vuejs-accessibility/form-control-has-label -->
  <input
    ref="fileInput"
    type="file"
    :accept="props.accept"
    hidden
    @change="onChange"
  />
</template>
