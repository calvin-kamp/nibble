<script setup lang="ts">
import type { TrackingEntryKind } from '@features/tracking/tracking.types'

import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import FoodEntryForm from '@features/tracking/components/FoodEntryForm.vue'
import TrackingOptions from '@features/tracking/components/TrackingOptions.vue'
import WeightEntryForm from '@features/tracking/components/WeightEntryForm.vue'
import { BaseDialog, BaseDrawer } from '@shared/ui'

import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { useBreakpoint } from '@shared/composables/breakpoint'
import { useToast } from '@shared/composables/toast'

// Chooser and entry dialogs, mounted once in App.vue. They are opened via useTrackingDialogs().
// The forms live inside the dialog content, so they start empty every time it opens.
const { chooserOpen, entry, preset, openEntry, restoreFocus } = useTrackingDialogs()
const toast = useToast()

// From desktop the sidebar opens the chooser, below that the bottom navigation
const { isDesktop } = useBreakpoint()

function entryModel(kind: 'food' | 'weight') {
	return computed<boolean>({
		get: () => entry.value === kind,
		set: (open) => {
			if (!open) entry.value = null
		},
	})
}

// A link in the dialog, e.g. "Mahlzeit anlegen", leads to another page, where the dialog is closed.
const route = useRoute()

watch(
	() => route.path,
	() => {
		chooserOpen.value = false
		pendingEntry.value = null
		entry.value = null
	},
)

const foodOpen = entryModel('food')
const weightOpen = entryModel('weight')

function onSaved(message: string): void {
	entry.value = null
	toast.show(message)
}

// The drawer keeps its focus trap while it slides out and would pull focus out of the entry
// dialog, which then shows its validation right away. So the dialog only opens once the drawer
// is gone. The chooser dialog on desktop hands over directly.
const pendingEntry = ref<TrackingEntryKind | null>(null)

function onSelect(kind: TrackingEntryKind): void {
	if (isDesktop.value) {
		openEntry(kind)
		return
	}

	pendingEntry.value = kind
	chooserOpen.value = false
}

function onChooserClosed(event: Event): void {
	if (!pendingEntry.value) {
		restoreFocus(event)
		return
	}

	// Set directly instead of via openEntry, so focus still returns to the "+" button later
	event.preventDefault()
	entry.value = pendingEntry.value
	pendingEntry.value = null
}
</script>

<template>
	<!-- The chooser is a drawer where the bottom navigation opens it, like the account menu next
       to it. The entry itself is always a dialog. -->
	<component
		:is="isDesktop ? BaseDialog : BaseDrawer"
		v-model:open="chooserOpen"
		title="Was möchtest du eintragen?"
		description="Wähl aus, dann geht es direkt weiter."
		@close-auto-focus="onChooserClosed"
	>
		<TrackingOptions @select="onSelect" />
	</component>

	<BaseDialog
		v-model:open="foodOpen"
		title="Essen eintragen"
		description="Such ein Lebensmittel nach Name oder Barcode oder nimm eine deiner Mahlzeiten."
		@close-auto-focus="restoreFocus"
	>
		<FoodEntryForm
			:date="preset.date"
			:meal="preset.meal"
			:saved-meal-id="preset.savedMealId"
			@saved="onSaved(`${$event.name} eingetragen`)"
			@cancel="foodOpen = false"
		/>
	</BaseDialog>

	<BaseDialog
		v-model:open="weightOpen"
		title="Gewicht eintragen"
		description="Am besten morgens, vor dem Frühstück. Dann sind die Werte vergleichbar."
		@close-auto-focus="restoreFocus"
	>
		<WeightEntryForm
			:date="preset.date"
			@saved="onSaved('Gewicht eingetragen')"
			@cancel="weightOpen = false"
		/>
	</BaseDialog>
</template>
