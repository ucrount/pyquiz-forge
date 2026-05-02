import type { Language } from './common'

export interface Chapter {
  id: number
  code: string
  title: string
  order_index: number
  description: string
  language: Language | string
}

export interface ChapterWithKnowledgePoints extends Chapter {
  knowledge_points: import('./knowledge_point').KnowledgePoint[]
}

export interface ChapterCreate {
  code: string
  title: string
  language: Language | string
  order_index?: number
  description?: string
}

export interface ChapterUpdate {
  code?: string
  title?: string
  language?: Language | string
  order_index?: number
  description?: string
}

export interface ChapterCascadeInfo {
  chapter_id: number
  knowledge_points: number
  exercises: number
}
