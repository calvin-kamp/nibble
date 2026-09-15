import type { NavItem } from '@interfaces/navigation.types'

import {
  CalculatorIcon,
  ChefHatIcon,
  HomeIcon,
  LayoutDashboardIcon,
  UserRoundIcon,
} from '@lucide/vue'

export const navigation: NavItem[] = [
  {
    routeName: 'dashboard',
    label: 'Übersicht',
    icon: LayoutDashboardIcon,
    visibility: 'user',
  },
  {
    routeName: 'public-landing',
    label: 'Start',
    icon: HomeIcon,
    visibility: 'guest',
  },
  {
    routeName: 'recipe-list',
    label: 'Rezepte',
    icon: ChefHatIcon,
    visibility: 'always',
  },
  {
    routeName: 'calorie-calculator',
    label: 'Rechner',
    icon: CalculatorIcon,
    visibility: 'always',
  },
  {
    routeName: 'auth-login',
    label: 'Anmelden',
    icon: UserRoundIcon,
    visibility: 'guest',
  },
]
