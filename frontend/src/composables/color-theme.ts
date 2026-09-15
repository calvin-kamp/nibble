import { ref } from 'vue'

type Theme = 'light' | 'dark'

const KEY = 'color-theme'

function readStoredTheme(): Theme | null {
  const stored = localStorage.getItem(KEY)

  return stored === 'dark' || stored === 'light' ? stored : null
}

function resolveInitialTheme(): Theme {
  return (
    readStoredTheme() ??
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  )
}

const theme = ref<Theme>(resolveInitialTheme())

document.documentElement.classList.toggle('dark', theme.value === 'dark')

export function useColorTheme() {
  function applyTheme(next: Theme): void {
    theme.value = next
    document.documentElement.classList.toggle('dark', next === 'dark')
    localStorage.setItem(KEY, next)
  }

  function changeTheme(): void {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  return { theme, changeTheme }
}
