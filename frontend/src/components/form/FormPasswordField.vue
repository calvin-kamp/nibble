<script setup lang="ts">
import type { FormFieldProps } from './form.types'

import FormField from './FormField.vue'
import { InputControl } from './controls'
import { UiButton, UiIcon } from '@components/ui'
import { EyeIcon, EyeOffIcon } from '@lucide/vue'
import { ref } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps<FormFieldProps>()

const visible = ref<boolean>(false)
</script>

<template>
  <FormField v-bind="props">
    <template #control="{ id, componentField, invalid, describedBy }">
      <InputControl
        v-bind="{ ...$attrs, ...componentField }"
        :id="id"
        :type="visible ? 'text' : 'password'"
        :required="props.required"
        :aria-invalid="invalid || undefined"
        :aria-describedby="describedBy"
      >
        <template #trailing>
          <UiButton
            variant="ghost"
            size="icon-sm"
            aria-label="Passwort anzeigen"
            :aria-pressed="visible"
            :aria-controls="id"
            @click="visible = !visible"
          >
            <UiIcon :icon="visible ? EyeOffIcon : EyeIcon" />
          </UiButton>
        </template>
      </InputControl>
    </template>
  </FormField>
</template>
