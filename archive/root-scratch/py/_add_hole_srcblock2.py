import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hole_features.py")
t = P.read_text(encoding="utf-8")

MARK = "# ── 可用入口：把\"孤儿包装\"接成能用的 API（2026-10-01 轮 124）──────────"
assert MARK in t, "锚点不符"

BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_hole_features.py —— 「把孤儿包装接成可用 API」这一段。
# 定位:   2026-10-01（轮 124）补：`get_hole_standards` 等 4 个包装**在仓库里没有调用方**
#         （它们把出参甩给调用方）⇒ 本节提供自己造容器、自己读回来的高层入口。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `Object GetHoleStandardsData(Int32)`（在 `ISldWorks` 上）
#             `Boolean GetHoleStandards(Object&, Object&)`（在 `IHoleStandardsData` 上）
#           ② `C:\\swapi\\types\\ISldWorks\\GetHoleStandardsData.md`
#             （`HoleTypeID` 取自 `swWzdGeneralHoleTypes_e`；**= 5 `swWzdLegacy` 时返回 null**）
#           ③ `C:\\swapi\\types\\IHoleStandardsData\\GetHoleStandards.md`
#           ④ ★ **出参传法**取自真机裁断（已知事实 68，
#             `tools/probe_outparam_object_byref.py`）：只有 `VT_BYREF|VT_VARIANT` 可用。
#           ⑤ ★ **出参读回来是 tuple**：真机量到两组各 15 元、**一一对应**
#             （`tools/verify_hole_standards_smoke.py`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `_out_container` / `_out_value` / `_as_list` /
#         `list_hole_standards` 四个单元。
# ─────────────────────────────────────────────────────────────────────

"""
i = t.index(MARK)
t = t[:i] + BLOCK + t[i:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已插入来源块；语法 OK")
