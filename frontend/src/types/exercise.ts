import type { Difficulty, ExerciseStatus, QuestionType } from './common'

export interface TestCase {
  input: string
  expected_output: string
}

export interface Exercise {
  id: number
  title: string
  knowledge_point_id: number
  difficulty: Difficulty
  question_type: QuestionType
  description: string
  example_input: string
  example_output: string
  hint: string
  standard_answer: string
  reference_code: string
  test_cases: TestCase[]
  explanation: string
  common_mistakes: string
  extra: Record<string, unknown>
  llm_config_id: number | null
  generation_log_id: number | null
  status: ExerciseStatus
}

export interface ExerciseListItem {
  id: number
  title: string
  knowledge_point_id: number
  difficulty: Difficulty
  question_type: QuestionType
  status: ExerciseStatus
}

export interface ExerciseUpdate {
  title?: string
  description?: string
  example_input?: string
  example_output?: string
  hint?: string
  standard_answer?: string
  reference_code?: string
  test_cases?: TestCase[]
  explanation?: string
  common_mistakes?: string
  extra?: Record<string, unknown>
  status?: ExerciseStatus
}
