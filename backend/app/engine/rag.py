"""RAG：CWE 缺陷案例库 + TF-IDF 向量检索（纯 Python 离线，可替换为 ChromaDB/Milvus + embedding）"""
import math
import re
from collections import Counter

# 缺陷案例库（可扩展）
CORPUS = [
    {
        "cwe": "CWE-89", "title": "SQL 注入", "category": "安全",
        "desc": "SQL 语句通过字符串拼接或模板字符串构造，攻击者可注入恶意 SQL 绕过认证、窃取数据或拖库。",
        "fix": 'query = "SELECT * FROM users WHERE name = ?"\ncur.execute(query, (name,))',
    },
    {
        "cwe": "CWE-79", "title": "XSS 跨站脚本", "category": "安全",
        "desc": "未转义的用户输入被写入 HTML（如 innerHTML、模板渲染），攻击者可注入脚本窃取 Cookie 或执行任意操作。",
        "fix": 'el.textContent = html  # 或使用模板引擎的自动转义',
    },
    {
        "cwe": "CWE-798", "title": "硬编码密钥", "category": "安全",
        "desc": "API 密钥、口令、令牌等敏感信息被硬编码在源码中，代码一旦泄露即造成凭据泄露。",
        "fix": 'API_KEY = os.environ["API_KEY"]',
    },
    {
        "cwe": "CWE-95", "title": "eval 代码注入", "category": "安全",
        "desc": "eval/exec 执行由用户输入拼接的字符串，等价于远程代码执行（RCE）。",
        "fix": 'data = json.loads(user_input)  # 用安全解析替代 eval',
    },
    {
        "cwe": "CWE-1004", "title": "Cookie 安全属性缺失", "category": "安全",
        "desc": "会话 Cookie 未开启 httpOnly / SameSite / Secure，易被 XSS 窃取或跨站请求伪造。",
        "fix": "res.cookie('session', sid, { httpOnly: True, sameSite: 'Lax', secure: True })",
    },
    {
        "cwe": "CWE-330", "title": "弱随机数与令牌熵不足", "category": "安全",
        "desc": "使用可预测的随机数或熵不足的令牌，导致会话令牌、验证码等可被预测或枚举。",
        "fix": "import secrets\ntoken = secrets.token_hex(32)",
    },
    {
        "cwe": "CWE-200", "title": "敏感信息泄露", "category": "安全",
        "desc": "将密码哈希、内部字段、调试信息等敏感数据返回给客户端或写入日志。",
        "fix": 'return {"id": user.id, "name": user.name}  # 只返回必要字段',
    },
    {
        "cwe": "CWE-20", "title": "输入未校验", "category": "健壮性",
        "desc": "用户输入未做类型、长度、非空或白名单校验，异常输入可能导致崩溃或逻辑绕过。",
        "fix": "if not isinstance(uid, int) or uid <= 0:\n    raise ValueError('invalid uid')",
    },
    {
        "cwe": "CWE-754", "title": "缺少错误处理", "category": "健壮性",
        "desc": "数据库、网络、文件等可能失败的调用未做 try/except 或错误检查，异常会直接导致程序崩溃。",
        "fix": "try:\n    user = db.query(...)\nexcept Exception as e:\n    log.error(e)\n    return error_response()",
    },
    {
        "cwe": "CWE-772", "title": "资源未释放", "category": "健壮性",
        "desc": "文件句柄、数据库连接、锁等资源在使用后未关闭，长时间运行会耗尽资源。",
        "fix": "with open(path) as f:\n    ...  # 上下文管理器自动关闭",
    },
    {
        "cwe": "CWE-362", "title": "竞态条件", "category": "正确性",
        "desc": "多个线程/请求并发读写同一资源而未加锁，导致数据不一致或重复操作。",
        "fix": "with lock:\n    ...  # 对临界区加锁",
    },
    {
        "cwe": "CWE-117", "title": "遗留调试输出", "category": "代码质量",
        "desc": "console.log / print 等调试输出遗留在生产代码中，可能泄露内部数据并影响性能。",
        "fix": "logging.getLogger(__name__).info(...)  # 用日志框架并控制级别",
    },
    {
        "cwe": "CWE-710", "title": "变量声明风格", "category": "代码质量",
        "desc": "使用 var、命名不规范等代码风格问题，存在作用域隐患，影响可读性与可维护性。",
        "fix": "const total = price * 0.9  # 用 let/const 替代 var",
    },
]


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-z0-9_]+", text)
    for seg in re.findall(r"[\u4e00-\u9fff]+", text):
        tokens.append(seg)
        for i in range(len(seg) - 1):
            tokens.append(seg[i:i + 2])
    return tokens


class RagEngine:
    def __init__(self, corpus=CORPUS):
        self.corpus = corpus
        self.docs = [" ".join(_tokenize(c["title"] + " " + c["desc"] + " " + c["category"])) for c in corpus]
        self._idf = self._build_idf()
        self._vecs = [self._tfidf(d) for d in self.docs]

    def _build_idf(self):
        n = len(self.docs)
        df = Counter()
        for d in self.docs:
            for t in set(d.split()):
                df[t] += 1
        return {t: math.log((1 + n) / (1 + df[t])) + 1 for t in df}

    def _tfidf(self, text: str) -> dict:
        tf = Counter(_tokenize(text))
        vec = {}
        for t, c in tf.items():
            if t in self._idf:
                vec[t] = (1 + math.log(c)) * self._idf[t]
        return vec

    @staticmethod
    def _cos(a: dict, b: dict) -> float:
        if not a or not b:
            return 0.0
        dot = sum(a[t] * b.get(t, 0.0) for t in a)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def search(self, query: str, k: int = 3) -> list[dict]:
        qv = self._tfidf(query)
        scored = sorted(
            ((self._cos(qv, v), i) for i, v in enumerate(self._vecs)),
            key=lambda x: -x[0],
        )
        return [self.corpus[i] for s, i in scored[:k] if s > 0]


_engine = RagEngine()


def enhance(defects: list[dict], k: int = 1) -> list[dict]:
    """为规则缺陷附上相似案例的 CWE 编号与参考修复代码"""
    for d in defects:
        cases = _engine.search(f"{d['title']} {d['desc']} {d['cat']}", k)
        if cases:
            c = cases[0]
            if not d.get("cwe"):
                d["cwe"] = c["cwe"]
            if not d.get("code"):
                d["code"] = c["fix"]
    return defects


def cases_for_llm(defects: list[dict], k: int = 3) -> list[dict]:
    """聚合所有缺陷命中的相似案例，去重后供 LLM 参考"""
    seen, out = set(), []
    for d in defects:
        for c in _engine.search(f"{d['title']} {d['desc']}", k):
            if c["cwe"] not in seen:
                seen.add(c["cwe"])
                out.append(c)
    return out[:k]
