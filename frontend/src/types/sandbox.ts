export type TestStatus =
  | 'pass'
  | 'wrong_answer'
  | 'runtime_error'
  | 'compile_error'
  | 'timeout'
  | 'infra_error'

export interface TestResult {
  test_index: number
  input: string
  expected: string
  actual: string
  status: TestStatus
  stdout: string
  stderr: string
  exit_code: number | null
  signal: string | null
  runtime_ms: number
}

export interface JudgeResult {
  language: string
  passed: number
  total: number
  all_passed: boolean
  early_stop: boolean
  results: TestResult[]
}

export interface JudgeRequest {
  source: string
  language?: string
}

export interface RunTestCase {
  input: string
  expected_output: string
}

export interface RunRequest {
  language: string
  source: string
  test_cases: RunTestCase[]
}

export interface SupportedLangs {
  languages: string[]
}
