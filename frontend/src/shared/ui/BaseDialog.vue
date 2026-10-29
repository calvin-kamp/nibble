<script setup lang="ts">
import { XIcon } from '@lucide/vue'
import {
	DialogClose,
	DialogContent,
	DialogDescription,
	DialogOverlay,
	DialogPortal,
	DialogRoot,
	DialogTitle,
} from 'reka-ui'

import BaseIcon from './BaseIcon.vue'

interface Props {
	title: string
	description?: string
}

// Attributes and events (e.g. @close-auto-focus) go to the content, not to DialogRoot
defineOptions({
	inheritAttrs: false,
})

const props = withDefaults(defineProps<Props>(), {
	description: undefined,
})

const open = defineModel<boolean>('open')

// On open, focus the field with autofocus, otherwise the first field or the first
// option. Not the close button in the top right, which reka-ui would find first otherwise.
const FOCUS_TARGETS =
	'input, textarea, select, [role="combobox"], button:not(.dialog__close), a[href]'

function onOpenAutoFocus(event: Event): void {
	const content = event.target as HTMLElement | null
	const target =
		content?.querySelector<HTMLElement>('[autofocus]') ??
		content?.querySelector<HTMLElement>(FOCUS_TARGETS)

	if (!target) return

	event.preventDefault()
	target.focus()
}
</script>

<template>
	<DialogRoot v-model:open="open">
		<DialogPortal>
			<DialogOverlay class="backdrop" />

			<DialogContent
				v-bind="$attrs"
				class="dialog"
				@open-auto-focus="onOpenAutoFocus"
			>
				<div class="dialog__intro">
					<div class="dialog__header">
						<DialogTitle class="dialog__title">{{ props.title }}</DialogTitle>

						<DialogClose
							class="dialog__close"
							aria-label="Schließen"
						>
							<BaseIcon :icon="XIcon" />
						</DialogClose>
					</div>

					<DialogDescription
						v-if="props.description"
						class="dialog__description"
					>
						{{ props.description }}
					</DialogDescription>
				</div>

				<slot />
			</DialogContent>
		</DialogPortal>
	</DialogRoot>
</template>
