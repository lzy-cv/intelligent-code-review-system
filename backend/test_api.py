"""后端接口冒烟测试：注册/登录/审查/历史/日志（多用户 + 数据库）"""
import json
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"


def call(method, path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


# 1. 未登录访问历史 → 应 401
s, _ = call("GET", "/api/reviews")
print(f"1. 未登录访问 /api/reviews -> {s} (期望 401)")
assert s == 401

# 2. 登录预置演示账号 demo/demo123
s, r = call("POST", "/api/auth/login", {"username": "demo", "password": "demo123"})
print(f"2. 登录 demo -> {s}")
assert s == 200

# 3. 注册新用户（唯一用户名，可重复运行）
uname = f"alice{int(time.time())}"
s, r = call("POST", "/api/auth/register", {"username": uname, "password": "alice123"})
print(f"3. 注册 {uname} -> {s}")
assert s == 200
tok = r["token"]

# 4. 新用户提交审查
code = open("smoke/test.js", encoding="utf-8").read()
s, r = call("POST", "/api/review", {"code": code, "language": "javascript", "ruleset": "local", "file_name": "test.js"}, token=tok)
print(f"4. 审查 -> {s} | summary={r.get('summary')} | review_id={r.get('review_id')}")
assert s == 200 and r["summary"]["total"] == 7
rid = r["review_id"]

# 5. 新用户的历史（应只含自己那条）
s, r = call("GET", "/api/reviews", token=tok)
print(f"5. 历史条数 -> {len(r)} | 第一条: {r[0]['file_name']} ({r[0]['total']}处)")
assert s == 200 and len(r) == 1

# 6. 详情
s, r = call("GET", f"/api/reviews/{rid}", token=tok)
print(f"6. 详情 -> {s} | 缺陷数={len(r['defects'])}")
assert s == 200 and len(r["defects"]) == 7

# 7. 操作日志
s, r = call("GET", "/api/logs", token=tok)
print(f"7. 日志 -> {s} | 最近: [{r[0]['action']}] {r[0]['detail']}")
assert s == 200 and len(r) >= 2

# 8. 越权访问：demo 试图看 alice 的审查记录
s2, _ = call("POST", "/api/auth/login", {"username": "demo", "password": "demo123"})
demo_tok = s2 and _  # 仅演示，重新登录取 token
s2, r2 = call("POST", "/api/auth/login", {"username": "demo", "password": "demo123"})
demo_tok = r2["token"]
s, _ = call("GET", f"/api/reviews/{rid}", token=demo_tok)
print(f"8. demo 越权访问 alice 记录 -> {s} (期望 404)")
assert s == 404

print("\n✅ 后端认证 + 数据库 + 多用户隔离 + 日志 全部通过")
