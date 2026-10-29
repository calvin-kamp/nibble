<script setup lang="ts">
import {
	AlertDialogAction,
	AlertDialogCancel,
	AlertDialogContent,
	AlertDialogDescription,
	AlertDialogOverlay,
	AlertDialogPortal,
	AlertDialogRoot,
	AlertDialogTitle,
} from 'reka-ui'
import { computed } from 'vue'

import BaseActions from './BaseActions.vue'

// Confirmation before an action that cannot be undone. Unlike a dialog, it does not close on
// an outside click; the user has to decide. "Abbrechen" receives focus first so Enter
// discards nothing.
interface Props {
	title: string
	description: string
	confirmLabel: string
	cancelLabel?: string
	/** danger for actions where something is lost */
	variant?: 'primary' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
	cancelLabel: 'Abbrechen',
	variant: 'primary',
})

const emit = defineEmits<{
	confirm: []
}>()

const open = defineModel<boolean>('open')

const confirmClass = computed<string>(() => `button button--${props.variant}`)
</script>

<template>
	<AlertDialogRoot v-model:open="open">
		<AlertDialogPortal>
			<AlertDialogOverlay class="backdrop" />

			<AlertDialogContent class="dialog dialog--alert">
				<div class="dialog__intro">
					<AlertDialogTitle class="dialog__title">{{ props.title }}</AlertDialogTitle>

					<AlertDialogDescription class="dialog__description">
						{{ props.description }}
					</AlertDialogDescription>
				</div>

				<BaseActions>
					<AlertDialogAction
						:class="confirmClass"
						@click="emit('confirm')"
					>
						{{ props.confirmLabel }}
					</AlertDialogAction>

					<AlertDialogCancel class="button button--outline">{{
						props.cancelLabel
					}}</AlertDialogCancel>
				</BaseActions>
			</AlertDialogContent>
		</AlertDialogPortal>
	</AlertDialogRoot>
</template>
