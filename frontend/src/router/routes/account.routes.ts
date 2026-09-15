import type { RouteRecordRaw } from 'vue-router'

export const accountRoutes: RouteRecordRaw[] = [
  {
    path: 'konto',
    name: 'account',
    component: () => import('@views/account/AccountView.vue'),
  },
]
