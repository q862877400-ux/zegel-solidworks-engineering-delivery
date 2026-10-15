import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import requests

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"})
base = "https://www.misumi.com.cn"
r = s.get(base + "/", timeout=25)
urls = re.findall(r'src="(/_nuxt/[^"]+\.js)"', r.text)
# 关键：login.UyZE_TW1.js 与 dynamic-login 那两个
targets = [u for u in urls if re.search(r"login|auth|session", u, re.I)]
if not targets:
    targets = urls[:8]
print("  目标 chunk:", targets)
alljs = ""
for u in targets:
    try:
        alljs += s.get(base + u, timeout=25).text
    except Exception as e:
        print("   ERR", u, str(e)[:40])
print("  取到 JS %d 字节" % len(alljs))

print()
print("  ★ 所有 /api/** 路径（找登录）：")
paths = sorted(set(re.findall(r"['\"](/api/[a-zA-Z0-9_\-/]{3,60})['\"]", alljs)))
for p in paths:
    if re.search(r"login|auth|sign|token|session|password|regist", p, re.I):
        print("    ", p)
print("  （全部 %d 条，登录相关的在上面）" % len(paths))

print()
print("  ★ 登录请求体附近的代码：")
for kw in ("loginId", "passwordLogin", "signIn", "/auth/"):
    for m in re.finditer(re.escape(kw), alljs):
        seg = alljs[max(0, m.start() - 160):m.start() + 160]
        seg = re.sub(r"\s+", " ", seg)
        print("    [%s] %s" % (kw, seg[:230]))
        break
