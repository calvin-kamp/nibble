import type { UserMenuItem } from '@interfaces/navigation.types'

import { LogOutIcon, UserRoundIcon } from '@lucide/vue'

export const userMenu: UserMenuItem[] = [
  {
    routeName: 'account',
    label: 'Konto',
    icon: UserRoundIcon,
    variant: 'ghost',
  },
  {
    action: 'logout',
    label: 'Abmelden',
    icon: LogOutIcon,
    variant: 'destructive',
  },
]
