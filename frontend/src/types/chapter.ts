export interface Chapter {
  id: number
  code: string
  title: string
  order_index: number
  description: string
}

export interface ChapterWithKnowledgePoints extends Chapter {
  knowledge_points: import('./knowledge_point').KnowledgePoint[]
}
