/**
 * App store — theme, sidebar state, language.
 */
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type Theme = 'dark' | 'light'
export type Locale = string // e.g. 'en-US', 'zh-CN'

const STORAGE_THEME = 'qd_theme'
const STORAGE_LANG = 'qd_lang'

function getStoredTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_THEME) as Theme | null
  return stored ?? 'dark'
}

function getStoredLocale(): Locale {
  return localStorage.getItem(STORAGE_LANG) || 'en-US'
}

export const useAppStore = defineStore('app', () => {
  const theme = ref<Theme>(getStoredTheme())
  const sidebarCollapsed = ref(false)
  const language = ref<Locale>(getStoredLocale())

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setLanguage(locale: Locale) {
    language.value = locale
  }

  // Persist
  watch(theme, (v) => localStorage.setItem(STORAGE_THEME, v))
  watch(language, (v) => localStorage.setItem(STORAGE_LANG, v))

  return {
    theme,
    sidebarCollapsed,
    language,
    toggleTheme,
    toggleSidebar,
    setLanguage,
  }
})
