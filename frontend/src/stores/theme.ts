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

const STORAGE_KEY = 'pyquiz.theme'
const VALID_IDS = THEMES.map((t) => t.id)

function loadInitial(): ThemeId {
  const saved = localStorage.getItem(STORAGE_KEY) as ThemeId | null
  if (saved && VALID_IDS.includes(saved)) return saved
  return 'cyber'
}

function applyToDocument(id: ThemeId) {
  document.documentElement.setAttribute('data-theme', id)
}

export const useThemeStore = defineStore('theme', () => {
  const current = ref<ThemeId>(loadInitial())

  // Apply immediately on store creation
  applyToDocument(current.value)

  function setTheme(id: ThemeId) {
    current.value = id
  }

  watch(current, (v) => {
    applyToDocument(v)
    try {
      localStorage.setItem(STORAGE_KEY, v)
    } catch {
      // storage disabled — ignore
    }
  })

  return { current, setTheme }
})
