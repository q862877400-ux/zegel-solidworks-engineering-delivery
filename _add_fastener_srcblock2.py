import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hole_features.py")
t = P.read_text(encoding="utf-8")

MARK = "def list_fastener_types(sw, standard_name: str, hole_type_id: int = 0):"
assert MARK in t, "锚点不符"

BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_hole_features.py —— 「紧固件链路」这一段（轮 125）。
# 定位:   把 `get_fastener_types` / `get_fastener_table_types` / `get_fastener_table`
#         三个包装接成可用的高层入口（它们此前同样**没有调用方**）。
#         链路：标准（15）→ 紧固件类型（14）→ 表类型（`[0,1,2]`）。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `Boolean GetFastenerTypes(String, Object&, Object&)` ·
#             `Boolean GetFastenerTableTypes(String, Int32, Object&)` ·
#             `Boolean GetFastenerTable(String, Int32, Int32, out Object)`
#           ② `C:\\swapi\\types\\IHoleStandardsData\\GetFastenerTable.md`
#             （第 4 参是 `out System.object HoleTable`，类型 `[[IHoleDataTable]]`）
#           ③ ★ **必须热身的约束**是**真机查出**的，官方**未写**
#             （`_probe_fastener_ordering.py` 四组对照 A/B/C/D）
#           ④ ★ 出参读回来是 `tuple`、两组一一对应（`tools/verify_hole_standards_smoke.py` 11/11）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 本段与文件里**已有**的来源块交错，用「后续同级定义」会被
#         下一个来源块截断（**轮 125 实测踩到**）⇒ 这里用「全文件」以保证覆盖。
# ─────────────────────────────────────────────────────────────────────

"""
i = t.index(MARK)
t = t[:i] + BLOCK + t[i:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已在 L%d 之前插入来源块（覆盖: 全文件）" % (t[:i].count(chr(10)) + 1))
