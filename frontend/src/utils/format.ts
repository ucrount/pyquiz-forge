export function formatDateTime(s?: string | null): string {
  if (!s) return '-'
  const d = new Date(s)
  if (isNaN(d.getTime())) return s
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(
    d.getHours(),
  )}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

export function formatDuration(ms: number): string {
  if (!ms || ms < 0) return '-'
  if (ms < 1000) return `${ms} ms`
  return `${(ms / 1000).toFixed(2)} s`
}

export function formatTokens(n: number): string {
  if (!n) return '0'
  if (n < 1000) return String(n)
  return `${(n / 1000).toFixed(1)}k`
}
