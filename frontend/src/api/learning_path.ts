import client from './client'
import type {
  Chapter,
  ChapterCascadeInfo,
  ChapterCreate,
  ChapterUpdate,
  ChapterWithKnowledgePoints,
} from '@/types/chapter'
import type {
  KnowledgePoint,
  KnowledgePointCascadeInfo,
  KnowledgePointCreate,
  KnowledgePointUpdate,
} from '@/types/knowledge_point'

export const learningPathApi = {
  // ===== Read =====
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

  // ===== Chapter mutations =====
  createChapter(data: ChapterCreate): Promise<Chapter> {
    return client.post('/chapters', data).then((r) => r.data)
  },
  updateChapter(id: number, data: ChapterUpdate): Promise<Chapter> {
    return client.put(`/chapters/${id}`, data).then((r) => r.data)
  },
  deleteChapter(id: number): Promise<void> {
    return client.delete(`/chapters/${id}`).then(() => void 0)
  },
  chapterCascadeInfo(id: number): Promise<ChapterCascadeInfo> {
    return client.get(`/chapters/${id}/cascade-info`).then((r) => r.data)
  },

  // ===== KP mutations =====
  createKP(data: KnowledgePointCreate): Promise<KnowledgePoint> {
    return client.post('/knowledge-points', data).then((r) => r.data)
  },
  updateKP(id: number, data: KnowledgePointUpdate): Promise<KnowledgePoint> {
    return client.put(`/knowledge-points/${id}`, data).then((r) => r.data)
  },
  deleteKP(id: number): Promise<void> {
    return client.delete(`/knowledge-points/${id}`).then(() => void 0)
  },
  kpCascadeInfo(id: number): Promise<KnowledgePointCascadeInfo> {
    return client.get(`/knowledge-points/${id}/cascade-info`).then((r) => r.data)
  },

  // ===== Helpers =====
  nextOrder(language: string, chapterId?: number): Promise<{ next: number }> {
    const params: Record<string, any> = { language }
    if (chapterId !== undefined) params.chapter_id = chapterId
    return client
      .get('/learning-path/next-order', { params })
      .then((r) => r.data)
  },
}
