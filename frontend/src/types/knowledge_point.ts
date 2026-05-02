import type { Language } from './common'

export interface KnowledgePoint {
  id: number
  chapter_id: number
  code: string
  title: string
  order_index: number
  keywords: string[]
  description: string
  language: Language | string
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
