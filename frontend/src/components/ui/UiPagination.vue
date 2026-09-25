<script setup lang="ts">
import type { HTMLAttributes } from 'vue'

import { ChevronLeftIcon, ChevronRightIcon } from '@lucide/vue'
import {
  PaginationEllipsis,
  PaginationList,
  PaginationListItem,
  PaginationNext,
  PaginationPrev,
  PaginationRoot,
} from 'reka-ui'
import { mergeClasses } from '@lib/merge-classes'
import UiIcon from './UiIcon.vue'

interface Props {
  total: number
  itemsPerPage?: number
  label?: string
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  itemsPerPage: 20,
  label: 'Seitenauswahl',
  class: undefined,
})

const page = defineModel<number>('page', { required: true })
</script>

<template>
  <PaginationRoot
    v-if="props.total > props.itemsPerPage"
    v-slot="{ page: currentPage, pageCount }"
    v-model:page="page"
    :total="props.total"
    :items-per-page="props.itemsPerPage"
    :sibling-count="1"
    :aria-label="props.label"
    :class="mergeClasses('w-full', props.class)"
    show-edges
  >
    <div class="flex flex-wrap items-center justify-between gap-2">
      <PaginationPrev
        aria-label="Vorherige Seite"
        class="inline-flex min-h-11 min-w-11 items-center justify-center gap-2 md:px-3 rounded-md outline-hidden enabled:hover:bg-muted enabled:active:bg-input focus-visible:focus-ring transition-interactive disabled:inactive"
      >
        <UiIcon :icon="ChevronLeftIcon" />

        <span class="hidden md:inline">Vorherige Seite</span>
      </PaginationPrev>

      <p class="text-center tabular-nums md:hidden">Seite {{ currentPage }} von {{ pageCount }}</p>

      <PaginationList
        v-slot="{ items }"
        as="ul"
        class="hidden flex-wrap items-center justify-center gap-1 md:flex"
      >
        <li
          v-for="(item, index) in items"
          :key="index"
        >
          <PaginationListItem
            v-if="item.type === 'page'"
            :value="item.value"
            :aria-label="`Seite ${item.value}`"
            class="inline-flex min-h-11 min-w-11 items-center justify-center px-2 rounded-md outline-hidden not-data-selected:hover:bg-muted not-data-selected:active:bg-input data-selected:bg-primary focus-visible:focus-ring data-selected:text-primary-foreground data-selected:font-medium tabular-nums transition-interactive data-selected:cursor-default"
          >
            {{ item.value }}
          </PaginationListItem>

          <PaginationEllipsis
            v-else
            :index="index"
            aria-hidden="true"
            class="inline-flex size-11 items-center justify-center text-muted-foreground"
          >
            …
          </PaginationEllipsis>
        </li>
      </PaginationList>

      <PaginationNext
        aria-label="Nächste Seite"
        class="inline-flex min-h-11 min-w-11 items-center justify-center gap-2 md:px-3 rounded-md outline-hidden enabled:hover:bg-muted enabled:active:bg-input focus-visible:focus-ring transition-interactive disabled:inactive"
      >
        <span class="hidden md:inline">Nächste Seite</span>

        <UiIcon :icon="ChevronRightIcon" />
      </PaginationNext>
    </div>
  </PaginationRoot>
</template>
