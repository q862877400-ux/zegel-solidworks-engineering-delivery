import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
FILES = ["sw_document_data", "sw_drawing_view", "sw_geometry_selectors", "sw_gtol",
         "sw_mold", "sw_selection", "sw_sheet_metal", "sw_simulation", "sw_topology",
         "sw_view", "sw_weldment", "sw_part", "sw_assembly"]

BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/{stem}.py —— 本文件（**轮 145 的命名迁移**）。
# 定位:   2026-10-01（轮 145）**只做了一件事**：把那些「**故意要调**」的零参调用
#         从 `get_com_member(...)` 改成 **`call_com_member(...)`**。
#         ★★ 起因：审计（`tools/audit_get_com_member_semantics.py`）发现
#         `get_com_member` 的语义是「**取或调**」—— **对 COM 成员，「取」可能等于「调」**；
#         而 471 个无实参调用点里有 193 处的成员在反射里**有零参重载**（会真的执行）。
#         ★ 逐条读过之后确认：**作者大多是故意的**（拿返回值当成败 / 要的就是那个动作），
#         但**代码里读不出来** ⇒ 本轮用 `call_com_member` **让名字表态**。
# 官方签名依据: 本次迁移**不改任何 COM 调用**（只是换个名字），
#         各调用的官方依据在原函数的来源块里。
# 许可:   本仓库 MIT（上游部分见 `THIRD-PARTY-NOTICES.md`）。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 本块是**轮 145 迁移这件事**的说明，
#         它**不替代**本文件里原有的、更精确的逐函数来源块。
# ─────────────────────────────────────────────────────────────────────

"""

done = 0
for stem in FILES:
    p = ROOT / "scripts" / (stem + ".py")
    t = p.read_text(encoding="utf-8")
    if "轮 145 的命名迁移" in t:
        print("  · %s 已有" % stem)
        continue
    lines = t.splitlines(keepends=True)
    #: 插在**模块 docstring 之后**（若有），否则文件头
    ins = 0
    if lines and lines[0].lstrip().startswith(('"""', "'''", 'r"""', "r'''")):
        q = '"""' if '"""' in lines[0] else "'''"
        ins = 1
        while ins < len(lines) and q not in lines[ins]:
            ins += 1
        ins += 1
    lines.insert(ins, BLOCK.format(stem=stem))
    p.write_text("".join(lines), encoding="utf-8")
    ast.parse(p.read_text(encoding="utf-8"))
    done += 1
    print("  ✓ %s（插在第 %d 行）" % (stem, ins + 1))
print()
print("  共 %d 个文件" % done)
