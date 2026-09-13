<script setup lang="ts">
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from '@/components/ui/input-group'
import { SearchIcon, XIcon } from '@lucide/vue'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { useId } from 'vue'
import { Field, FieldLabel } from '@/components/ui/field'

const model = defineModel<string>({ default: '' })
const fieldId: string = useId()
</script>

<template>
  <Field>
    <FieldLabel
      :for="fieldId"
      class="sr-only"
    >
      Suche
    </FieldLabel>

    <InputGroup>
      <InputGroupInput
        :id="fieldId"
        v-model="model"
        type="search"
        placeholder="Rezepte durchsuchen"
      />

      <InputGroupAddon>
        <LucideIcon :icon="SearchIcon" />
      </InputGroupAddon>

      <InputGroupAddon
        v-if="model.length > 0"
        align="inline-end"
      >
        <InputGroupButton
          data-size="icon-sm"
          aria-label="Suche zurücksetzen"
          @click="model = ''"
        >
          <LucideIcon :icon="XIcon" />
        </InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  </Field>
</template>
