import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

#: 「定性断言」的措辞 —— 这些是从**异常/失败**推出"做不到"的地方
PAT = re.compile(r"(架构性|架构限制|到不了|不可用|做不到|无法调用|不可达|走不通)")
#: 「回读」的措辞 —— 有它才说明结论是靠**状态**而不是靠**异常**
READBACK = re.compile(r"(回读|计数|线段数|GetSelectedObjectCount|回读状态)")

rows = []
for f in sorted((R / "scripts").glob("*.py")) + sorted((R / "tools").glob("*.py")):
    try:
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:      # noqa: BLE001
        continue
    for i, l in enumerate(lines, 1):
        if PAT.search(l):
            #: 看这一行**前后 8 行**有没有"回读"字样（判定依据是状态还是异常）
            win = "\n".join(lines[max(0, i - 9):i + 8])
            rows.append({
                "file": f.name, "line": i,
                "text": l.strip()[:96],
                "has_readback": bool(READBACK.search(win)),
            })
print("  含「定性断言」措辞的行: **%d** 处" % len(rows))
by_file: dict = {}
for r in rows:
    by_file.setdefault(r["file"], []).append(r)
print()
print("  按文件（★ = 该处附近**没有**回读字样 ⇒ **疑似「只看异常就定性」**）：")
for fn, rs in sorted(by_file.items(), key=lambda kv: -len(kv[1]))[:16]:
    n_no = sum(1 for r in rs if not r["has_readback"])
    print("    %-30s %2d 处 · ★无回读 %d 处" % (fn, len(rs), n_no))
print()
print("  ── ★ 疑似「只看异常就定性」的具体行（前 18 条）──")
n = 0
for r in rows:
    if not r["has_readback"]:
        print("    %-26s:%-4d %s" % (r["file"], r["line"], r["text"][:84]))
        n += 1
        if n >= 18:
            break
