"""对比实验：Semgrep 单独 / LLM 单独 / 三引擎融合 的检出率、准确率、误报率"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.engine import semgrep, pipeline  # noqa: E402
from app.engine.llm_analyzer import analyze as llm_analyze  # noqa: E402

TOL = 2  # 行号匹配容差（±2 行）

# 测试样本：code 为代码，truth 为人工标注的真值缺陷 (行号, 标签)
SAMPLES = [
    {
        "name": "登录服务(JS)",
        "lang": "javascript",
        "code": """// user-service.js — 用户登录与查询模块
const db = require('./db');
const API_KEY = "sk-9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c";

async function login(req, res) {
  const { username, password } = req.body;
  const query = `SELECT * FROM users WHERE name = '${username}' AND pass = '${password}'`;
  const user = await db.query(query);
  if (user) {
    res.cookie('session', user.id, { httpOnly: false });
    res.send(eval("('" + username + "')"));
  }
  return res.json({ ok: true, data: user });
}

function renderProfile(html) {
  document.getElementById('profile').innerHTML = html;
}

function calcDiscount(price) {
  var total = price * 0.9;
  console.log("discount applied");
  return total;
}
""",
        "truth": [
            (3, "硬编码密钥"), (6, "输入未校验"), (7, "SQL注入"),
            (8, "缺少错误处理"), (10, "Cookie安全"), (11, "eval"),
            (13, "返回敏感数据"), (17, "XSS"), (21, "var声明"), (22, "调试日志"),
        ],
    },
    {
        "name": "订单退款(PY)",
        "lang": "python",
        "code": """import sqlite3
import os

DB_PATH = "orders.db"

def get_order(order_id):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM orders WHERE id = " + str(order_id)
    row = conn.execute(query).fetchone()
    if row:
        return {"ok": True, "data": row}
    return {"ok": False}

def refund(order_id, password):
    if password == "admin123":
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE orders SET status='refunded' WHERE id=" + str(order_id))
        conn.commit()
    else:
        print("wrong password", password)
        return {"ok": False}
    return {"ok": True}
""",
        "truth": [
            (7, "资源未释放"), (8, "SQL注入"), (9, "缺少错误处理"),
            (11, "返回敏感数据"), (15, "硬编码口令"), (17, "SQL注入"), (20, "调试输出"),
        ],
    },
    {
        "name": "文件上传(JS)",
        "lang": "javascript",
        "code": """// upload.js — 文件上传处理
const fs = require('fs');
const path = require('path');
const S3_SECRET = "aws-secret-key-1234567890abcdef";

function handleUpload(req, res) {
  const filename = req.body.filename;
  const target = '/uploads/' + filename;
  fs.writeFileSync(target, req.body.content);
  res.send('ok');
}

function getUser(uid) {
  const users = JSON.parse(fs.readFileSync('users.json'));
  return users[uid];
}

function delFile(name) {
  const dir = path.join(__dirname, 'files');
  fs.unlinkSync(dir + '/' + name);
}
""",
        "truth": [
            (3, "硬编码密钥"), (7, "路径穿越"), (8, "缺少错误处理"),
            (13, "缺少错误处理"), (16, "缺少错误处理"),
        ],
    },
    {
        "name": "令牌生成(PY)",
        "lang": "python",
        "code": """import random
import hashlib

SECRET = "my-secret-token-abcdef123456"

def make_token():
    return random.randint(100000, 999999)

def hash_password(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()

def verify(user, pwd):
    stored = get_stored(user)
    if stored == hash_password(pwd):
        return True
    return False

def get_stored(user):
    return "d41d8cd98f00b204e9800998ecf8427e"
""",
        "truth": [
            (4, "硬编码密钥"), (7, "弱随机数"), (10, "弱哈希算法"), (16, "缺少错误处理"),
        ],
    },
    {
        "name": "资料渲染(JS)",
        "lang": "javascript",
        "code": """// profile.js — 个人资料渲染
function renderProfile(user) {
  document.getElementById('name').innerHTML = user.name;
  document.getElementById('bio').innerHTML = user.bio;
}

function greet(name) {
  return eval("alert('Hello " + name + "')");
}

function setCookie(value) {
  document.cookie = "session=" + value;
}

function saveData(data) {
  localStorage.setItem('user', JSON.stringify(data));
  console.log('saved', data);
}
""",
        "truth": [
            (3, "XSS"), (4, "XSS"), (8, "eval"), (12, "会话安全"), (16, "敏感信息"), (17, "调试日志"),
        ],
    },
    {
        "name": "计算工具(PY)",
        "lang": "python",
        "code": """def divide(a, b):
    return a / b

def calc_discount(price, rate):
    total = price * (1 - rate)
    print("discount", total)
    return total

def load_config():
    f = open("config.json")
    data = f.read()
    return data
""",
        "truth": [
            (2, "除零未校验"), (5, "输入未校验"), (6, "调试输出"), (10, "资源未释放"),
        ],
    },
]


def evaluate(reported, truth, tol=TOL):
    """贪心行号匹配：报告缺陷与真值 ±tol 行内视为命中"""
    reported = sorted(reported, key=lambda d: d["line"])
    matched = set()
    tp = 0
    for gline, _ in truth:
        for i, r in enumerate(reported):
            if i not in matched and abs(r["line"] - gline) <= tol:
                matched.add(i)
                tp += 1
                break
    fp = len(reported) - tp
    fn = len(truth) - tp
    recall = tp / len(truth) if truth else 0.0
    precision = tp / len(reported) if reported else 0.0
    return tp, fp, fn, recall, precision


def run_mode(sample, mode):
    code, lang = sample["code"], sample["lang"]
    if mode == "semgrep":
        defects, _, _, _ = semgrep.run_review(code, lang)
    elif mode == "llm":
        defects, _ = llm_analyze(code, lang, [], [])
    else:  # fusion
        defects, _, _, _, _ = pipeline.run_review(code, lang)
    return defects


def main():
    modes = ["semgrep", "llm", "fusion"]
    names = {"semgrep": "Semgrep", "llm": "LLM", "fusion": "三引擎融合"}
    agg = {m: {"tp": 0, "fp": 0, "fn": 0, "truth": 0} for m in modes}

    print(f"{'样本':<14}{'模式':<10}{'真值':>4}{'报告':>4}{'命中':>4}{'漏报':>4}{'误报':>4}{'检出率':>8}{'准确率':>8}{'误报率':>8}")
    print("-" * 82)

    for s in SAMPLES:
        for m in modes:
            defects = run_mode(s, m)
            tp, fp, fn, recall, precision = evaluate(defects, s["truth"])
            agg[m]["tp"] += tp
            agg[m]["fp"] += fp
            agg[m]["fn"] += fn
            agg[m]["truth"] += len(s["truth"])
            fpr = 1 - precision
            print(f"{s['name']:<14}{names[m]:<10}{len(s['truth']):>4}{len(defects):>4}{tp:>4}{fn:>4}{fp:>4}"
                  f"{recall*100:>7.1f}%{precision*100:>7.1f}%{fpr*100:>7.1f}%")
        print()

    print("=" * 82)
    print("汇总（6 个样本，36 处标注缺陷）")
    for m in modes:
        a = agg[m]
        tp, fp, fn = a["tp"], a["fp"], a["fn"]
        recall = tp / a["truth"]
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        print(f"  {names[m]:<8} 命中 {tp:>2}  漏报 {fn:>2}  误报 {fp:>2}  "
              f"检出率 {recall*100:>5.1f}%  准确率 {precision*100:>5.1f}%  误报率 {(1-precision)*100:>5.1f}%")

    # 保存结果供论文引用
    result = {
        "tolerance": TOL,
        "samples": len(SAMPLES),
        "total_truth": sum(len(s["truth"]) for s in SAMPLES),
        "modes": {m: {"tp": agg[m]["tp"], "fp": agg[m]["fp"], "fn": agg[m]["fn"], "truth": agg[m]["truth"]} for m in modes},
    }
    Path("benchmark_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n结果已保存到 benchmark_results.json")


if __name__ == "__main__":
    main()
