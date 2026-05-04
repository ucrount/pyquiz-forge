/**
 * Static answer-grading helpers used by the practice mode.
 * No network calls; pure string comparison with normalization.
 */
import type { Exercise } from '@/types/exercise'

export type GradeResult = 'correct' | 'wrong' | 'no-grade' | 'skipped'

/** Normalize text for comparison: lowercase, trim, normalize whitespace+punct. */
export function normalizeText(s: string): string {
  return (s || '')
    .replace(/[，]/g, ',')
    .replace(/[。]/g, '.')
    .replace(/[；]/g, ';')
    .replace(/[：]/g, ':')
    .replace(/[（]/g, '(')
    .replace(/[）]/g, ')')
    .replace(/[“”]/g, '"')
    .replace(/[‘’]/g, "'")
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
}

/** Normalize for choice answers: extract letter A/B/C/D. */
export function normalizeChoice(s: string): string {
  const m = (s || '').trim().match(/^[A-Da-d]/)
  return m ? m[0].toUpperCase() : (s || '').trim().toUpperCase()
}

/** Normalize for judge: 正确/对/T/Y/yes/true vs 错误/错/F/N/no/false. */
export function normalizeJudge(s: string): 'TRUE' | 'FALSE' | string {
  const t = (s || '').trim().toLowerCase()
  if (
    ['正确', '对', 'true', 't', 'y', 'yes', '是'].includes(t)
  ) {
    return 'TRUE'
  }
  if (['错误', '错', 'false', 'f', 'n', 'no', '否'].includes(t)) {
    return 'FALSE'
  }
  return t
}

export function gradeAnswer(
  question: Exercise,
  userAnswer: string | null,
): GradeResult {
  if (userAnswer === null || userAnswer === undefined) return 'skipped'
  const ans = (userAnswer || '').trim()
  const std = (question.standard_answer || '').trim()
  if (!std) return 'no-grade'

  switch (question.question_type) {
    case 'choice':
      return normalizeChoice(ans) === normalizeChoice(std) ? 'correct' : 'wrong'
    case 'judge':
      return normalizeJudge(ans) === normalizeJudge(std) ? 'correct' : 'wrong'
    case 'fill':
    case 'read':
    case 'complete':
      return normalizeText(ans) === normalizeText(std) ? 'correct' : 'wrong'
    case 'program':
    case 'debug':
      return 'no-grade'
    default:
      return 'no-grade'
  }
}
