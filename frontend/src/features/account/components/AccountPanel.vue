<script setup lang="ts">
import { useId } from 'reka-ui'
import { onMounted, ref } from 'vue'

interface Props {
	title: string
}

const props = defineProps<Props>()

const titleId = useId(undefined, 'account-panel')
const heading = ref<HTMLElement | null>(null)

onMounted(() => {
	const previous = window.history.state?.back

	if (typeof previous === 'string' && previous.startsWith('/einstellungen')) heading.value?.focus()
})
</script>

<template>
	<section
		class="flex flex-col gap-6 p-5 border border-divider rounded-xl bg-card md:p-8 xl:p-10"
		:aria-labelledby="titleId"
	>
		<h2
			:id="titleId"
			ref="heading"
			class="outline-none max-xl:sr-only"
			tabindex="-1"
		>
			{{ props.title }}
		</h2>

		<div class="flex flex-col gap-8">
			<slot />
		</div>
	</section>
</template>
