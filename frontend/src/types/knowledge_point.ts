import type { Language, Mastery } from './common'

export interface KnowledgePoint {
  id: number
  chapter_id: number
  code: string
  title: string
  order_index: number
  keywords: string[]
  description: string
  language: Language | string

  // Learning content + mastery (v0.3)
  content: string
  mastery: Mastery
  mastery_note: string
  mastery_updated_at: string | null
}

export interface KnowledgePointCreate {
  chapter_id: number
  code: string
  title: string
  language: Language | string
  order_index?: number
  keywords?: string[]
  description?: string
}

export interface KnowledgePointUpdate {
  chapter_id?: number
  code?: string
  title?: string
  language?: Language | string
  order_index?: number
  keywords?: string[]
  description?: string
}

export interface KnowledgePointCascadeInfo {
  knowledge_point_id: number
  exercises: number
}

export interface MasteryCounts {
  not_started: number
  learning: number
  mastered: number
  unknown: number
}
