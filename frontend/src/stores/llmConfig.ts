import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { llmConfigApi } from '@/api'
import type { LLMConfig } from '@/types/llm_config'

export const useLLMConfigStore = defineStore('llmConfig', () => {
  const list = ref<LLMConfig[]>([])
  const loading = ref(false)
  const lastLoaded = ref<number>(0)

  const active = computed(() => list.value.find((c) => c.is_active) ?? null)

  async function refresh(force = false) {
    // Cache 30s unless force
    if (!force && Date.now() - lastLoaded.value < 30_000 && list.value.length) {
      return
    }
    loading.value = true
    try {
      list.value = await llmConfigApi.list()
      lastLoaded.value = Date.now()
    } finally {
      loading.value = false
    }
  }

  function clear() {
    list.value = []
    lastLoaded.value = 0
  }

  return { list, loading, active, refresh, clear }
})
