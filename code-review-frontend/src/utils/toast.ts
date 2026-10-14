export function toast(msg: string, type: 'success' | 'warn' | 'info' = 'info') {
  const colors: Record<'success' | 'warn' | 'info', string> = {
    success: '#16a34a',
    warn: '#f59e0b',
    info: '#2f6bff',
  }
  const box = document.createElement('div')
  box.textContent = msg
  box.style.cssText =
    `position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:100;` +
    `background:#1a1d24;color:#fff;padding:11px 20px;border-radius:12px;font-size:13px;font-weight:500;` +
    `box-shadow:0 8px 30px rgba(0,0,0,.25);opacity:0;transition:opacity .3s, transform .3s;` +
    `border-left:4px solid ${colors[type]};`
  document.body.appendChild(box)
  requestAnimationFrame(() => {
    box.style.opacity = '1'
    box.style.transform = 'translateX(-50%) translateY(-4px)'
  })
  window.setTimeout(() => {
    box.style.opacity = '0'
    box.style.transform = 'translateX(-50%) translateY(0)'
    window.setTimeout(() => box.remove(), 300)
  }, 2200)
}
