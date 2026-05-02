import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { Language } from '@/types/common'

const STORAGE_KEY = 'pyquiz.language'

function loadInitial(): Language {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'python' || saved === 'java' || saved === 'go' || saved === 'javascript') {
    return saved
  }
  return 'python'
}

export const useLanguageStore = defineStore('language', () => {
  const current = ref<Language>(loadInitial())

  function setLanguage(lang: Language) {
    current.value = lang
  }

  // Persist to localStorage on every change
  watch(current, (v) => {
    try {
      localStorage.setItem(STORAGE_KEY, v)
    } catch {
      // storage may be disabled — ignore
    }
  })

  return { current, setLanguage }
})
