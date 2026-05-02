import type { Provider } from './common'

export interface LLMConfig {
  id: number
  name: string
  provider: Provider
  api_key: string // server returns masked
  api_base: string
  model: string
  temperature: number
  max_tokens: number
  extra: Record<string, unknown>
  is_active: boolean
}

export interface LLMConfigCreate {
  name: string
  provider: Provider
  api_key: string
  api_base?: string
  model: string
  temperature?: number
  max_tokens?: number
  extra?: Record<string, unknown>
}

export type LLMConfigUpdate = Partial<LLMConfigCreate>

export interface LLMTestResult {
  ok: boolean
  message: string
  latency_ms: number
}
