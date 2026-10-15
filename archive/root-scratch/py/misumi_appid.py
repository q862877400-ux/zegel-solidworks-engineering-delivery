# -*- coding: utf-8 -*-
"""API000101 = applicationId 无效。找对了这个值就能用。"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import requests

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"})
r = s.get("https://www.misumi.com.cn/", timeout=20)
print("  官网 cookie:", list(s.cookies.keys()))

# 从页面 HTML 里挖 applicationId / appId 之类
body = r.text
print("  页面大小:", len(body))
pats = [r"applicationId[\"'\s:=]+([A-Za-z0-9_\-]{4,40})",
        r"appId[\"'\s:=]+([A-Za-z0-9_\-]{4,40})",
        r"application_id[\"'\s:=]+([A-Za-z0-9_\-]{4,40})"]
found = set()
for p in pats:
    found |= set(re.findall(p, body, re.I))
print("  HTML 里挖到的 id:", sorted(found)[:10] if found else "无")

# Nuxt 常见：window.__NUXT__ 或 __INITIAL_STATE__
for key in ("__NUXT__", "__INITIAL_STATE__", "applicationId", "appId"):
    idx = body.find(key)
    if idx > 0:
        print("  '%s' 出现在偏移 %d" % (key, idx))
        print("    片段:", re.sub(r"\s+", " ", body[idx:idx + 150])[:140])

# 从 JS chunk 里找
urls = re.findall(r'src="(/_nuxt/[^"]+\.js)"', body)
print("  JS chunk 数:", len(urls))
found2 = set()
for u in urls[:12]:
    try:
        j = s.get("https://www.misumi.com.cn" + u, timeout=15).text
        found2 |= set(re.findall(r"applicationId[\"'\s:=]+([A-Za-z0-9_\-]{4,40})", j, re.I))
        found2 |= set(re.findall(r"appId[\"'\s:=]+([A-Za-z0-9_\-]{6,40})", j, re.I))
    except Exception:
        pass
print("  JS 里挖到的 id:", sorted(found2)[:14] if found2 else "无")
