<script setup lang="ts">
import type { FilterGroup, RecipeFilterValues } from '@features/recipes/recipes.types'

import { BaseChoiceList } from '@shared/ui'

import { groupValue, withGroupValue } from '@features/recipes/recipes.utils'

// One filter group as radios or checkboxes. Changes the filters immediately.
interface Props {
	group: FilterGroup
}

const props = defineProps<Props>()

const filters = defineModel<RecipeFilterValues>({ required: true })
</script>

<template>
	<BaseChoiceList
		:legend="props.group.legend"
		:type="props.group.type"
		:options="props.group.options"
		:model-value="groupValue(filters, props.group.id)"
		@update:model-value="filters = withGroupValue(filters, props.group.id, $event)"
	/>
</template>
