import { apiFetch } from './http'
import type { Defect, RiskLevel } from '../types'

interface ApiDefect {
  line: number
  level: string
  cat: string
  title: string
  desc: string
  fix: string
  rule_id?: string
  cwe?: string
  code?: string
  source?: string
}

function mapDefect(d: ApiDefect): Defect {
  return {
    line: d.line,
    level: d.level as RiskLevel,
    cat: d.cat,
    title: d.title,
    desc: d.desc,
    fix: d.fix,
    code: d.code,
    source: d.source as Defect['source'],
  }
}

export interface ReviewResult {
  review_id: number
  defects: Defect[]
  summary: { total: number; high: number; mid: number; low: number }
  duration_ms: number
}

export interface ReviewListItem {
  id: number
  file_name: string
  language: string
  total: number
  high: number
  mid: number
  low: number
  duration_ms: number
  created_at: string
}

export interface ReviewDetail {
  id: number
  file_name: string
  language: string
  code: string
  total: number
  high: number
  mid: number
  low: number
  duration_ms: number
  created_at: string
  defects: Defect[]
}

// 提交审查（后端跑 Semgrep + 落库）
export async function reviewCode(code: string, language: string, ruleset = 'local', file_name = ''): Promise<ReviewResult> {
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), 60000)
  try {
    const resp = await apiFetch('/api/review', {
      method: 'POST',
      body: JSON.stringify({ code, language, ruleset, file_name }),
      signal: controller.signal,
    })
    if (!resp.ok) {
      let detail = `审查失败(${resp.status})`
      try {
        detail = (await resp.json()).detail || detail
      } catch {
        /* ignore */
      }
      throw new Error(detail)
    }
    const data = await resp.json()
    return {
      review_id: data.review_id,
      defects: (data.defects as ApiDefect[]).map(mapDefect),
      summary: data.summary,
      duration_ms: data.duration_ms,
    }
  } finally {
    window.clearTimeout(timer)
  }
}

export async function fetchReviews(): Promise<ReviewListItem[]> {
  const resp = await apiFetch('/api/reviews')
  if (!resp.ok) throw new Error('加载审查历史失败')
  return (await resp.json()) as ReviewListItem[]
}

export async function fetchReviewDetail(id: number): Promise<ReviewDetail> {
  const resp = await apiFetch(`/api/reviews/${id}`)
  if (!resp.ok) throw new Error('加载审查详情失败')
  const data = await resp.json()
  return { ...data, defects: (data.defects as ApiDefect[]).map(mapDefect) }
}
