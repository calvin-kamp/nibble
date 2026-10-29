<script setup lang="ts">
import type { Component } from 'vue'

import { computed } from 'vue'

import BaseIcon from './BaseIcon.vue'

// Placeholder for an empty list or a search without results: icon, title, a sentence and
// optionally an action. The text goes into the default slot, the action into #actions.
interface Props {
	icon: Component
	title: string
	/** sm inside forms and dialogs: smaller, and the title is no heading there */
	size?: 'default' | 'sm'
}

const props = withDefaults(defineProps<Props>(), {
	size: 'default',
})

const isSmall = computed<boolean>(() => props.size === 'sm')
</script>

<template>
	<div
		class="empty-state"
		:class="{ 'empty-state--sm': isSmall }"
	>
		<div class="empty-state__intro">
			<BaseIcon
				class="text-muted"
				:icon="props.icon"
				:size="isSmall ? 24 : 32"
			/>

			<component
				:is="isSmall ? 'p' : 'h2'"
				class="empty-state__title"
			>
				{{ props.title }}
			</component>

			<p class="empty-state__text">
				<slot />
			</p>
		</div>

		<slot name="actions" />
	</div>
</template>
