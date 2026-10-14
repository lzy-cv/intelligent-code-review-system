// 手写轻量语法高亮 + HTML 转义（仅用于演示，生产可用 highlight.js / Shiki）
export function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

const KEYWORDS =
  'const|let|var|function|return|if|else|for|while|async|await|new|class|import|from|export|default|' +
  'try|catch|throw|typeof|instanceof|this|switch|case|break|continue|delete|void|yield|extends|super|' +
  'null|undefined|true|false|in|of|def|print|not|and|or|elif'

const BUILTINS =
  'console|document|window|Math|JSON|Object|Array|String|Number|Promise|require|res|req|db|eval|' +
  'Buffer|process|sqlite3|os'

const TOKEN_CLASS = ['tok-comment', 'tok-string', 'tok-keyword', 'tok-number', 'tok-builtin', 'tok-func']

export function highlightLine(line: string): string {
  const esc = escapeHtml(line)
  const re = new RegExp(
    '(\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/|#[^\\n]*)' +
      '|(`(?:[^`\\\\]|\\\\.)*`|"(?:[^"\\\\]|\\\\.)*"|\'(?:[^\'\\\\]|\\\\.)*\')' +
      '|\\b(' + KEYWORDS + ')\\b' +
      '|\\b(\\d+(?:\\.\\d+)?)\\b' +
      '|\\b(' + BUILTINS + ')\\b' +
      '|\\b([a-zA-Z_$][\\w$]*)(?=\\s*\\()',
    'g',
  )

  return esc.replace(re, (m, c1, c2, c3, c4, c5, c6) => {
    const groups = [c1, c2, c3, c4, c5, c6]
    const i = groups.findIndex((x) => x !== undefined)
    return i >= 0 ? `<span class="${TOKEN_CLASS[i]}">${m}</span>` : m
  })
}
