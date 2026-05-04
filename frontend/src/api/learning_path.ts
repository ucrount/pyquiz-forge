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
  MasteryCounts,
} from '@/types/knowledge_point'
import type { Mastery } from '@/types/common'

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
  listKPs(
    chapterId?: number,
    language?: string,
    mastery?: Mastery[],
  ): Promise<KnowledgePoint[]> {
    const params = new URLSearchParams()
    if (chapterId) params.append('chapter_id', String(chapterId))
    if (language) params.append('language', language)
    if (mastery && mastery.length) {
      for (const m of mastery) params.append('mastery', m)
    }
    return client.get('/knowledge-points', { params }).then((r) => r.data)
  },
  getKP(id: number): Promise<KnowledgePoint> {
    return client.get(`/knowledge-points/${id}`).then((r) => r.data)
  },
  masteryCounts(language?: string): Promise<MasteryCounts> {
    const params = language ? { language } : {}
    return client
      .get('/knowledge-points/mastery-counts', { params })
      .then((r) => r.data)
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

  // ===== Learning content + mastery (v0.3) =====
  generateContent(id: number, llmConfigId?: number): Promise<KnowledgePoint> {
    const params = llmConfigId ? { llm_config_id: llmConfigId } : {}
    return client
      .post(`/knowledge-points/${id}/generate-content`, null, { params })
      .then((r) => r.data)
  },
  updateContent(id: number, content: string): Promise<KnowledgePoint> {
    return client
      .put(`/knowledge-points/${id}/content`, { content })
      .then((r) => r.data)
  },
  setMastery(id: number, mastery: Mastery, note?: string): Promise<KnowledgePoint> {
    return client
      .patch(`/knowledge-points/${id}/mastery`, { mastery, note })
      .then((r) => r.data)
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
