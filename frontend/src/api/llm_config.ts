import client from './client'
import type {
  LLMConfig,
  LLMConfigCreate,
  LLMConfigUpdate,
  LLMTestResult,
} from '@/types/llm_config'

export const llmConfigApi = {
  list(): Promise<LLMConfig[]> {
    return client.get('/llm-configs').then((r) => r.data)
  },
  get(id: number): Promise<LLMConfig> {
    return client.get(`/llm-configs/${id}`).then((r) => r.data)
  },
  create(data: LLMConfigCreate): Promise<LLMConfig> {
    return client.post('/llm-configs', data).then((r) => r.data)
  },
  update(id: number, data: LLMConfigUpdate): Promise<LLMConfig> {
    return client.put(`/llm-configs/${id}`, data).then((r) => r.data)
  },
  remove(id: number): Promise<void> {
    return client.delete(`/llm-configs/${id}`).then(() => void 0)
  },
  activate(id: number): Promise<LLMConfig> {
    return client.post(`/llm-configs/${id}/activate`).then((r) => r.data)
  },
  test(id: number): Promise<LLMTestResult> {
    return client.post(`/llm-configs/${id}/test`).then((r) => r.data)
  },
}
