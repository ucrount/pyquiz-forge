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
