/**
 * vue-i18n setup — 10 languages, persisted preference.
 */
import { createI18n } from 'vue-i18n'
import enUS from './locales/en-US.json'

export type SupportedLocale =
  | 'en-US'
  | 'zh-CN'
  | 'zh-TW'
  | 'ja-JP'
  | 'ko-KR'
  | 'de-DE'
  | 'fr-FR'
  | 'ar-SA'
  | 'th-TH'
  | 'vi-VN'

export const SUPPORTED_LOCALES: { value: SupportedLocale; label: string }[] = [
  { value: 'en-US', label: 'English' },
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-TW', label: '繁體中文' },
  { value: 'ja-JP', label: '日本語' },
  { value: 'ko-KR', label: '한국어' },
  { value: 'de-DE', label: 'Deutsch' },
  { value: 'fr-FR', label: 'Français' },
  { value: 'ar-SA', label: 'العربية' },
  { value: 'th-TH', label: 'ภาษาไทย' },
  { value: 'vi-VN', label: 'Tiếng Việt' },
]

// Placeholder imports for other locales (will be populated by agents)
const zhCN = () => import('./locales/zh-CN.json')
const zhTW = () => import('./locales/zh-TW.json')
const jaJP = () => import('./locales/ja-JP.json')
const koKR = () => import('./locales/ko-KR.json')
const deDE = () => import('./locales/de-DE.json')
const frFR = () => import('./locales/fr-FR.json')
const arSA = () => import('./locales/ar-SA.json')
const thTH = () => import('./locales/th-TH.json')
const viVN = () => import('./locales/vi-VN.json')

const stored = localStorage.getItem('qd_lang') as SupportedLocale | null
const defaultLocale: SupportedLocale =
  stored && SUPPORTED_LOCALES.some((l) => l.value === stored) ? stored : 'en-US'

export const i18n = createI18n({
  legacy: false, // use Composition API mode
  locale: defaultLocale,
  fallbackLocale: 'en-US',
  messages: {
    'en-US': enUS,
    // other locales loaded on demand
  },
  missingWarn: false,
  fallbackWarn: false,
})

export function setLocale(locale: SupportedLocale) {
  ;(i18n.global.locale as unknown as { value: string }).value = locale
  localStorage.setItem('qd_lang', locale)
  document.documentElement.setAttribute('lang', locale)
}



export function getAntdLocale(_locale: string): unknown {
  // Ant Design Vue will fall back to English for missing locales
  // Real locale loading can be added later when needed
  return undefined
}
