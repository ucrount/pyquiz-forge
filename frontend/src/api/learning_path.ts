import client from './client'
import type { Chapter, ChapterWithKnowledgePoints } from '@/types/chapter'
import type { KnowledgePoint } from '@/types/knowledge_point'

export const learningPathApi = {
  tree(language?: string): Promise<ChapterWithKnowledgePoints[]> {
    const params = language ? { language } : {}
    return client.get('/learning-path', { params }).then((r) => r.data)
  },
  listChapters(language?: string): Promise<Chapter[]> {
    const params = language ? { language } : {}
    return client.get('/chapters', { params }).then((r) => r.data)
  },
  listKPs(chapterId?: number, language?: string): Promise<KnowledgePoint[]> {
    const params: Record<string, any> = {}
    if (chapterId) params.chapter_id = chapterId
    if (language) params.language = language
    return client.get('/knowledge-points', { params }).then((r) => r.data)
  },
  getKP(id: number): Promise<KnowledgePoint> {
    return client.get(`/knowledge-points/${id}`).then((r) => r.data)
  },
}
