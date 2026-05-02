import client from './client'
import type { Exercise, ScoreDimensions } from '@/types/exercise'

export interface ScoreResult {
  overall: number
  dimensions: ScoreDimensions
  comment: string
}

export interface BatchScoreResult {
  succeeded: Array<{ id: number; score: ScoreResult }>
  failed: Array<{ id: number; error: string }>
}

export const scoringApi = {
  score(id: number, llm_config_id?: number): Promise<Exercise> {
    return client
      .post(`/exercises/${id}/score`, { llm_config_id })
      .then((r) => r.data)
  },
  scoreBatch(
    ids: number[],
    llm_config_id?: number,
  ): Promise<BatchScoreResult> {
    return client
      .post('/exercises/score/batch', { ids, llm_config_id })
      .then((r) => r.data)
  },
}
