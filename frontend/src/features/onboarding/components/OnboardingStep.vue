<script setup lang="ts">
import { useId } from 'reka-ui'
import { onMounted, ref } from 'vue'

// Frame of a step. As a form, the step is a named form: Enter submits and Next is its submit
// button. As a section when it contains its own form.
interface Props {
	title: string
	lead?: string
	as?: 'form' | 'section'
	/** Wider for the calculator, which shows three fields side by side */
	wide?: boolean
	/** Nothing has to be entered; Next continues either way */
	optional?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	lead: undefined,
	as: 'form',
	wide: false,
	optional: false,
})

const titleId = useId(undefined, 'onboarding-step')

// Each new step moves focus to its heading so screen readers announce it
const heading = ref<HTMLElement | null>(null)

onMounted(() => heading.value?.focus())
</script>

<template>
	<component
		:is="props.as"
		class="flex flex-col gap-6 w-full mx-auto"
		:class="props.wide ? 'max-w-5xl' : 'max-w-3xl'"
		:aria-labelledby="titleId"
		:novalidate="props.as === 'form' || undefined"
	>
		<div class="flex flex-col gap-4">
			<p
				v-if="props.optional"
				class="self-start px-3 py-1 rounded-full bg-surface-muted text-sm font-semibold text-ink-soft"
			>
				Optional
			</p>

			<h1
				:id="titleId"
				ref="heading"
				class="outline-none"
				tabindex="-1"
			>
				{{ props.title }}
			</h1>

			<p
				v-if="props.lead"
				class="text-md text-ink-soft md:text-lg"
			>
				{{ props.lead }}
			</p>
		</div>

		<slot />
	</component>
</template>
