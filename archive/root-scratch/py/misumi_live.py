# -*- coding: utf-8 -*-
"""带上 applicationId + 登录态，打米思米真实 API。"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
d = {}
for line in Path(r"C:\swprojects\.misumi.env").read_text(encoding="utf-8").splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        d[k.strip()] = v.strip()
import requests

APP = "77f56fb2-4165-4116-b82f-e495838bb6e1"
HOST = "https://api.cn.misumi.com.cn"
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
    "applicationId": APP,
    "lang": "CHN",
    "Referer": "https://www.misumi.com.cn/",
    "Origin": "https://www.misumi.com.cn",
})
s.get("https://www.misumi.com.cn/", timeout=20)

print("  ① 未登录直接查：")
for kw in ("丝杠", "直线导轨", "铝型材"):
    try:
        r = s.get(HOST + "/api/v1/keyword/search",
                  params={"keyword": kw, "applicationId": APP}, timeout=20)
        txt = (r.text or "")[:120].replace("\n", " ")
        print("     %-8s -> %d  %s" % (kw, r.status_code, txt))
    except Exception as e:
        print("     %-8s ERR %s" % (kw, str(e)[:40]))

print()
print("  ② 试登录端点（常见的几个）：")
for path, body in (
    ("/api/v1/login", {"email": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"]}),
    ("/api/v1/member/login", {"email": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"]}),
    ("/api/v1/auth/login", {"email": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"]}),
    ("/api/v1/user/login", {"email": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"]}),
):
    try:
        r = s.post(HOST + path, json=body, timeout=20)
        txt = (r.text or "")[:110].replace("\n", " ")
        print("     %-24s -> %d  %s" % (path, r.status_code, txt))
    except Exception as e:
        print("     %-24s ERR %s" % (path, str(e)[:36]))
