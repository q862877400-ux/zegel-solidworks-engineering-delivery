import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
changed = []

#: ① 8 个 tools 文件：`from sw_connect import residual_dialogs` ⇒ 补上 dismiss_residual_dialogs
OLD1 = "from sw_connect import residual_dialogs"
NEW1 = "from sw_connect import dismiss_residual_dialogs, residual_dialogs"
for p in sorted((R / "tools").glob("*.py")):
    t = p.read_text(encoding="utf-8")
    if OLD1 in t and "dismiss_residual_dialogs" in t and "dismiss_residual_dialogs," not in t:
        p.write_text(t.replace(OLD1, NEW1, 1), encoding="utf-8")
        changed.append(str(p.relative_to(R)))

#: ② sw_jlcfa_cards.py：`_drag` 里用 time 而没导入 ⇒ 函数内补（★ 照该函数既有风格）
p = R / "scripts" / "sw_jlcfa_cards.py"
t = p.read_text(encoding="utf-8")
if "    import time\n" not in t:
    t2 = t.replace("def _drag(x1, y1, x2, y2, steps: int = 12) -> None:\n    import win32api",
                   "def _drag(x1, y1, x2, y2, steps: int = 12) -> None:\n    import time\n    import win32api", 1)
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
        changed.append("scripts/sw_jlcfa_cards.py")

#: ③ probe_window_vs_graphics.py：`SW_PID` ⇒ 仓里叫 `sw_pid()`
p = R / "tools" / "probe_window_vs_graphics.py"
t = p.read_text(encoding="utf-8")
if "SW_PID" in t and "sw_pid" not in t:
    t2 = t.replace("SW_PID", "sw_pid()")
    #: ★ 需要导入它 —— ★ 插在最后一个 top-level import 之后
    lines = t2.splitlines()
    last = max(i for i, l in enumerate(lines) if l.startswith("import ") or l.startswith("from "))
    lines.insert(last + 1, "from sw_guard import sw_pid")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    changed.append("tools/probe_window_vs_graphics.py")

print("  改了 %d 个文件：" % len(changed))
for c in changed:
    print("     " + c)
st = subprocess.run(["git", "diff", "--stat"], cwd=str(R), capture_output=True,
                    text=True, encoding="utf-8", errors="replace").stdout
print("\n  git diff --stat：")
for l in st.strip().splitlines()[-16:]:
    print("     " + l)
dele = sum(int(m.group(1)) for m in re.finditer(r"(\d+) deletion", st))
print("\n  \u2605 deletions \u5408\u8ba1 = %d\uff08\u2605 \u5fc5\u987b\u4e3a 0 \u2014\u2014 \u4e8b\u5b9e 61\uff09" % dele)
