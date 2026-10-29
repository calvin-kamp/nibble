<script setup lang="ts">
import type { BreadcrumbItem } from '@shared/ui/types'

import { ChevronRightIcon } from '@lucide/vue'

import BaseIcon from './BaseIcon.vue'
import BaseLink from './BaseLink.vue'

// Path to the current page. The last level is the page itself and not a link.
interface Props {
	items: BreadcrumbItem[]
	current: string
}

const props = defineProps<Props>()
</script>

<template>
	<nav
		class="breadcrumb"
		aria-label="Brotkrumen"
	>
		<ol class="breadcrumb__list">
			<li
				v-for="item in props.items"
				:key="item.routeName"
				class="breadcrumb__item"
			>
				<BaseLink
					class="breadcrumb__link"
					variant="inline"
					:route-name="item.routeName"
					:params="item.params"
					:query="item.query"
				>
					{{ item.label }}
				</BaseLink>

				<BaseIcon
					class="breadcrumb__separator"
					:icon="ChevronRightIcon"
					:size="16"
				/>
			</li>

			<li
				class="breadcrumb__item"
				aria-current="page"
			>
				{{ props.current }}
			</li>
		</ol>
	</nav>
</template>
