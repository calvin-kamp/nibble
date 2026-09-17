import type { RouteLocationRaw } from 'vue-router'
import type { AuthNotice } from '@interfaces/auth.types'

import { nextTick } from 'vue'
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

export async function focusFirstInvalidField(form: HTMLFormElement | null): Promise<void> {
  await nextTick()

  form?.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus()
}
