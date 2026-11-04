<script setup lang="ts">
import { useId } from 'reka-ui'

interface Props {
	title: string
	description?: string
}

const props = withDefaults(defineProps<Props>(), {
	description: undefined,
})

const titleId = useId(undefined, 'account-section')
</script>

<template>
	<section
		class="flex flex-col gap-5 pt-8 border-t border-divider first:pt-0 first:border-t-0"
		:aria-labelledby="titleId"
	>
		<div class="flex flex-col gap-1">
			<h3
				:id="titleId"
				class="font-sans text-lg font-bold tracking-normal"
			>
				{{ props.title }}
			</h3>

			<p
				v-if="props.description"
				class="text-foreground/80"
			>
				{{ props.description }}
			</p>
		</div>

		<slot />
	</section>
</template>
