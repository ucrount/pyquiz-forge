import type { Difficulty, QuestionType } from './common'
import type { Exercise } from './exercise'

export interface GenerateRequest {
  knowledge_point_id: number
  difficulty: Difficulty
  question_type: QuestionType
  llm_config_id?: number
}

export interface BatchItem {
  difficulty: Difficulty
  question_type: QuestionType
  count: number
}

export interface BatchGenerateRequest {
  knowledge_point_id: number
  items: BatchItem[]
  llm_config_id?: number
}

export interface BatchGenerateResult {
  succeeded: Exercise[]
  failed: Array<{
    difficulty: string
    question_type: string
    error: string
  }>
}

export interface RegenerateRequest {
  mode: 'new' | 'overwrite'
  llm_config_id?: number
}

export interface GenerationLog {
  id: number
  llm_config_id: number | null
  knowledge_point_id: number | null
  difficulty: string
  question_type: string
  parsed_ok: boolean
  error_message: string
  latency_ms: number
  prompt_tokens: number
  completion_tokens: number
}

export interface GenerationLogDetail extends GenerationLog {
  prompt: string
  raw_response: string
}
