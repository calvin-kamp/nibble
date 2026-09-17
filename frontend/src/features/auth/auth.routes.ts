import type { RouteRecordRaw } from 'vue-router'

export const authRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@components/layout/AuthLayout.vue'),
    meta: { guestOnly: true },
    children: [
      {
        path: 'anmeldung',
        name: 'auth-login',
        meta: { title: 'Anmelden' },
        component: () => import('./views/LoginView.vue'),
      },
      {
        path: 'registrierung',
        name: 'auth-register',
        meta: { title: 'Konto erstellen' },
        component: () => import('./views/RegisterView.vue'),
      },
    ],
  },
]
