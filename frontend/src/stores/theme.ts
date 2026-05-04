import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeId = 'cyber' | 'nebula' | 'matrix' | 'sunset' | 'minimal'

export interface ThemeMeta {
  id: ThemeId
  name: string
  description: string
  preview: { bg: string; primary: string; secondary: string }
}

export const THEMES: ThemeMeta[] = [
  {
    id: 'cyber',
    name: 'Cyber',
    description: '默认 — 深海军蓝 + 青紫霓虹',
    preview: { bg: '#050810', primary: '#00d4ff', secondary: '#b54aff' },
  },
  {
    id: 'nebula',
    name: 'Nebula',
    description: '深紫 + 洋红霓虹，浪漫宇宙',
    preview: { bg: '#0c0420', primary: '#ff4dd6', secondary: '#9d4dff' },
  },
  {
    id: 'matrix',
    name: 'Matrix',
    description: '黑绿 + 霓虹绿，黑客经典',
    preview: { bg: '#001005', primary: '#00ff7e', secondary: '#7effc7' },
  },
  {
    id: 'sunset',
    name: 'Sunset',
    description: '暗酒红 + 橙粉，温暖夕阳',
    preview: { bg: '#1a0a0e', primary: '#ff8033', secondary: '#ff4d8d' },
  },
  {
    id: 'minimal',
    name: 'Minimal',
    description: '纯黑 + 单白，无装饰极简',
    preview: { bg: '#0a0a0a', primary: '#e0e0e0', secondary: '#a0a0a0' },
  },
]

export type ContrastLevel = 'normal' | 'high'
export type FontSize = 'small' | 'normal' | 'large' | 'xlarge'

export const CONTRAST_OPTIONS: { value: ContrastLevel; label: string; hint: string }[] = [
  { value: 'normal', label: '标准', hint: '默认对比度，沉浸感强' },
  { value: 'high', label: '高对比度', hint: '正文文字更亮，看着更清楚' },
]

export const FONT_OPTIONS: { value: FontSize; label: string; hint: string }[] = [
  { value: 'small', label: '紧凑', hint: '12.5 px' },
  { value: 'normal', label: '标准', hint: '14 px' },
  { value: 'large', label: '舒适', hint: '16 px' },
  { value: 'xlarge', label: '阅读', hint: '17.5 px' },
]

const VALID_THEMES = THEMES.map((t) => t.id)
const VALID_CONTRAST: ContrastLevel[] = ['normal', 'high']
const VALID_FONT: FontSize[] = ['small', 'normal', 'large', 'xlarge']

const STORAGE_KEY = 'pyquiz.theme'
const CONTRAST_KEY = 'pyquiz.contrast'
const FONT_KEY = 'pyquiz.fontSize'

function pick<T extends string>(
  v: string | null,
  valid: readonly T[],
  fallback: T,
): T {
  return v && (valid as readonly string[]).includes(v) ? (v as T) : fallback
}

function applyToDocument(
  theme: ThemeId,
  contrast: ContrastLevel,
  fontSize: FontSize,
) {
  const html = document.documentElement
  html.setAttribute('data-theme', theme)
  // contrast=normal → remove the attr to keep CSS clean
  if (contrast === 'high') html.setAttribute('data-contrast', 'high')
  else html.removeAttribute('data-contrast')
  html.setAttribute('data-font', fontSize)
}

export const useThemeStore = defineStore('theme', () => {
  const current = ref<ThemeId>(
    pick(localStorage.getItem(STORAGE_KEY), VALID_THEMES, 'cyber'),
  )
  const contrast = ref<ContrastLevel>(
    pick(localStorage.getItem(CONTRAST_KEY), VALID_CONTRAST, 'normal'),
  )
  const fontSize = ref<FontSize>(
    pick(localStorage.getItem(FONT_KEY), VALID_FONT, 'normal'),
  )

  // Apply immediately on store creation
  applyToDocument(current.value, contrast.value, fontSize.value)

  function setTheme(id: ThemeId) { current.value = id }
  function setContrast(c: ContrastLevel) { contrast.value = c }
  function setFontSize(f: FontSize) { fontSize.value = f }

  watch([current, contrast, fontSize], () => {
    applyToDocument(current.value, contrast.value, fontSize.value)
    try {
      localStorage.setItem(STORAGE_KEY, current.value)
      localStorage.setItem(CONTRAST_KEY, contrast.value)
      localStorage.setItem(FONT_KEY, fontSize.value)
    } catch {}
  })

  return { current, contrast, fontSize, setTheme, setContrast, setFontSize }
})
