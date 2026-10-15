import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import requests

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"})
r = s.get("https://www.misumi.com.cn/", timeout=25)
js = s.get("https://www.misumi.com.cn/_nuxt/entry.4KD1wBAi.js", timeout=25).text
cfg = r.text[r.text.find("__NUXT__.config"):]
cfg = cfg[:cfg.find("</script>")]

print("  ① 配置里的 API host：")
for m in re.finditer(r"(api[\w.]*)\s*:\s*\{([^}]{0,300})", cfg):
    for h in re.findall(r'host\s*:\s*"([^"]+)"', m.group(2)):
        print("    %-22s %s" % (m.group(1), h))
for h in re.findall(r'host\s*:\s*"([a-z0-9.\-]+)"', cfg):
    print("    host:", h)

print()
print("  ② 登录相关方法（baseURL 上下文）：")
for kw in ("/api/v1/auth/check", "async login", "login(", "signIn", "pwdLogin"):
    for m in re.finditer(re.escape(kw), js):
        seg = re.sub(r"\s+", " ", js[max(0, m.start() - 200):m.start() + 260])
        print("    [%s]" % kw)
        print("      ", seg[:300])
        break
