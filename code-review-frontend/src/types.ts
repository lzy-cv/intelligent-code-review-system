export type RiskLevel = 'high' | 'mid' | 'low'
export type RiskFilter = 'all' | RiskLevel

export interface Defect {
  line: number
  level: RiskLevel
  cat: string
  title: string
  desc: string
  fix: string
  code?: string
  source?: 'rule' | 'llm'
}

export interface Sample {
  code: string
  file: string
  label: string
  defects: Defect[]
}

export interface StartPayload {
  code: string
  lang: string
  risk: RiskFilter
  fileName?: string
}
