import type { VariantProps } from 'class-variance-authority'

import { cva } from 'class-variance-authority'

const textLink = 'font-medium underline decoration-1 underline-offset-3 hover:decoration-2'

export const buttonVariants = cva(
  [
    'relative',
    'inline-flex items-center justify-center gap-2',
    'transition-interactive',
    'focus-visible:focus-ring',
    'disabled:inactive',
  ],
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        ghost: 'text-foreground hover:bg-muted',
        destructive:
          'bg-destructive/10 text-destructive hover:bg-destructive/20 focus-visible:focus-ring-destructive',
        link: textLink,
      },
      size: {
        default: 'h-11 rounded-md px-4',
        icon: 'size-11 rounded-full',
        'icon-sm': 'size-7 rounded-full after:absolute after:-inset-2',
        'icon-lg': 'size-13 rounded-full',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export type ButtonVariants = VariantProps<typeof buttonVariants>

export const linkVariants = {
  inline: ['rounded-sm', textLink],
  standalone: [
    'relative',
    '-ms-2 inline-flex min-h-11 items-center px-2',
    'text-muted-foreground underline-offset-3',
    'rounded-md',
    'transition-interactive',
    'hover:text-foreground hover:underline',
    'before:absolute before:inset-y-3.5 before:left-0 before:w-0.5 before:rounded-full',
    'aria-[current=page]:font-medium aria-[current=page]:text-foreground aria-[current=page]:before:bg-primary',
  ].join(' '),
} as const

export type LinkVariant = keyof typeof linkVariants

export const calloutVariants = cva(['flex items-start gap-2 p-3 rounded-xl border'], {
  variants: {
    variant: {
      neutral: 'bg-muted/60 border-border',
      info: 'bg-primary/8 border-primary/30',
      warning: 'bg-destructive/8 border-destructive/30',
    },
  },
  defaultVariants: {
    variant: 'neutral',
  },
})

export type CalloutVariants = VariantProps<typeof calloutVariants>

export const badgeVariants = cva(
  'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-sm font-medium whitespace-nowrap',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground',
        secondary: 'bg-secondary text-secondary-foreground',
        outline: 'border border-border text-muted-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

export type BadgeVariants = VariantProps<typeof badgeVariants>
