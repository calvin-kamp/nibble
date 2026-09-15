import type { FooterGroup } from '@interfaces/navigation.types'

export const footerNavigation: FooterGroup[] = [
  {
    id: 'footer-app-nav',
    title: 'App',
    links: [
      {
        routeName: 'recipe-list',
        label: 'Rezepte',
      },
      {
        routeName: 'calorie-calculator',
        label: 'Kalorienrechner',
      },
      {
        routeName: 'auth-login',
        label: 'Anmelden',
        visibility: 'guest',
      },
      {
        routeName: 'auth-register',
        label: 'Konto erstellen',
        visibility: 'guest',
      },
    ],
  },
  {
    id: 'footer-legal-nav',
    title: 'Rechtliches',
    links: [
      {
        routeName: 'legal-notice',
        label: 'Impressum',
      },
      {
        routeName: 'legal-privacy',
        label: 'Datenschutz',
      },
      {
        routeName: 'legal-tos',
        label: 'AGB',
      },
      {
        routeName: 'account',
        hash: '#einwilligungen',
        label: 'Einwilligungen verwalten',
        visibility: 'user',
      },
    ],
  },
]
