import type { Defect, RiskLevel } from '../types'
import { toast } from './toast'

const LV: Record<RiskLevel, string> = { high: '高危', mid: '中危', low: '低危' }

function download(name: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime + ';charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = name
  a.click()
  URL.revokeObjectURL(a.href)
}

export function exportReport(kind: 'markdown' | 'html', defects: Defect[]) {
  const counts = {
    high: defects.filter((d) => d.level === 'high').length,
    mid: defects.filter((d) => d.level === 'mid').length,
    low: defects.filter((d) => d.level === 'low').length,
  }
  const now = new Date().toLocaleString('zh-CN')

  if (kind === 'markdown') {
    let md = `# 智能代码审查报告\n\n> 生成时间：${now}  |  缺陷总数：${defects.length}（高危 ${counts.high} / 中危 ${counts.mid} / 低危 ${counts.low}）\n\n`
    defects.forEach((d) => {
      md += `## [${LV[d.level]}] ${d.title}\n- **位置**：第 ${d.line} 行\n- **类型**：${d.cat}\n- **描述**：${d.desc}\n- **修复建议**：${d.fix}\n\n`
    })
    download('code-review-report.md', md, 'text/markdown')
  } else {
    let html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>代码审查报告</title></head><body style="font-family:sans-serif;max-width:760px;margin:40px auto;color:#1a1d24"><h1>智能代码审查报告</h1><p>生成时间：${now} ｜ 缺陷总数：${defects.length}</p><hr>`
    defects.forEach((d) => {
      html += `<div style="border:1px solid #e7e9ee;border-radius:12px;padding:16px;margin:12px 0"><strong>[${LV[d.level]}] ${d.title}</strong> <em style="color:#666">第 ${d.line} 行 · ${d.cat}</em><p>${d.desc}</p><p><b>修复建议：</b>${d.fix}</p></div>`
    })
    html += '</body></html>'
    download('code-review-report.html', html, 'text/html')
  }
  toast('报告导出成功，已开始下载', 'success')
}
