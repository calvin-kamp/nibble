<script setup lang="ts">
import { useId } from 'reka-ui'
import { onMounted, ref } from 'vue'

// Surface of a settings area. Sections inside it are separated by a line.
// On phone and tablet the area name is already shown in the select above, so the heading is
// only there for screen readers.
interface Props {
	title: string
}

const props = defineProps<Props>()

const titleId = useId(undefined, 'account-panel')
const heading = ref<HTMLElement | null>(null)

// When switching areas, screen readers announce the new area. Not on the first visit to the
// page, where focus should stay at the top of the page.
onMounted(() => {
	const previous = window.history.state?.back

	if (typeof previous === 'string' && previous.startsWith('/konto')) heading.value?.focus()
})
</script>

<template>
	<section
		class="flex flex-col gap-4 px-5 py-6 rounded-xl bg-surface md:p-8 xl:p-9"
		:aria-labelledby="titleId"
	>
		<h2
			:id="titleId"
			ref="heading"
			class="text-2xl outline-none max-xl:sr-only"
			tabindex="-1"
		>
			{{ props.title }}
		</h2>

		<!-- Sections and rows: a line above each one except the first -->
		<div class="flex flex-col gap-7">
			<slot />
		</div>
	</section>
</template>
