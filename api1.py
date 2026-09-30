import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
for dll in ("fa-open-biz-toolkit-3.0-SNAPSHOT.dll", "sw-fa-prod-selector35.dll"):
    p = B / dll
    if not p.is_file(): continue
    raw = p.read_bytes()
    # 找含 "http" 的字符串（API 端点）
    urls = set()
    for m in re.findall(rb"(?:[ -~]\x00){8,120}", raw):
        try: s = m.decode("utf-16le")
        except Exception: continue
        if re.search(r"https?://|/api/|/biz/|forface", s, re.I):
            urls.add(s.strip())
    print("### %s" % dll)
    for u in sorted(urls)[:18]:
        print("   ", u[:96])