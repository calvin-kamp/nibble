<script setup lang="ts">
import type { PolicySection } from '@features/legal/legal.types'

interface Props {
	section: PolicySection
}

const props = defineProps<Props>()
</script>

<template>
	<section
		class="legal__section"
		:aria-labelledby="props.section.id"
	>
		<h2
			:id="props.section.id"
			class="legal__heading"
			tabindex="-1"
		>
			{{ props.section.title }}
		</h2>

		<slot />
	</section>
</template>
