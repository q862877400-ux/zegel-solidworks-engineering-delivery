# -*- coding: utf-8 -*-
"""用本地凭证文件试登录米思米，并探测 API 主机。

⚠ 凭证只从 C:\\swprojects\\.misumi.env 读，**不回显、不写日志、不进 git**。
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ENV = Path(r"C:\swprojects\.misumi.env")


def creds():
    if not ENV.is_file():
        print("  找不到凭证文件:", ENV)
        return None, None
    d = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    return d.get("MISUMI_EMAIL"), d.get("MISUMI_PASSWORD")


def main() -> int:
    email, pw = creds()
    if not email or not pw:
        return 2
    print("  凭证已读（不回显）:", email[:3] + "***@" + email.split("@")[-1])
    try:
        import requests
    except ImportError:
        print("  没装 requests")
        return 3

    s = requests.Session()
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/131.0 Safari/537.36"),
    })
    # ① 先访问官网拿初始 cookie
    for url in ("https://www.misumi.com.cn/", "https://cn.misumi-ec.com/"):
        try:
            r = s.get(url, timeout=20)
            print("  GET %-34s -> %d  cookie %d 项" % (url, r.status_code, len(s.cookies)))
        except Exception as e:
            print("  GET %-34s ERR %s" % (url, str(e)[:44]))

    # ② 找登录端点（调研提到的 /api/v1/… 与 passport）
    cands = [
        "https://www.misumi.com.cn/api/v1/keyword/search",
        "https://api.cn.misumi.com.cn/api/v1/keyword/search",
        "https://www.misumi.com.cn/api/v1/category/search",
    ]
    for u in cands:
        try:
            r = s.get(u, timeout=15)
            print("  GET %-58s -> %d" % (u[8:66], r.status_code))
        except Exception as e:
            print("  GET %-58s ERR %s" % (u[8:66], str(e)[:40]))

    # ③ 看 cn 站是不是 WAF 挑战页
    try:
        r = s.get("https://cn.misumi-ec.com/", timeout=20)
        body = r.text
        waf = any(k in body for k in ("acw_sc__v2", "arg1=", "aliyun_waf"))
        print()
        print("  cn 站 WAF 挑战:", "★ 是（%d 字节挑战页）" % len(body) if waf else "否")
    except Exception as e:
        print("  cn 站 ERR", str(e)[:44])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
