import client from './client'
import type {
  Difficulty,
  ExerciseStatus,
  QuestionType,
} from '@/types/common'
import type { Exercise } from '@/types/exercise'

export interface PracticeSessionRequest {
  language?: string
  chapter_id?: number
  knowledge_point_id?: number
  difficulties?: Difficulty[]
  question_types?: QuestionType[]
  min_score?: number
  status?: ExerciseStatus
  size?: number
  random_order?: boolean
}

export interface PracticeSessionResponse {
  questions: Exercise[]
  total_available: number
}

export const practiceApi = {
  createSession(req: PracticeSessionRequest): Promise<PracticeSessionResponse> {
    return client.post('/practice/session', req).then((r) => r.data)
  },
}
