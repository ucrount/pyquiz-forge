import client from './client'
import type {
  Difficulty,
  ExerciseStatus,
  QuestionType,
} from '@/types/common'

interface ExportParams {
  knowledge_point_id?: number
  difficulty?: Difficulty
  question_type?: QuestionType
  status?: ExerciseStatus
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function ts(): string {
  const d = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(
    d.getHours(),
  )}${pad(d.getMinutes())}${pad(d.getSeconds())}`
}

export const exportApi = {
  async json(params: ExportParams = {}): Promise<void> {
    const r = await client.get('/export/json', {
      params,
      responseType: 'blob',
    })
    downloadBlob(r.data, `pyquiz-${ts()}.json`)
  },
  async markdown(params: ExportParams = {}): Promise<void> {
    const r = await client.get('/export/markdown', {
      params,
      responseType: 'blob',
    })
    downloadBlob(r.data, `pyquiz-${ts()}.md`)
  },
}
