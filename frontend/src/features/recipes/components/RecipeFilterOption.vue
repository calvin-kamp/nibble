<script setup lang="ts">
import { CheckboxControl } from '@components/form/controls'
import { Label as RekaLabel } from 'reka-ui'
import { useId } from 'vue'

interface Props {
  label: string
  checked: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  toggle: [checked: boolean]
}>()

const optionId = useId()
</script>

<template>
  <RekaLabel
    :for="optionId"
    class="flex min-h-11 w-full items-center gap-3 px-2 rounded-md hover:bg-accent cursor-pointer"
  >
    <CheckboxControl
      :id="optionId"
      :model-value="props.checked"
      :disabled="props.disabled"
      @update:model-value="(checked) => emit('toggle', checked === true)"
    />

    <span>{{ props.label }}</span>
  </RekaLabel>
</template>
