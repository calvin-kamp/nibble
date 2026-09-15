import type { NavItem } from '@interfaces/navigation.types'

import { ScanBarcodeIcon, SearchIcon, WeightIcon } from '@lucide/vue'

export const trackingMenu: NavItem[] = [
  {
    routeName: 'tracking-weight',
    label: 'Gewicht',
    icon: WeightIcon,
  },
  {
    routeName: 'tracking-nutrition',
    label: 'Barcode scannen',
    icon: ScanBarcodeIcon,
  },
  {
    routeName: 'tracking-nutrition',
    label: 'Lebensmittel suchen',
    icon: SearchIcon,
  },
]
