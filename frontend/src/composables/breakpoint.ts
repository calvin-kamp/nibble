import type { ComputedRef, Ref } from 'vue'
import { computed, ref } from 'vue'

export const BREAKPOINTS = {
  tablet: 768,
  desktop: 1280,
} as const

export type BreakpointName = 'mobile' | 'tablet' | 'desktop'

const queries = {
  tablet: window.matchMedia(`(min-width: ${BREAKPOINTS.tablet}px)`),
  desktop: window.matchMedia(`(min-width: ${BREAKPOINTS.desktop}px)`),
}

const isTablet = ref<boolean>(queries.tablet.matches)
const isDesktop = ref<boolean>(queries.desktop.matches)

queries.tablet.addEventListener('change', (e) => (isTablet.value = e.matches))
queries.desktop.addEventListener('change', (e) => (isDesktop.value = e.matches))

const activeBreakpoint = computed<BreakpointName>(() => {
  if (isDesktop.value) return 'desktop'
  if (isTablet.value) return 'tablet'

  return 'mobile'
})

export function useBreakpoint(): {
  activeBreakpoint: ComputedRef<BreakpointName>
  isTablet: Ref<boolean>
  isDesktop: Ref<boolean>
} {
  return { activeBreakpoint, isTablet, isDesktop }
}
