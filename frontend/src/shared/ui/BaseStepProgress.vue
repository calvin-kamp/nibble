<script setup lang="ts">
import BaseProgressBar from './BaseProgressBar.vue'

// "Schritt 2 von 4" with a bar, for forms that run in steps on phones
interface Props {
	/** Counted from 1 */
	current: number
	total: number
}

const props = defineProps<Props>()
</script>

<template>
	<div class="flex flex-col gap-2">
		<p class="text-sm font-semibold text-muted">
			Schritt {{ props.current }} von {{ props.total }}
		</p>

		<BaseProgressBar
			class="h-1.5"
			:value="props.current"
			:max="props.total"
			label="Fortschritt"
		/>
	</div>
</template>
