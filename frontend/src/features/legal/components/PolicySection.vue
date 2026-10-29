<script setup lang="ts">
import type { PolicySection } from '@features/legal/legal.types'

interface Props {
	section: PolicySection
}

const props = defineProps<Props>()
</script>

<template>
	<!-- The heading carries the jump mark. tabindex -1: after a jump from the table of contents
       focus moves there, without the heading joining the tab order. -->
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
