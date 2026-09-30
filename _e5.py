import sys, io, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for p in Path(r"D:\AI\SW\_raw").rglob("enum_sldworks.txt"):
    txt = p.read_text(encoding="utf-8", errors="replace")
    names = re.findall(r"^## (\w+)", txt, re.M) or re.findall(r"^(\w+_e)\s", txt, re.M)
    print("  %d 字节 / %d 个枚举名" % (len(txt), len(names)))
    for pat in ("swUserPreferenceStringValue", "swUserPreferenceToggle", "swSelObjects", "swDocumentTypes"):
        hit = [n for n in names if pat.lower() in n.lower()]
        print("    %-30s -> %s" % (pat, hit[:3] if hit else "(无)"))
    break
