# 智能代码审查系统 Intelligent Code Review System

基于「LLM 大模型 + Semgrep 规则引擎 + RAG 检索」三引擎融合的智能代码审查平台，实现代码缺陷的自动检测、风险分级与修复建议生成，支持多用户与审查历史持久化。

## 系统架构

审查流水线（`backend/app/engine/`）：

1. **Semgrep 规则引擎**：确定性漏洞扫描（SQL 注入 / XSS / 硬编码密钥 / eval 等）
2. **RAG 检索增强**：内置 13 类 CWE 缺陷案例库，TF-IDF + 余弦相似度检索，为缺陷附上参考修复代码
3. **LLM 深度分析**：DeepSeek（OpenAI 兼容）做语义级分析，找出规则无法覆盖的逻辑缺陷
4. **融合去重**：规则 + LLM 结果合并，每条缺陷标注来源（规则 / LLM）

## 目录结构

```
.
├── backend/               # FastAPI 后端（Semgrep + LLM + RAG + SQLite + JWT）
├── code-review-frontend/  # Vue3 + TypeScript 前端
└── code-review.html       # 最初的前端静态原型（单文件，双击可打开）
```

## 快速开始

### 后端（需 Python 3.10+，已装 Semgrep）

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # 可选：填入 DeepSeek API Key 启用 LLM
python run.py               # 启动 http://127.0.0.1:8000
```

### 前端（需 Node 18+）

```bash
cd code-review-frontend
npm install
npm run dev                 # 启动 http://localhost:5173
```

浏览器打开 http://localhost:5173，登录演示账号 **demo / demo123**（首次启动自动预置）。

## 对比实验

`backend/benchmark.py` 对比三种模式（Semgrep 单独 / LLM 单独 / 三引擎融合）的检出率、准确率、误报率。

> 在 6 个样本、36 处标注缺陷上：**融合方案检出率 100%（0 漏报）**，由纯规则引擎的 41.7% 提升而来。

## 技术栈

Vue3 · TypeScript · Tailwind CSS · Chart.js · Pinia · Vue Router · FastAPI · SQLAlchemy · SQLite · Semgrep · DeepSeek · RAG · JWT
