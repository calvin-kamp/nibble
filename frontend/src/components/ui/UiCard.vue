<script setup lang="ts">
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'

import { Primitive } from 'reka-ui'
import { mergeClasses } from '@lib/merge-classes'

interface Props extends PrimitiveProps {
  size?: 'default' | 'sm'
  title?: string
  titleAs?: PrimitiveProps['as']
  description?: string
  class?: HTMLAttributes['class']
  mediaClass?: HTMLAttributes['class']
  headerClass?: HTMLAttributes['class']
  titleClass?: HTMLAttributes['class']
  descriptionClass?: HTMLAttributes['class']
  actionClass?: HTMLAttributes['class']
  contentClass?: HTMLAttributes['class']
  footerClass?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  as: 'div',
  asChild: false,
  size: 'default',
  title: undefined,
  titleAs: 'p',
  description: undefined,
  class: undefined,
  mediaClass: undefined,
  headerClass: undefined,
  titleClass: undefined,
  descriptionClass: undefined,
  actionClass: undefined,
  contentClass: undefined,
  footerClass: undefined,
})
</script>

<template>
  <Primitive
    :as="props.as"
    :as-child="props.asChild"
    :class="
      mergeClasses(
        'flex flex-col overflow-hidden bg-card rounded-lg ring-1 ring-foreground/10 text-card-foreground',
        props.size === 'sm' ? 'gap-3 py-0 pbe-4' : 'gap-6 py-6',
        $slots.media && 'pt-0',
        props.asChild && (props.size === 'sm' ? 'px-4' : 'px-6'),
        props.class,
      )
    "
  >
    <template v-if="props.asChild">
      <slot />
    </template>

    <template v-else>
      <div
        v-if="$slots.media"
        :class="mergeClasses(props.mediaClass)"
      >
        <slot name="media" />
      </div>

      <div
        v-if="
          props.title || props.description || $slots.title || $slots.description || $slots.action
        "
        :class="
          mergeClasses(
            'flex items-start justify-between gap-3',
            props.size === 'sm' ? 'px-4' : 'px-6',
            props.headerClass,
          )
        "
      >
        <div class="flex min-w-0 flex-col gap-1">
          <Primitive
            v-if="props.title || $slots.title"
            :as="props.titleAs"
            :class="
              mergeClasses('font-heading text-base leading-snug font-medium', props.titleClass)
            "
          >
            <slot name="title">{{ props.title }}</slot>
          </Primitive>

          <p
            v-if="props.description || $slots.description"
            :class="mergeClasses('text-muted-foreground text-sm', props.descriptionClass)"
          >
            <slot name="description">{{ props.description }}</slot>
          </p>
        </div>

        <div
          v-if="$slots.action"
          :class="mergeClasses('shrink-0', props.actionClass)"
        >
          <slot name="action" />
        </div>
      </div>

      <div
        v-if="$slots.default"
        :class="mergeClasses(props.size === 'sm' ? 'px-4' : 'px-6', props.contentClass)"
      >
        <slot />
      </div>

      <div
        v-if="$slots.footer"
        :class="
          mergeClasses(
            'flex items-center gap-2',
            props.size === 'sm' ? 'px-4' : 'px-6',
            props.footerClass,
          )
        "
      >
        <slot name="footer" />
      </div>
    </template>
  </Primitive>
</template>
