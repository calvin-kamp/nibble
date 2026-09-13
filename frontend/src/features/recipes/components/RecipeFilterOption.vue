<script setup lang="ts">
import { useId } from 'vue'
import { Checkbox } from '@/components/ui/checkbox'
import { FieldLabel } from '@/components/ui/field'

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

const optionId: string = useId()
</script>

<template>
  <FieldLabel
    :for="optionId"
    class="hover:bg-accent flex min-h-11 w-full cursor-pointer items-center gap-3 rounded-md px-2 font-normal"
  >
    <Checkbox
      :id="optionId"
      :model-value="props.checked"
      :disabled="props.disabled"
      @update:model-value="(checked) => emit('toggle', checked === true)"
    />

    <span>{{ props.label }}</span>
  </FieldLabel>
</template>
