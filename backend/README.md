# 智能代码审查平台 · 后端

FastAPI + Semgrep 规则引擎的最小闭环。核心接口 `POST /api/review` 接收代码，调用本地 Semgrep 做规则扫描，返回结构化的缺陷列表（行号 / 风险等级 / 类型 / 描述 / 修复建议）。

## 依赖安装

```bash
pip install -r requirements.txt
```

## 启动

```bash
# 方式一
python run.py

# 方式二
python -m uvicorn app.main:app --reload --port 8000
```

- 接口文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

## 冒烟测试（不启动服务，直接跑引擎）

```bash
python test_review.py
```

## 接口说明

`POST /api/review`

```json
{
  "code": "const query = `SELECT * FROM t WHERE id='${id}'`;",
  "language": "javascript",
  "ruleset": "local"
}
```

`ruleset` 取值：
- `local`（默认）：本地规则 `rules/demo.yaml`，离线、秒出、确定性
- `default` / `owasp` / `security-audit` / `auto`：Semgrep 官方规则集（需联网首次下载）

响应：

```json
{
  "defects": [
    { "line": 7, "level": "high", "cat": "安全", "title": "SQL 注入风险", "desc": "...", "fix": "...", "rule_id": "sql-injection-js", "cwe": "CWE-89" }
  ],
  "summary": { "total": 1, "high": 1, "mid": 0, "low": 0 },
  "duration_ms": 1234,
  "rule_findings": 1
}
```

## 启用 LLM 深度分析（可选）

1. 复制 `.env.example` 为 `.env`，填入 DeepSeek API Key：
   ```
   DEEPSEEK_API_KEY=sk-xxxx
   ```
2. 重启后端。未配置 key 时自动跳过 LLM，仅用规则引擎 + RAG（不影响使用）。

RAG 内置 CWE 案例库（`app/engine/rag.py`），用 TF-IDF 余弦相似度检索相似缺陷案例，为规则缺陷附上参考修复代码，并作为上下文注入 LLM。

## 目录结构

```
backend/
├─ app/
│  ├─ main.py          # FastAPI 入口 + CORS + 路由
│  ├─ schemas.py       # Pydantic 请求/响应模型
│  └─ engine/
│     └─ semgrep.py    # Semgrep 子进程封装 + JSON 解析 + 中文映射
├─ rules/
│  └─ demo.yaml        # 本地演示规则集（可自行扩展）
├─ smoke/              # 冒烟测试样例
├─ test_review.py      # 引擎冒烟测试
└─ run.py              # 启动脚本
```
