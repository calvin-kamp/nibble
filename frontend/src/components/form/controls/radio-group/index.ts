import type { VariantProps } from 'class-variance-authority'

import { cva } from 'class-variance-authority'

export const radioItemVariants = cva(
  [
    'flex flex-col justify-center items-center min-h-11',
    'border border-input rounded-md text-start',
    'transition-interactive focus-visible:focus-ring',
    'group-aria-invalid:border-destructive group-aria-invalid:focus-visible:focus-ring-destructive',
    'disabled:inactive',
    'data-[state=checked]:border-primary',
  ],
  {
    variants: {
      variant: {
        segment:
          'px-4 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground',
        card: 'gap-1 p-4 data-[state=checked]:bg-primary/10',
      },
    },
    defaultVariants: {
      variant: 'card',
    },
  },
)

export type RadioItemVariants = VariantProps<typeof radioItemVariants>

export { default as RadioGroup } from './RadioGroup.vue'
export { default as RadioGroupItem } from './RadioGroupItem.vue'
