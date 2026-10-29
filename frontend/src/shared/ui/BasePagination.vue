<script setup lang="ts">
import { ArrowLeftIcon, ArrowRightIcon } from '@lucide/vue'
import {
	PaginationEllipsis,
	PaginationList,
	PaginationListItem,
	PaginationNext,
	PaginationPrev,
	PaginationRoot,
} from 'reka-ui'

import BaseIcon from './BaseIcon.vue'

// reka-ui labels the buttons in English ("Page 2"), so custom labels are set here.
// They contain the visible text so voice control finds "Weiter".
interface Props {
	total: number
	itemsPerPage: number
	label?: string
}

const props = withDefaults(defineProps<Props>(), {
	label: 'Seiten',
})

const page = defineModel<number>('page', { required: true })
</script>

<template>
	<PaginationRoot
		v-model:page="page"
		class="pagination"
		:aria-label="props.label"
		:total="props.total"
		:items-per-page="props.itemsPerPage"
		:sibling-count="1"
		show-edges
	>
		<PaginationList
			v-slot="{ items }"
			class="pagination__list"
		>
			<PaginationPrev
				class="pagination__link"
				aria-label="Zurück zur vorherigen Seite"
			>
				<BaseIcon :icon="ArrowLeftIcon" />

				<span class="max-sm:sr-only">Zurück</span>
			</PaginationPrev>

			<template
				v-for="(item, index) in items"
				:key="index"
			>
				<PaginationListItem
					v-if="item.type === 'page'"
					class="pagination__link"
					:value="item.value"
					:aria-label="`Seite ${item.value}`"
				>
					{{ item.value }}
				</PaginationListItem>

				<PaginationEllipsis
					v-else
					class="pagination__gap"
					aria-hidden="true"
					>…</PaginationEllipsis
				>
			</template>

			<PaginationNext
				class="pagination__link"
				aria-label="Weiter zur nächsten Seite"
			>
				<span class="max-sm:sr-only">Weiter</span>

				<BaseIcon :icon="ArrowRightIcon" />
			</PaginationNext>
		</PaginationList>
	</PaginationRoot>
</template>
