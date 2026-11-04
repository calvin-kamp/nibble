<script setup lang="ts">
import { useId } from 'reka-ui'
import { nextTick, ref } from 'vue'

import { BaseButton } from '@shared/ui'

interface Props {
	label: string
	value?: string
}

const props = withDefaults(defineProps<Props>(), {
	value: undefined,
})

const slots = defineSlots<{
	default?(props: { close: () => void }): unknown
	value?(): unknown
	status?(): unknown
}>()

const titleId = useId(undefined, 'account-setting')

const editing = ref<boolean>(false)
const content = ref<HTMLElement | null>(null)
const editButton = ref<InstanceType<typeof BaseButton> | null>(null)

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
		class="flex flex-col gap-5 pt-8 border-t border-divider first:pt-0 first:border-t-0"
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

				<p
					v-if="!editing"
					class="text-foreground/80 wrap-break-word"
				>
					<slot name="value">
						{{ props.value }}
					</slot>
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
				Ändern<span class="sr-only">
					: {{ props.label }}
				</span>
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
