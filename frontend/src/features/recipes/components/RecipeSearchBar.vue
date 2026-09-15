<script setup lang="ts">
import { InputControl } from '@components/form/controls'
import { UiButton, UiIcon } from '@components/ui'
import { SearchIcon, XIcon } from '@lucide/vue'
import { Label as RekaLabel } from 'reka-ui'
import { useId } from 'vue'

const model = defineModel<string>({ default: '' })

const fieldId = useId()
</script>

<template>
  <div class="flex flex-col">
    <RekaLabel
      :for="fieldId"
      class="sr-only"
    >
      Suche
    </RekaLabel>

    <InputControl
      :id="fieldId"
      v-model="model"
      type="search"
      placeholder="Rezepte durchsuchen"
    >
      <template #leading>
        <UiIcon :icon="SearchIcon" />
      </template>

      <template
        v-if="model.length > 0"
        #trailing
      >
        <UiButton
          variant="ghost"
          size="icon-sm"
          aria-label="Suche zurücksetzen"
          @click="model = ''"
        >
          <UiIcon :icon="XIcon" />
        </UiButton>
      </template>
    </InputControl>
  </div>
</template>
