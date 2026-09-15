import type { RouteRecordRaw } from 'vue-router'

export const legalRoutes: RouteRecordRaw[] = [
  {
    path: 'impressum',
    name: 'legal-notice',
    component: () => import('@views/legal/LegalNoticeView.vue'),
  },
  {
    path: 'datenschutz',
    name: 'legal-privacy',
    component: () => import('@views/legal/PrivacyPolicyView.vue'),
  },
  {
    path: 'agb',
    name: 'legal-tos',
    component: () => import('@views/legal/TermsOfServiceView.vue'),
  },
]
