# -*- coding: utf-8 -*-
"""未登录状态下，米思米 API 能拿到多少？（决定「查询」这条路是否完全走得通）"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
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


def g(path, **p):
    try:
        r = s.get(HOST + path, params=dict(p, applicationId=APP), timeout=20)
        return r
    except Exception as e:
        print("   ERR", str(e)[:50]); return None


print("  ① 13 个大类全列：")
r = g("/api/v1/category/search")
cats = r.json().get("categoryList", []) if r else []
for c in cats:
    print("     %-10s %s" % (c.get("categoryCode"), c.get("categoryName")))
print()
for c in cats[:3]:
    cc = c.get("categoryCode")
    r2 = g("/api/v1/category/search", parentId=cc, categoryCode=cc)
    if r2 is None:
        continue
    try:
        sub = r2.json().get("categoryList", [])
        print("  ② %s 下 %d 个子类" % (c.get("categoryName"), len(sub)))
        for x in sub[:8]:
            print("       %-10s %s" % (x.get("categoryCode"), x.get("categoryName")))
    except Exception as e:
        print("  ②", cc, "解析失败", str(e)[:40])
    print()

print("  ③ 未登录按型号查（type/search 要 partNumber）：")
for pn in ("SFU1605", "HGR20", "HFS5-4040"):
    r = g("/api/v1/type/search", partNumber=pn)
    if r is None:
        continue
    t = (r.text or "").replace("\n", " ")
    print("   %-10s -> %3d  %s" % (pn, r.status_code, t[:120]))
