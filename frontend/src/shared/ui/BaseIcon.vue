<script lang="ts" setup>
import type { LucideIcon } from '@lucide/vue'
import type { Component, HTMLAttributes } from 'vue'

interface Props {
	icon: Component | LucideIcon
	size?: number
	class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
	size: 20,
	class: undefined,
})
</script>

<template>
	<component
		:is="props.icon"
		:size="props.size"
		class="shrink-0"
		:class="props.class"
		aria-hidden="true"
	/>
</template>
