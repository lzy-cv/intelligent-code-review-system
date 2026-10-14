import type { Defect, Sample } from '../types'
import jsCode from './samples/js.txt?raw'
import pyCode from './samples/python.txt?raw'

const JS_DEFECTS: Defect[] = [
  {
    line: 3, level: 'high', cat: '安全', title: '硬编码 API 密钥',
    desc: '检测到明文写入的密钥常量 API_KEY，属于敏感信息泄露。密钥一旦进入代码仓库即视为泄露，可被用于未授权调用下游服务。',
    fix: '将密钥迁移到环境变量或密钥管理服务（KMS/Vault），通过 process.env 读取，并立即轮换已泄露的密钥。',
    code: 'const API_KEY = process.env.API_KEY;',
  },
  {
    line: 7, level: 'high', cat: '安全', title: 'SQL 注入风险',
    desc: "SQL 语句通过字符串拼接用户输入构造，攻击者可注入恶意 SQL（如 ' OR '1'='1'--）绕过认证或拖库。",
    fix: '使用参数化查询 / 预编译语句，彻底杜绝字符串拼接。',
    code: "const query = 'SELECT * FROM users WHERE name = ? AND pass = ?';\nawait db.query(query, [username, password]);",
  },
  {
    line: 11, level: 'high', cat: '安全', title: 'eval() 危险函数调用',
    desc: 'eval 会执行由用户输入拼接出的字符串，等价于远程代码执行（RCE），是最危险的反模式之一。',
    fix: '删除 eval，改用 JSON.parse 或安全的序列化方式处理数据。',
    code: 'res.send(JSON.parse(JSON.stringify(username)));',
  },
  {
    line: 17, level: 'high', cat: '安全', title: 'XSS 跨站脚本攻击',
    desc: 'innerHTML 直接注入未转义的 html 参数，攻击者可通过构造恶意标签窃取 Cookie、执行任意脚本。',
    fix: '改用 textContent 赋值，或对内容做转义 / 白名单过滤后再渲染。',
    code: 'el.textContent = html;',
  },
  {
    line: 6, level: 'mid', cat: '健壮性', title: '用户输入未校验',
    desc: 'username / password 直接解构使用，未做类型、长度、非空校验，异常输入可能导致下游错误或逻辑绕过。',
    fix: '对入参做类型 / 长度 / 非空校验，必要时引入 schema 校验库（如 zod）。',
  },
  {
    line: 8, level: 'mid', cat: '健壮性', title: '数据库查询缺少错误处理',
    desc: 'await db.query 未做 try/catch，连接失败或查询异常会直接抛出，导致接口崩溃。',
    fix: '包裹 try/catch，统一错误响应并记录日志。',
    code: 'try {\n  const user = await db.query(query, params);\n} catch (err) {\n  console.error(err);\n}',
  },
  {
    line: 10, level: 'mid', cat: '安全', title: 'Cookie 安全属性缺失',
    desc: 'httpOnly 设为 false 使 JS 可读取会话 Cookie，一旦发生 XSS 即可被窃取会话。',
    fix: '开启 httpOnly 与 SameSite，生产环境同时开启 Secure。',
    code: "res.cookie('session', user.id, { httpOnly: true, sameSite: 'lax', secure: true });",
  },
  {
    line: 21, level: 'low', cat: '代码质量', title: '使用 var 声明变量',
    desc: 'var 存在变量提升与函数级作用域问题，易引发意外覆盖与闭包 bug。',
    fix: '改用 let / const 声明。',
    code: 'const total = price * 0.9;',
  },
  {
    line: 22, level: 'low', cat: '代码质量', title: '遗留调试日志',
    desc: 'console.log 调试信息遗留在生产代码中，可能泄露内部数据并影响性能。',
    fix: '移除或改用统一日志框架并控制日志级别。',
  },
]

const PY_DEFECTS: Defect[] = [
  {
    line: 5, level: 'high', cat: '安全', title: '硬编码 API 密钥',
    desc: '明文写入的密钥常量 API_KEY，属于敏感信息泄露，一旦进入代码仓库即视为泄露。',
    fix: '通过环境变量或密钥管理服务读取，并立即轮换已泄露密钥。',
    code: 'import os\nAPI_KEY = os.environ["API_KEY"]',
  },
  {
    line: 9, level: 'high', cat: '安全', title: 'SQL 注入风险',
    desc: "SQL 语句通过字符串拼接用户输入构造，攻击者可注入恶意 SQL（如 ' OR '1'='1'--）绕过认证或拖库。",
    fix: '使用参数化查询，禁止字符串拼接 SQL。',
    code: 'query = "SELECT * FROM users WHERE name = ? AND pass = ?"\ncur = conn.execute(query, (username, password))',
  },
  {
    line: 8, level: 'mid', cat: '健壮性', title: '数据库连接缺少上下文管理',
    desc: '直接 connect 未使用 with 也未 try/finally，异常时连接无法释放，易耗尽连接池。',
    fix: '使用 with 上下文管理器或 try/finally 确保连接关闭。',
    code: 'with sqlite3.connect("users.db") as conn:\n    cur = conn.execute(query)',
  },
  {
    line: 13, level: 'mid', cat: '安全', title: '会话令牌熵不足',
    desc: 'os.urandom(8).hex() 仅产生 64 位熵的令牌，且为弱随机，存在被预测 / 枚举的风险。',
    fix: '使用 secrets 模块生成更高熵的安全令牌。',
    code: 'import secrets\ntoken = secrets.token_hex(32)',
  },
  {
    line: 18, level: 'mid', cat: '安全', title: 'XSS 跨站脚本攻击',
    desc: 'html 参数未做转义直接拼接返回，攻击者可注入恶意标签窃取数据或执行脚本。',
    fix: '对输出进行 HTML 转义，或使用模板引擎的自动转义能力。',
    code: 'import html as h\ndef render(html):\n    return "<div>" + h.escape(html) + "</div>"',
  },
  {
    line: 14, level: 'low', cat: '安全', title: '敏感数据直接返回',
    desc: '将 user 完整记录返回给客户端，可能泄露密码哈希等敏感字段。',
    fix: '显式挑选需要返回的字段，过滤敏感信息。',
    code: 'return {"ok": True, "token": token, "data": {"id": user[0]}}',
  },
  {
    line: 21, level: 'low', cat: '代码质量', title: '变量命名不规范',
    desc: '变量命名过于简短（calc / total），缺少类型标注，可读性与可维护性差。',
    fix: '使用有意义的命名并补充类型标注。',
    code: 'def calc_discount(price: float) -> float:',
  },
  {
    line: 22, level: 'low', cat: '代码质量', title: '遗留调试输出',
    desc: 'print 调试信息遗留在生产代码中，可能泄露内部数据并影响性能。',
    fix: '移除或改用 logging 模块并控制日志级别。',
  },
]

const SAMPLES: Record<string, Sample> = {
  javascript: { code: jsCode.trim(), file: 'user-service.js', label: 'JavaScript', defects: JS_DEFECTS },
  typescript: { code: jsCode.trim(), file: 'user-service.ts', label: 'TypeScript', defects: JS_DEFECTS },
  python: { code: pyCode.trim(), file: 'app.py', label: 'Python', defects: PY_DEFECTS },
}

export function getSample(lang: string): Sample {
  return SAMPLES[lang] ?? SAMPLES.javascript
}
