import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export const choiceGroupVariants = cva('group/choice-group', {
  variants: {
    layout: {
      stack: '',
      row: 'grid-flow-col auto-cols-fr',
      responsive: 'sm:grid-flow-col sm:auto-cols-fr',
    },
  },
  defaultVariants: {
    layout: 'stack',
  },
})

export type ChoiceGroupVariants = VariantProps<typeof choiceGroupVariants>

export { default as ChoiceButton } from './ChoiceButton.vue'
export { default as ChoiceGroup } from './ChoiceGroup.vue'
export { default as ChoiceTile } from './ChoiceTile.vue'
