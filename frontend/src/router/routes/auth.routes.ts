import type { RouteRecordRaw } from 'vue-router'

export const authRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@components/layout/AuthLayout.vue'),
    children: [
      {
        path: 'anmeldung',
        name: 'auth-login',
        component: () => import('@views/auth/LoginView.vue'),
      },
      {
        path: 'registrierung',
        name: 'auth-register',
        component: () => import('@views/auth/RegisterView.vue'),
      },
    ],
  },
]
