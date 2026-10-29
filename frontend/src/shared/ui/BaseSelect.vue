<script setup lang="ts">
import type { SelectOption, SelectOptionGroup } from '@shared/ui/types'

import { CheckIcon, ChevronDownIcon } from '@lucide/vue'
import {
	SelectContent,
	SelectGroup,
	SelectIcon,
	SelectItem,
	SelectItemIndicator,
	SelectItemText,
	SelectLabel,
	SelectPortal,
	SelectRoot,
	SelectTrigger,
	SelectValue,
	SelectViewport,
} from 'reka-ui'

import BaseIcon from './BaseIcon.vue'

// Select without a form, e.g. for a time range or as navigation. In forms it is wrapped by
// SelectField. Attributes such as id or aria-label end up on the trigger.
defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<Props>(), {
	options: () => [],
	groups: () => [],
	placeholder: 'Bitte auswählen',
	disabled: false,
})

const emit = defineEmits<{
	'update:open': [open: boolean]
}>()

const model = defineModel<string | undefined>()

interface Props {
	/** Options without groups */
	options?: SelectOption[]
	/** Options with group headings, instead of options */
	groups?: SelectOptionGroup[]
	placeholder?: string
	disabled?: boolean
}
</script>

<template>
	<SelectRoot
		v-model="model"
		:disabled="props.disabled"
		@update:open="emit('update:open', $event)"
	>
		<SelectTrigger
			class="field__input select__trigger"
			v-bind="$attrs"
		>
			<SelectValue
				class="select__value"
				:placeholder="props.placeholder"
			/>

			<SelectIcon>
				<BaseIcon :icon="ChevronDownIcon" />
			</SelectIcon>
		</SelectTrigger>

		<SelectPortal>
			<SelectContent
				class="select__content"
				position="popper"
				:side-offset="4"
			>
				<SelectViewport :class="{ 'select__viewport--grouped': props.groups.length > 0 }">
					<SelectItem
						v-for="option in props.options"
						:key="option.value"
						class="select__item"
						:value="option.value"
						:disabled="option.disabled"
					>
						<SelectItemText>{{ option.label }}</SelectItemText>

						<SelectItemIndicator>
							<BaseIcon :icon="CheckIcon" />
						</SelectItemIndicator>
					</SelectItem>

					<SelectGroup
						v-for="group in props.groups"
						:key="group.label"
						class="select__group"
					>
						<SelectLabel class="select__group-label">{{ group.label }}</SelectLabel>

						<SelectItem
							v-for="option in group.options"
							:key="option.value"
							class="select__item"
							:value="option.value"
							:disabled="option.disabled"
						>
							<SelectItemText>{{ option.label }}</SelectItemText>

							<SelectItemIndicator>
								<BaseIcon :icon="CheckIcon" />
							</SelectItemIndicator>
						</SelectItem>
					</SelectGroup>
				</SelectViewport>
			</SelectContent>
		</SelectPortal>
	</SelectRoot>
</template>
