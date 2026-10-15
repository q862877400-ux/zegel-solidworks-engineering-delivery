# -*- coding: utf-8 -*-
"""抓官网自己的登录调用：它用什么端点、什么参数名、什么编码。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import requests

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"})
r = s.get("https://www.misumi.com.cn/", timeout=25)
print("  页面:", r.status_code, len(r.text), "bytes")
body = r.text

print()
print("  ① 页面里出现的 login / auth 相关路径：")
paths = set()
for m in re.findall(r"['\"](/[a-zA-Z0-9_\-/.]{3,60}(?:login|auth|signin|session|token)[a-zA-Z0-9_\-/.]*)['\"]", body, re.I):
    paths.add(m)
for m in re.findall(r"['\"](https://[a-z0-9.\-]+/[a-zA-Z0-9_\-/]{3,60})['\"]", body):
    if re.search(r"login|auth|passport|account", m, re.I):
        paths.add(m)
for p in sorted(paths)[:20]:
    print("    ", p)

print()
print("  ② JS chunk 里的登录端点：")
urls = re.findall(r'src="(/_nuxt/[^"]+\.js)"', body)
print("    chunk 数:", len(urls))
found = set()
for u in urls:
    try:
        j = s.get("https://www.misumi.com.cn" + u, timeout=20).text
    except Exception:
        continue
    for m in re.findall(r"['\"](/api/[a-zA-Z0-9_\-/]{3,50})['\"]", j):
        if re.search(r"login|auth|sign|token|member|user", m, re.I):
            found.add(m)
for f in sorted(found)[:20]:
    print("    ", f)

print()
print("  ③ 登录相关参数名（password/loginId/mobile/phone/captcha）：")
alljs = ""
for u in urls[:6]:
    try:
        alljs += s.get("https://www.misumi.com.cn" + u, timeout=20).text
    except Exception:
        pass
for kw in ("loginId", "password", "mobile", "phone", "captcha", "smsCode", "pwd"):
    n = alljs.count(kw)
    if n:
        print("    %-12s 出现 %d 次" % (kw, n))
