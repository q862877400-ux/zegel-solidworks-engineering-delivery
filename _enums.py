import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = Path(r"D:\AI\SW\_raw\reflect_sldworks\enum_sldworks.txt")
if not p.is_file():
    print("NO ENUM FILE")
    raise SystemExit(0)
txt = p.read_text(encoding="utf-8", errors="replace")
for ename in ("swUserPreferenceStringValue_e", "swUserPreferenceIntegerValue_e",
              "swUserPreferenceToggle_e", "swUserPreferenceDoubleValue_e"):
    m = re.search(r"(?ms)^## %s\r?\n(.*?)(?=\r?\n## |\z)" % ename, txt)
    if not m:
        print("### %s  NOT FOUND" % ename); continue
    body = [l.strip() for l in m.group(1).splitlines() if l.strip()]
    print("### %s (%d)" % (ename, len(body)))
    for l in body[:10]:
        print("   ", l)
