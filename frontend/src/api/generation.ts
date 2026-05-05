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

export interface BatchJobCreated {
  job_id: string
  total: number
}

export interface JobEvent {
  ts: number
  kind: 'start' | 'success' | 'fail'
  label: string
  exercise_id: number | null
  error: string
  latency_ms: number
}

export interface JobProgress {
  id: string
  kind: string
  status: 'running' | 'done' | 'failed'
  total: number
  completed: number
  current: string
  succeeded: number[]
  failed: Array<{ difficulty: string; question_type: string; error: string }>
  events: JobEvent[]
  created_at: number
  finished_at: number | null
}

export const generationApi = {
  generate(data: GenerateRequest): Promise<Exercise> {
    return client.post('/exercises/generate', data).then((r) => r.data)
  },
  /** Async batch — returns a job id immediately. Poll getJob() for progress. */
  generateBatch(data: BatchGenerateRequest): Promise<BatchJobCreated> {
    return client.post('/exercises/generate/batch', data).then((r) => r.data)
  },
  /** Legacy alias kept for old callers (returns final BatchGenerateResult). */
  generateBatchSync(_data: BatchGenerateRequest): Promise<BatchGenerateResult> {
    throw new Error('Synchronous batch generation removed; use generateBatch + getJob.')
  },
  getJob(jobId: string): Promise<JobProgress> {
    // Send a header to silence the centralized error toast — caller wants to
    // poll silently and handle 404/etc itself.
    return client
      .get(`/generation-jobs/${jobId}`, { headers: { 'X-Silent': '1' } })
      .then((r) => r.data)
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
