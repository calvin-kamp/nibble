<script setup lang="ts">
import { useId } from 'reka-ui'
import { nextTick, ref } from 'vue'

import { BaseButton } from '@shared/ui'

// A setting as a row: name, current value and "Ändern". Only a click opens the form below it,
// so not every form is permanently open.
interface Props {
	label: string
	/** Current value. For values that should not be shown (password), use the value slot. */
	value?: string
}

const props = withDefaults(defineProps<Props>(), {
	value: undefined,
})

const slots = defineSlots<{
	/** The form for changing the value. Without this slot the value is read-only. */
	default?(props: { close: () => void }): unknown
	value?(): unknown
	/** Below the value, even while the form is closed, e.g. "Bestätigung ausstehend" */
	status?(): unknown
}>()

const titleId = useId(undefined, 'account-setting')

const editing = ref<boolean>(false)
const content = ref<HTMLElement | null>(null)
const editButton = ref<InstanceType<typeof BaseButton> | null>(null)

// On open, focus the first field; on close, return focus to "Ändern"
async function open(): Promise<void> {
	editing.value = true

	await nextTick()
	content.value?.querySelector<HTMLElement>('input')?.focus()
}

async function close(): Promise<void> {
	editing.value = false

	await nextTick()

	const element = editButton.value?.$el as HTMLElement | undefined

	element?.focus()
}
</script>

<template>
	<section
		class="flex flex-col gap-5 pt-7 border-t border-divider first:pt-0 first:border-t-0"
		:aria-labelledby="titleId"
	>
		<div class="flex items-start justify-between gap-4">
			<div class="flex flex-col gap-0.5 min-w-0">
				<h3
					:id="titleId"
					class="font-sans text-md font-bold tracking-normal"
				>
					{{ props.label }}
				</h3>

				<!-- While editing, the value is in the form, so it is not repeated here -->
				<p
					v-if="!editing"
					class="text-ink-soft wrap-break-word"
				>
					<slot name="value">{{ props.value }}</slot>
				</p>
			</div>

			<BaseButton
				v-if="!editing && slots.default"
				ref="editButton"
				class="shrink-0"
				variant="outline"
				size="sm"
				@click="open"
			>
				Ändern<span class="sr-only">: {{ props.label }}</span>
			</BaseButton>
		</div>

		<slot name="status" />

		<div
			v-if="editing"
			ref="content"
		>
			<slot :close="close" />
		</div>
	</section>
</template>
