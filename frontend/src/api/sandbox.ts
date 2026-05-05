import client from './client'
import type {
  JudgeRequest,
  JudgeResult,
  RunRequest,
  SupportedLangs,
} from '@/types/sandbox'

export const sandboxApi = {
  listLanguages(): Promise<SupportedLangs> {
    return client.get('/sandbox/languages').then((r) => r.data)
  },
  run(req: RunRequest): Promise<JudgeResult> {
    return client.post('/sandbox/run', req).then((r) => r.data)
  },
  judgeExercise(exerciseId: number, req: JudgeRequest): Promise<JudgeResult> {
    return client.post(`/sandbox/judge/${exerciseId}`, req).then((r) => r.data)
  },
}
