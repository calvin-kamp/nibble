<script setup lang="ts">
import type { RadioGroupRootEmits, RadioGroupRootProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import type { ChoiceGroupVariants } from '.'
import { reactiveOmit } from '@vueuse/core'
import { useForwardPropsEmits } from 'reka-ui'
import { cn } from '@/lib/utils'
import { RadioGroup } from '@/components/ui/radio-group'
import { choiceGroupVariants } from '.'

interface Props extends RadioGroupRootProps {
  layout?: ChoiceGroupVariants['layout']
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'stack',
  class: undefined,
})

const emits = defineEmits<RadioGroupRootEmits>()

const delegatedProps = reactiveOmit(props, 'class', 'layout')

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <RadioGroup
    v-slot="slotProps"
    data-slot="choice-group"
    :data-layout="props.layout"
    :class="cn(choiceGroupVariants({ layout: props.layout }), props.class)"
    v-bind="forwarded"
  >
    <slot v-bind="slotProps" />
  </RadioGroup>
</template>
