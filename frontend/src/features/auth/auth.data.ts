import type { LucideIcon } from '@lucide/vue'
import type { AuthNotice } from '@interfaces/auth.types'

import { BookmarkIcon, CalculatorIcon, ChartLineIcon, UtensilsIcon } from '@lucide/vue'

interface Benefit {
  icon: LucideIcon
  text: string
}

interface BenefitPanel {
  title: string
  benefits: Benefit[]
}

export const benefitPanel: BenefitPanel = {
  title: 'Kalorien, Gewicht und Rezepte an einem Ort',
  benefits: [
    { icon: CalculatorIcon, text: 'Kalorienbedarf berechnen und als Tagesziel übernehmen' },
    {
      icon: UtensilsIcon,
      text: 'Mahlzeiten erfassen und sehen, wie viele Kalorien heute noch bleiben',
    },
    { icon: ChartLineIcon, text: 'Gewicht eintragen und den Verlauf über Wochen verfolgen' },
    { icon: BookmarkIcon, text: 'Rezepte finden und für später speichern' },
  ],
}

export const authErrorMessages = {
  loginFailed: 'E-Mail-Adresse oder Passwort stimmt nicht.',
  unreachable: 'Nibble ist gerade nicht erreichbar. Später erneut versuchen.',
  emailTaken: 'Für diese E-Mail-Adresse gibt es schon ein Konto. Stattdessen anmelden.',
}

export const authNotices: Record<AuthNotice, string> = {
  'session-expired': 'Die Sitzung ist abgelaufen. Erneut anmelden, um weiterzumachen.',
  'logged-out': 'Du bist abgemeldet.',
}
