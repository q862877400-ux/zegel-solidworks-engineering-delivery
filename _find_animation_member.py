"""三源查证：SolidWorks 里「动画导出 AVI」的确切成员名。

源① `D:\\AI\\SW\\_raw\\**\\iface_*.txt`（官方 interop 反射 ⇒ **名字与签名的权威**）
源② `C:\\swapi\\types|enums|docs`（结构化 markdown ⇒ 语义）
源③ `D:\\AI\\SW\\AI Solidworks\\官方文档\\`（CHM 解包 ⇒ 用法/示例）

⚠ 检索词**刻意收紧**（不用 `.avi` 这种松模式 —— 轮 60 实测它匹配到了 `cavity`）。
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: 与「动画导出」真正相关的词（**排除** pure 单词边界问题）
TERMS = ("SaveAnimation", "Animation", "AVI", "Movie", "VideoClip", "PlayAnimation",
         "SaveMovie", "ExportAnimation", "BeginAnimation")

print("═" * 72)
print("源① 官方 interop 反射（名字与签名权威）")
print("═" * 72)
raw = Path(r"D:\AI\SW\_raw")
iface = sorted(raw.rglob("iface_*.txt"))
print("  扫 %d 份反射" % len(iface))
hits = {}
for f in iface:
    cur = None
    for ln, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        s = line.strip()
        if s.startswith("## "):
            cur = s[3:]
            continue
        for t in TERMS:
            if t in s and not s.startswith("##"):
                hits.setdefault(t, []).append((f.parent.name, cur, s))
for t in TERMS:
    got = hits.get(t, [])
    print("\n  ── %-18s %d 处 ──" % (t, len(got)))
    seen = set()
    for src, iface_name, txt in got:
        key = (iface_name, txt)
        if key in seen:
            continue
        seen.add(key)
        print("     [%s / %s] %s" % (src, iface_name, txt[:100]))
        if len(seen) > 8:
            print("     …")
            break

print()
print("═" * 72)
print("源② C:\\swapi\\ 结构化 markdown（语义）")
print("═" * 72)
swapi = Path(r"C:\swapi")
for sub in ("types", "enums", "docs", "index"):
    d = swapi / sub
    if not d.is_dir():
        continue
    found = []
    for f in d.rglob("*.md"):
        txt = f.read_text(encoding="utf-8", errors="replace")
        for t in ("SaveAnimation", "AVI", "SaveMovie"):
            if t in txt:
                found.append((f.relative_to(swapi), t))
    print("  %-8s ⇒ %d 个文件命中" % (sub, len(found)))
    for rel, t in found[:10]:
        print("     %s   （%s）" % (rel, t))

print()
print("═" * 72)
print("源③ CHM 解包（用法/示例）")
print("═" * 72)
chm = Path(r"D:\AI\SW\AI Solidworks\官方文档")
for sub in ("CHM", "SWhelp"):
    d = chm / sub
    if not d.is_dir():
        continue
    found = []
    for f in list(d.rglob("*.htm")) + list(d.rglob("*.html")) + list(d.rglob("*.txt")):
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for t in ("SaveAnimation", "SaveMovie"):
            if t in txt:
                found.append((f.relative_to(chm), t))
    print("  %-8s ⇒ %d 个文件命中" % (sub, len(found)))
    for rel, t in found[:10]:
        print("     %s   （%s）" % (rel, t))
