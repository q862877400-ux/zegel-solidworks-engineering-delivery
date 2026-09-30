# -*- coding: utf-8 -*-
"""摸清 api.cn.misumi.com.cn 的真实路径与认证方式。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ENV = Path(r"C:\swprojects\.misumi.env")
d = {}
for line in ENV.read_text(encoding="utf-8").splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        d[k.strip()] = v.strip()
import requests

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"})
s.get("https://www.misumi.com.cn/", timeout=20)

HOST = "https://api.cn.misumi.com.cn"
print("  === 400 说明端点存在，测它要什么 ===")
tests = [
    ("GET", "/api/v1/keyword/search", None),
    ("GET", "/api/v1/keyword/search?keyword=%E8%9B%8B", None),   # 螺
    ("GET", "/api/v1/category/search", None),
    ("GET", "/keyword/search", None),
    ("GET", "/api/keyword/search", None),
    ("GET", "/", None),
    ("POST", "/api/v1/keyword/search", {}),
    ("POST", "/api/v1/login", {"email": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"]}),
    ("POST", "/api/v1/auth/login", {"email": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"]}),
]
for meth, path, body in tests:
    try:
        if meth == "GET":
            r = s.get(HOST + path, timeout=15)
        else:
            r = s.post(HOST + path, json=body, timeout=15)
        msg = ""
        try:
            j = r.json()
            msg = str(j)[:70]
        except Exception:
            msg = (r.text or "")[:70].replace("\n", " ")
        print("  %-4s %-34s -> %3d  %s" % (meth, path, r.status_code, msg))
    except Exception as e:
        print("  %-4s %-34s ERR %s" % (meth, path, str(e)[:40]))
