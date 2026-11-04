<script setup lang="ts">
import type { Component } from 'vue'

import { computed } from 'vue'

import BaseIcon from './BaseIcon.vue'

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
			<span
				class="empty-state__icon"
				aria-hidden="true"
			>
				<BaseIcon
					:icon="props.icon"
					:size="isSmall ? 20 : 24"
				/>
			</span>

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
