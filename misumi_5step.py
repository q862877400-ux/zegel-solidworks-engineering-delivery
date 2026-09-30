# -*- coding: utf-8 -*-
"""米思米五步最小验证：登录 -> 分类树 -> 丝杆系列 -> 下 1 个 CAD -> 校验。

⚠ 凭证只从 C:\\swprojects\\.misumi.env 读，不回显、不写日志。
⚠ 第 1 步（登录）过不去就**立刻停**，不硬试。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ENV = Path(r"C:\swprojects\.misumi.env")
d = {}
for line in ENV.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        d[k.strip()] = v.strip()

import requests

APP = "77f56fb2-4165-4116-b82f-e495838bb6e1"
HOST = "https://api.cn.misumi.com.cn"
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
    "applicationId": APP, "lang": "CHN",
    "Referer": "https://www.misumi.com.cn/", "Origin": "https://www.misumi.com.cn",
})
s.get("https://www.misumi.com.cn/", timeout=20)


def show(tag, r, n=140):
    txt = (r.text or "").replace("\n", " ")
    print("  %-22s %-30s -> %3d  %s" % (tag, str(n)[:30], r.status_code, txt[:120]))


print("  ① 登录（参数名按 API000100 提示逐个试）")
LOGGED = False
for body in ({"loginId": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"]},
             {"loginId": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"],
              "applicationId": APP},
             {"account": d["MISUMI_EMAIL"], "password": d["MISUMI_PASSWORD"]}):
    try:
        r = s.post(HOST + "/api/v1/auth/login", json=body, timeout=20)
        show("login", r)
        if r.status_code == 200:
            LOGGED = True
            break
    except Exception as e:
        print("    ERR", str(e)[:50])
if not LOGGED:
    print("  ✗ 登录未过 —— 按纪律**停止**，不硬试其余步骤")
    raise SystemExit(1)

print()
print("  ② 分类树")
r = s.get(HOST + "/api/v1/category/search", params={"applicationId": APP}, timeout=20)
show("category", r)
try:
    cats = r.json().get("categoryList", [])
    print("     %d 个大类: %s" % (len(cats),
          ", ".join(c.get("categoryName", "?") for c in cats[:14])))
except Exception:
    pass

print()
print("  ③ 丝杠 → 系列（用 series/search，它要 keyword 参数）")
r = s.get(HOST + "/api/v1/series/search",
          params={"keyword": "丝杠", "applicationId": APP}, timeout=20)
show("series", r)

print()
print("  ④ 型号直查 type/search（要 partNumber）")
for pn in ("SFU1605", "HGR20", "HFS5-4040"):
    r = s.get(HOST + "/api/v1/type/search",
              params={"partNumber": pn, "applicationId": APP}, timeout=20)
    show("type " + pn, r, 90)

print()
print("  ⑤ CAD 下载（看是否需要登录 / 要什么参数）")
for path, p in (("/api/v1/cad/download", {"partNumber": "HGR20"}),
                ("/api/v1/cad/termsOfUse", {}),
                ("/api/v1/cad/preview", {"partNumber": "HGR20"})):
    r = s.get(HOST + path, params=dict(p, applicationId=APP), timeout=25)
    ct = r.headers.get("content-type", "")
    show(path, r, 90)
    if "zip" in ct or "octet" in ct:
        print("     ★ 返回二进制 %d 字节, %s" % (len(r.content), ct))
