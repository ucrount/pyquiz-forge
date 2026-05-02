import client from './client'
import type { Chapter, ChapterWithKnowledgePoints } from '@/types/chapter'
import type { KnowledgePoint } from '@/types/knowledge_point'

export const learningPathApi = {
  tree(): Promise<ChapterWithKnowledgePoints[]> {
    return client.get('/learning-path').then((r) => r.data)
  },
  listChapters(): Promise<Chapter[]> {
    return client.get('/chapters').then((r) => r.data)
  },
  listKPs(chapterId?: number): Promise<KnowledgePoint[]> {
    const params = chapterId ? { chapter_id: chapterId } : {}
    return client.get('/knowledge-points', { params }).then((r) => r.data)
  },
  getKP(id: number): Promise<KnowledgePoint> {
    return client.get(`/knowledge-points/${id}`).then((r) => r.data)
  },
}
