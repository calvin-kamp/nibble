<script setup lang="ts">
import { useId } from 'reka-ui'
import { onMounted, ref } from 'vue'

interface Props {
	title: string
	lead?: string
	as?: 'form' | 'section'
	wide?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	lead: undefined,
	as: 'form',
	wide: false,
})

const titleId = useId(undefined, 'onboarding-step')

const heading = ref<HTMLElement | null>(null)

onMounted(() => heading.value?.focus())
</script>

<template>
	<component
		:is="props.as"
		class="flex flex-col gap-8 w-full mx-auto"
		:class="props.wide ? 'max-w-5xl' : 'max-w-3xl'"
		:aria-labelledby="titleId"
		:novalidate="props.as === 'form' || undefined"
	>
		<div class="flex flex-col gap-3">
			<h1
				:id="titleId"
				ref="heading"
				class="min-w-0 outline-none wrap-break-word"
				tabindex="-1"
			>
				{{ props.title }}
			</h1>

			<p
				v-if="props.lead"
				class="text-lg text-foreground/80"
			>
				{{ props.lead }}
			</p>
		</div>

		<slot />
	</component>
</template>
