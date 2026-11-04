<script setup lang="ts">
import type { ChoiceOption } from '@shared/ui/types'

import { useId } from 'reka-ui'

// For validated forms use RadioField and CheckboxGroupField.
interface Props {
	legend: string
	options: ChoiceOption[]
	type?: 'radio' | 'checkbox'
}

const props = withDefaults(defineProps<Props>(), {
	type: 'radio',
})

const model = defineModel<string | string[]>({ required: true })

const name = useId(undefined, 'choice-list')
</script>

<template>
	<fieldset class="choice-list">
		<legend class="choice-list__legend">
			{{ props.legend }}
		</legend>

		<label
			v-for="option in props.options"
			:key="option.value"
			class="choice-list__option"
		>
			<input
				v-model="model"
				class="choice-list__input"
				:type="props.type"
				:name="name"
				:value="option.value"
			/>

			{{ option.label }}
		</label>
	</fieldset>
</template>
