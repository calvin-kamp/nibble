<script setup lang="ts">
import { XIcon } from '@lucide/vue'
import {
	DialogClose,
	DialogContent,
	DialogOverlay,
	DialogPortal,
	DialogRoot,
	DialogTitle,
} from 'reka-ui'

import BaseIcon from './BaseIcon.vue'

interface Props {
	title: string
	titleHidden?: boolean
	side?: 'left' | 'right'
}

defineOptions({
	inheritAttrs: false,
})

const props = withDefaults(defineProps<Props>(), {
	titleHidden: false,
	side: 'left',
})

const open = defineModel<boolean>('open')
</script>

<template>
	<DialogRoot v-model:open="open">
		<DialogPortal>
			<DialogOverlay class="backdrop" />

			<!-- aria-describedby: a menu needs no description; this tells reka-ui so -->
			<DialogContent
				v-bind="$attrs"
				class="sheet"
				:class="`sheet--${props.side}`"
				:aria-describedby="undefined"
			>
				<div class="sheet__header">
					<DialogTitle :class="props.titleHidden ? 'sr-only' : 'sheet__title'">
						{{ props.title }}
					</DialogTitle>

					<slot name="header" />

					<DialogClose
						class="dialog__close ml-auto"
						aria-label="Menü schließen"
					>
						<BaseIcon :icon="XIcon" />
					</DialogClose>
				</div>

				<slot />
			</DialogContent>
		</DialogPortal>
	</DialogRoot>
</template>
