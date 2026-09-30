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
EMAIL, PW = d["MISUMI_EMAIL"], d["MISUMI_PASSWORD"]

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
    "applicationId": APP, "lang": "CHN",
    "Referer": "https://www.misumi.com.cn/", "Origin": "https://www.misumi.com.cn",
})
s.get("https://www.misumi.com.cn/", timeout=20)

print("  用官网自己出现的端点试：")
for path in ("/api/v1/auth/check", "/api/user/v1/auth/login",
             "/api/v1/auth/login", "/api/user/v1/auth/signIn",
             "/api/v1/user/login"):
    for body in ({"loginId": EMAIL, "password": PW},
                 {"account": EMAIL, "password": PW}):
        try:
            r = s.post(HOST + path, json=body, timeout=20)
            t = (r.text or "").replace("\n", " ")
            import json as J
            try:
                j = r.json()
                msg = (j.get("errorList") or [{}])[0].get("errorMessage", "")[:60]
                ok = "token" in J.dumps(j).lower() or "success" in J.dumps(j).lower()
            except Exception:
                msg, ok = t[:60], False
            print("  %-28s %-8s -> %3d  %s" % (path, list(body)[0], r.status_code,
                                                "★ " + msg if ok else msg))
            if ok:
                print("     完整响应:", t[:220])
                raise SystemExit(0)
        except SystemExit:
            raise
        except Exception as e:
            print("  %-28s ERR %s" % (path, str(e)[:40]))
