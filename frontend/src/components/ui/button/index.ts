import { focusRingDestructive, focusRingOffset, invalidRing, transitionInteractive } from '@/lib/interactive-styles.ts'
import type { VariantProps } from 'class-variance-authority'
import { cva } from 'class-variance-authority'

export { default as Button } from './Button.vue'

export const buttonVariants = cva(
  [
    focusRingOffset,
    invalidRing,
    transitionInteractive,
    'group/button inline-flex shrink-0 items-center justify-center bg-clip-padding border border-transparent rounded-lg text-sm font-medium whitespace-nowrap select-none disabled:pointer-events-none disabled:opacity-50 active:not-aria-[haspopup]:translate-y-px [&_svg:not([class*=size-])]:size-4 [&_svg]:pointer-events-none [&_svg]:shrink-0',
  ],
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/80',
        outline: 'bg-input/30 border-border hover:bg-input/50 hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 aria-expanded:bg-secondary aria-expanded:text-secondary-foreground',
        ghost: 'hover:bg-muted dark:hover:bg-muted/50 hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground',
        destructive: [focusRingDestructive, 'bg-destructive/10 dark:bg-destructive/20 text-destructive hover:bg-destructive/20 dark:hover:bg-destructive/30'],
        link: 'text-primary underline underline-offset-4 hover:text-primary/80'
      },
      size: {
        'default': 'h-11 gap-2 px-4',
        'icon': 'size-11 rounded-full',
        'icon-lg': 'size-13 rounded-full [&_svg:not([class*=size-])]:size-5',
        'link': 'h-11'
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)
export type ButtonVariants = VariantProps<typeof buttonVariants>
