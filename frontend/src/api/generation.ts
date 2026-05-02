import client from './client'
import type { Exercise } from '@/types/exercise'
import type {
  BatchGenerateRequest,
  BatchGenerateResult,
  GenerateRequest,
  GenerationLog,
  GenerationLogDetail,
  RegenerateRequest,
} from '@/types/generation'

export const generationApi = {
  generate(data: GenerateRequest): Promise<Exercise> {
    return client.post('/exercises/generate', data).then((r) => r.data)
  },
  generateBatch(data: BatchGenerateRequest): Promise<BatchGenerateResult> {
    return client.post('/exercises/generate/batch', data).then((r) => r.data)
  },
  regenerate(id: number, data: RegenerateRequest): Promise<Exercise> {
    return client.post(`/exercises/${id}/regenerate`, data).then((r) => r.data)
  },
  listLogs(page = 1, size = 20): Promise<GenerationLog[]> {
    return client
      .get('/generation-logs', { params: { page, size } })
      .then((r) => r.data)
  },
  getLog(id: number): Promise<GenerationLogDetail> {
    return client.get(`/generation-logs/${id}`).then((r) => r.data)
  },
}
