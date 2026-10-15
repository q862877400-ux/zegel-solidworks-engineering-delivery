import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_sketch_contract.py")
t = P.read_text(encoding="utf-8")
old = "# ⚠ 本文件为静态照录，未在本机实测（见 AGENTS.md 铁律 2）"
old2 = "# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）"
new = ("# ⚑ 2026-10-01（轮 117）：**本模块已真机实测** —— `python tools/verify_sketch_getters_smoke.py`\n"
       "#   （**17/17**）。⚠ 但**本文件**里的判据仍是**静态**的（零 COM）；"
       "真机证据在 capability `sketch_query` 的 `evidence` 里。")
new2 = ("# ⚑ 2026-10-01（轮 117）：本表所列取法**已真机实测**（见 `tools/verify_sketch_getters_smoke.py`）。"
        "⚠ 本表本身仍是**静态照录**。")
changed = 0
if old in t:
    t = t.replace(old, new, 1)
    changed += 1
if old2 in t:
    t = t.replace(old2, new2, 1)
    changed += 1
if changed:
    P.write_text(t, encoding="utf-8")
    print("  ok 更正了 %d 处过时注释" % changed)
else:
    print("  无可更正（或已改）")
