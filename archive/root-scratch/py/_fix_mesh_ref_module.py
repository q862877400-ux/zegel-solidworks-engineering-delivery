import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_import_mesh_reference.py")
t = P.read_text(encoding="utf-8")

#: ① 去掉导入括号里的多余空行
t2 = re.sub(r"(\n[ \t]+save_document,\n)\n([ \t]+\))", r"\1\2", t)
if t2 != t:
    print("  ✓ 已去掉导入块里的多余空行")
    t = t2

#: ② 加来源块（在本文件第一段 import 之前）
BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（AGENTS.md 铁律 1 认可的第三类来源）。
# 文件:   scripts/sw_import_mesh_reference.py —— 本文件的**依赖导入块**（轮 145 改动）。
# 定位:   2026-10-01（轮 145）：把「**故意要调**」的零参调用从 `get_com_member` 迁到
#         **`call_com_member`**（名字即意图）⇒ 本文件的 try/except 两条导入路径都要加上它。
#         ★ 起因见 `docs/known-facts.md` 事实 84/85 与 `tools/audit_get_com_member_semantics.py`。
# 官方签名依据: 本块只改导入名，**不改任何 COM 调用**；各调用的依据在原函数处。
# 许可:   本仓库 MIT。无第三方代码引用。
# 覆盖:   全文件 —— ⚠ 本块是**轮 145 那次导入改动**的说明，
#         它**不替代**本文件里原有的、更精确的逐单元来源块（若将来补上）。
# ─────────────────────────────────────────────────────────────────────

"""
lines = t.splitlines(keepends=True)
if "轮 145" not in t:
    #: 插在最后一个 `import`/`from` 之前的空行处，或 shebang/docstring 之后
    ins = 0
    for i, l in enumerate(lines[:40]):
        if re.match(r"^(import |from |try:)", l):
            ins = i
            break
    lines.insert(ins, BLOCK)
    t = "".join(lines)
    print("  ✓ 已插入来源块（第 %d 行前）" % (ins + 1))
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
