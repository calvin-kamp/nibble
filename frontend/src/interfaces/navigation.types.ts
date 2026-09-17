import type { LucideIcon } from '@lucide/vue'
import type { ButtonVariants } from '@components/ui/variants'

export type NavVisibility = 'always' | 'user' | 'guest'

export interface NavItem {
  routeName: string
  label: string
  icon: LucideIcon
  visibility?: NavVisibility
}

export interface UserMenuItem {
  routeName?: string
  action?: 'logout'
  label: string
  icon: LucideIcon
  variant: ButtonVariants['variant']
}

export interface FooterLink {
  routeName: string
  hash?: string
  label: string
  visibility?: NavVisibility
}

export interface FooterGroup {
  id: string
  title: string
  links: FooterLink[]
}
