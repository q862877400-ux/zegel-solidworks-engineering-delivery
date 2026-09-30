# -*- coding: utf-8 -*-
"""免登录能拿到多少米思米数据？——决定这条路的天花板。"""
import json
import sys

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


def g(tag, path, **p):
    try:
        r = s.get(HOST + path, params=dict(p, applicationId=APP, lang="CHN"), timeout=20)
        j = None
        try:
            j = r.json()
        except Exception:
            pass
        head = ""
        if isinstance(j, dict):
            head = "totalCount=%s keys=%s" % (
                j.get("totalCount"), list(j)[:6])
        print("  %-22s -> %3d  %s" % (tag, r.status_code, head or
                                        (r.text or "")[:90]))
        return j
    except Exception as e:
        print("  %-22s ERR %s" % (tag, str(e)[:50]))
        return None


print("  ① partNumber/suggest（免登录拿规范化型号）")
j = g("suggest SUS304", "/api/v1/partNumber/suggest",
      keyword="SUS304", count=3, field="@default,partNumberList.innerCode")
if j:
    print("     样例:", json.dumps(j, ensure_ascii=False)[:200])

print()
print("  ② ★ partNumber/search —— 能否免登录拿**规格明细**")
j = g("partNumber HGR20", "/api/v1/partNumber/search", partNumber="HGR20")
if isinstance(j, dict):
    print("     全部键:", list(j)[:14])

print()
print("  ③ fullText/searchInCADComponents（英文词可能有效）")
for kw in ("bearing", "linear", "guide", "SFU1605", "HGR20"):
    g("searchInCAD " + kw, "/api/v1/fullText/searchInCADComponents", keyword=kw)

print()
print("  ④ CAD 相关端点（看是否 401 = 需登录）")
for path, p in (("/api/v1/cad/termsOfUse", {}),
                ("/api/v1/cad/preview", {"partNumber": "HGR20"}),
                ("/api/v1/cad/download", {"partNumber": "HGR20"})):
    try:
        r = s.get(HOST + path, params=dict(p, applicationId=APP, lang="CHN"), timeout=20)
        msg = ""
        try:
            msg = (r.json().get("errorList") or [{}])[0].get("errorMessage", "")
        except Exception:
            msg = (r.text or "")[:60]
        print("  %-24s -> %3d  %s" % (path, r.status_code, msg))
    except Exception as e:
        print("  %-24s ERR %s" % (path, str(e)[:40]))

print()
print("  ⑤ 别的 CAD 主机（调研给的官方服务域名）")
for u in ("https://rd-cn-cadapi.misumi.com.cn",
          "https://rd-cn-caddata.misumi.com.cn"):
    try:
        r = s.get(u, timeout=12)
        print("  %-44s -> %3d" % (u, r.status_code))
    except Exception as e:
        print("  %-44s ERR %s" % (u, str(e)[:40]))
