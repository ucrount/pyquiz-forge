import client from './client'
import type {
  Difficulty,
  ExerciseStatus,
  PageResult,
  QuestionType,
} from '@/types/common'
import type {
  Exercise,
  ExerciseListItem,
  ExerciseUpdate,
} from '@/types/exercise'

interface ListParams {
  knowledge_point_id?: number
  difficulty?: Difficulty
  question_type?: QuestionType
  status?: ExerciseStatus
  min_score?: number
  page?: number
  size?: number
}

export const exerciseApi = {
  list(params: ListParams = {}): Promise<PageResult<ExerciseListItem>> {
    return client.get('/exercises', { params }).then((r) => r.data)
  },
  get(id: number): Promise<Exercise> {
    return client.get(`/exercises/${id}`).then((r) => r.data)
  },
  update(id: number, data: ExerciseUpdate): Promise<Exercise> {
    return client.patch(`/exercises/${id}`, data).then((r) => r.data)
  },
  remove(id: number): Promise<void> {
    return client.delete(`/exercises/${id}`).then(() => void 0)
  },
  bulkDelete(ids: number[]): Promise<{ deleted: number }> {
    return client
      .post('/exercises/bulk-delete', { ids })
      .then((r) => r.data)
  },
}
