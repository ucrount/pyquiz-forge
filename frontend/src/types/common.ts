// Mirror of app/schemas/common.py

export type Difficulty =
  | 'entry'
  | 'basic'
  | 'intermediate'
  | 'advanced'
  | 'comprehensive'

export const DIFFICULTY_LABEL: Record<Difficulty, string> = {
  entry: '入门',
  basic: '基础',
  intermediate: '中级',
  advanced: '进阶',
  comprehensive: '综合',
}

export const DIFFICULTY_COLOR: Record<Difficulty, string> = {
  entry: '#909399',
  basic: '#67c23a',
  intermediate: '#409eff',
  advanced: '#e6a23c',
  comprehensive: '#f56c6c',
}

export const DIFFICULTY_OPTIONS: { value: Difficulty; label: string }[] = (
  Object.keys(DIFFICULTY_LABEL) as Difficulty[]
).map((v) => ({ value: v, label: DIFFICULTY_LABEL[v] }))

export type QuestionType =
  | 'choice'
  | 'fill'
  | 'judge'
  | 'read'
  | 'complete'
  | 'program'
  | 'debug'

export const QUESTION_TYPE_LABEL: Record<QuestionType, string> = {
  choice: '选择题',
  fill: '填空题',
  judge: '判断题',
  read: '代码阅读题',
  complete: '代码补全题',
  program: '编程实现题',
  debug: 'Debug 修错题',
}

export const QUESTION_TYPE_OPTIONS: { value: QuestionType; label: string }[] = (
  Object.keys(QUESTION_TYPE_LABEL) as QuestionType[]
).map((v) => ({ value: v, label: QUESTION_TYPE_LABEL[v] }))

export type Provider = 'openai' | 'deepseek' | 'qwen' | 'moonshot' | 'claude'

export const PROVIDER_OPTIONS: { value: Provider; label: string }[] = [
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'qwen', label: 'Qwen / 通义千问' },
  { value: 'moonshot', label: 'Moonshot / Kimi' },
  { value: 'claude', label: 'Claude' },
]

// === Languages (mirror of LANGUAGE_LABELS in app/llm/prompts.py) ===

export type Language = 'python' | 'java' | 'go' | 'javascript'

export const LANGUAGE_LABEL: Record<Language, string> = {
  python: 'Python',
  java: 'Java',
  go: 'Go',
  javascript: 'JavaScript',
}

export const LANGUAGE_COLOR: Record<Language, string> = {
  python: '#3776ab',
  java: '#ed8b00',
  go: '#00add8',
  javascript: '#f7df1e',
}

export const LANGUAGE_OPTIONS: { value: Language; label: string }[] = (
  Object.keys(LANGUAGE_LABEL) as Language[]
).map((v) => ({ value: v, label: LANGUAGE_LABEL[v] }))

export type ExerciseStatus = 'draft' | 'published' | 'archived'

export const EXERCISE_STATUS_LABEL: Record<ExerciseStatus, string> = {
  draft: '草稿',
  published: '已发布',
  archived: '已归档',
}

// === Mastery (per-KP learning state) ===

export type Mastery = 'not_started' | 'learning' | 'mastered' | 'unknown'

export const MASTERY_LABEL: Record<Mastery, string> = {
  not_started: '未开始',
  learning: '学习中',
  mastered: '已掌握',
  unknown: '不懂',
}

export const MASTERY_COLOR: Record<Mastery, string> = {
  not_started: '#94a3b8',
  learning: '#5ce0ff',
  mastered: '#00ff9d',
  unknown: '#ff4d8d',
}

export const MASTERY_ICON: Record<Mastery, string> = {
  not_started: '○',
  learning: '📖',
  mastered: '✓',
  unknown: '❓',
}

export const MASTERY_OPTIONS: { value: Mastery; label: string }[] = (
  Object.keys(MASTERY_LABEL) as Mastery[]
).map((v) => ({ value: v, label: MASTERY_LABEL[v] }))

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface MessageResponse {
  message: string
}
