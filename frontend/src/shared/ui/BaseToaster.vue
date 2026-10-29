<script setup lang="ts">
import type { ToastVariant } from '@shared/composables/toast'
import type { Component } from 'vue'

import { CircleAlertIcon, CircleCheckIcon, InfoIcon, XIcon } from '@lucide/vue'
import { ToastClose, ToastProvider, ToastRoot, ToastTitle, ToastViewport } from 'reka-ui'

import BaseIcon from './BaseIcon.vue'

import { useToast } from '@shared/composables/toast'

// Mounted once in App.vue. Shows every message from useToast().
const { toasts, dismiss } = useToast()

const ICONS: Record<ToastVariant, Component> = {
	success: CircleCheckIcon,
	info: InfoIcon,
	danger: CircleAlertIcon,
}

function onOpenChange(id: number, open: boolean): void {
	if (!open) dismiss(id)
}
</script>

<template>
	<ToastProvider
		label="Meldung"
		:duration="5000"
	>
		<ToastRoot
			v-for="toast in toasts"
			:key="toast.id"
			class="toast"
			:class="`toast--${toast.variant}`"
			:type="toast.variant === 'danger' ? 'foreground' : 'background'"
			default-open
			@update:open="onOpenChange(toast.id, $event)"
		>
			<BaseIcon
				class="toast__icon"
				:icon="ICONS[toast.variant]"
			/>

			<ToastTitle class="toast__title">{{ toast.message }}</ToastTitle>

			<ToastClose
				class="toast__close"
				aria-label="Meldung schließen"
			>
				<BaseIcon :icon="XIcon" />
			</ToastClose>
		</ToastRoot>

		<!-- F8 jumps to the messages via keyboard -->
		<ToastViewport
			class="toast-viewport"
			label="Meldungen ({hotkey})"
		/>
	</ToastProvider>
</template>
