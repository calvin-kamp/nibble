import type { RouteLocationRaw } from 'vue-router'
import type { AuthNotice } from '@interfaces/auth.types'

import { authNotices } from './auth.data'

export function getRedirectTarget(redirect: unknown): RouteLocationRaw {
  if (typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')) {
    return redirect
  }

  return { name: 'dashboard' }
}

export function getNoticeText(notice: unknown): string | null {
  if (typeof notice !== 'string' || !(notice in authNotices)) return null

  return authNotices[notice as AuthNotice]
}
