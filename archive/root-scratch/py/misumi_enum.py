# -*- coding: utf-8 -*-
"""米思米全库可枚举性探测：分类树 + 型号检索，看能不能爬出全量清单。"""
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


def call(path, **params):
    try:
        r = s.get(HOST + path, params=dict(params, applicationId=APP), timeout=20)
        return r.status_code, (r.text or "")[:300].replace("\n", " ")
    except Exception as e:
        return 0, "ERR " + str(e)[:60]


print("  === ① 分类树（能枚举的前提）===")
for path, p in (("/api/v1/category/search", {}),
                ("/api/v1/category/search", {"parentId": "0"}),
                ("/api/v1/series/search", {}),
                ("/api/v1/brand/search", {}),
                ("/api/v1/type/search", {})):
    code, txt = call(path, **p)
    print("  %-28s %-14s -> %3d %s" % (path, str(p)[:14], code, txt[:110]))

print()
print("  === ② 型号检索（每类能列出多少）===")
for kw in ("丝杠", "直线导轨", "铝型材", "轴承"):
    code, txt = call("/api/v1/keyword/search", keyword=kw)
    print("  %-8s -> %3d %s" % (kw, code, txt[:100]))

print()
print("  === ③ 型号直查（有没有 partNumber 搜索）===")
for path, p in (("/api/v1/partNumber/search", {"keyword": "HGR20"}),
                ("/api/v1/partNumber/search", {"searchType": "1", "keyword": "HGR20"}),
                ("/api/v1/partNumberPreview/search", {"keyword": "HGR20"}),
                ("/api/v1/similar/specInfo", {"partNumber": "HGR20"})):
    code, txt = call(path, **p)
    print("  %-38s -> %3d %s" % (path, str(p)[:22], code, txt[:80]))

print()
print("  === ④ CAD 下载（要登录，看是否 401）===")
for path, p in (("/api/v1/cad/download", {"partNumber": "HGR20"}),
                ("/api/v1/cad/termsOfUse", {})):
    code, txt = call(path, **p)
    print("  %-28s -> %3d %s" % (path, str(p)[:18], code, txt[:90]))
