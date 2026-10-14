# app.py — 用户登录与订单查询接口
import os
import sqlite3

API_KEY = "sk-8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c"

def login(username, password):
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE name = '" + username + "' AND pass = '" + password + "'"
    cur = conn.execute(query)
    user = cur.fetchone()
    if user:
        token = os.urandom(8).hex()
        return {"ok": True, "token": token, "data": user}
    return {"ok": False}

def render(html):
    return "<div>" + html + "</div>"

def calc(price):
    total = price * 0.9
    print("discount", total)
    return total
