<script setup lang="ts">
import { ArrowLeftIcon, ArrowRightIcon } from '@lucide/vue'

import { BaseActions, BaseButton, BaseIcon } from '@shared/ui'

interface Props {
	submitLabel?: string
	showBack?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	submitLabel: 'Weiter',
	showBack: true,
})

const emit = defineEmits<{
	back: []
}>()
</script>

<template>
	<!-- Next first: on top on phones, on the right from tablet up -->
	<BaseActions>
		<!-- Replaces the submit button, e.g. with a link in the last step -->
		<slot name="primary">
			<BaseButton type="submit">
				{{ props.submitLabel }}
				<BaseIcon :icon="ArrowRightIcon" />
			</BaseButton>
		</slot>

		<BaseButton
			v-if="props.showBack"
			variant="outline"
			@click="emit('back')"
		>
			<BaseIcon :icon="ArrowLeftIcon" />
			Zurück
		</BaseButton>
	</BaseActions>
</template>
