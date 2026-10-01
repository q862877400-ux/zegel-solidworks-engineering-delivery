import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

MARK = "def sketch_line("
assert MARK in t, "锚点不符"

BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   `wzyn20051216/solidworks-automation-skill`（**上游**，MIT）—— 本段是**上游继承**的
#         草图/特征助手（`sketch_*` / `extrude_*` / `fillet` / `chamfer` / `rib` / …），
#         **不是**从四家外部 MCP 项目移植的。
# 文件:   scripts/sw_part.py —— 「草图与特征助手」这一段（L427 起，到下一个来源块之前）。
# 定位:   2026-10-01（轮 132）**只做了一件事**：把这些函数的**长度单位声明**从
#         「米」校正为「**毫米**」—— 因为实测发现原声明**与实际不符**。
#         实测依据：`tools/verify_ellipse_smoke.py` —— 半径 **25** 的圆（**未换算**）
#         经拉伸后 `get_bounding_box` 得跨度 **50**（毫米）；拉伸 **10** ⇒ 跨度 **10**（毫米）。
#         ★ 与 `IBody2.GetBodyBox` 的返回单位一致（已知事实 71）。
# 官方签名依据: 这些函数的 COM 入口（`CreateCircleByRadius` / `CreateCornerRectangle` /
#         `FeatureExtrusion3` / `FeatureCut4` …）的官方依据见**原上游代码**与
#         `docs/signature-audit.md`；本块**不改任何调用**，只校正单位声明。
# 许可:   上游 MIT（保留版权声明，见 `THIRD-PARTY-NOTICES.md` §一.1）。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块涵盖这一段全部助手函数，**止于下一个来源块**（「边界框」那块）。
# ─────────────────────────────────────────────────────────────────────

"""
i = t.index(MARK)
if "「草图与特征助手」这一段" not in t:
    t = t[:i] + BLOCK + t[i:]
    P.write_text(t, encoding="utf-8")
    print("  ok 已在 sketch_line 前插入来源块（覆盖: 后续同级定义）")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
