const LABELS: Record<string, string> = {
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  python: 'Python',
  java: 'Java',
  go: 'Go',
  php: 'PHP',
  c: 'C',
  cpp: 'C++',
  ruby: 'Ruby',
  rust: 'Rust',
}

export function langLabel(lang: string): string {
  return LABELS[lang] || lang || '未知语言'
}

export function formatTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString('zh-CN')
}
