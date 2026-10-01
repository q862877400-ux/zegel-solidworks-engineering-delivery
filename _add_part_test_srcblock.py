import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_part_sketch_selection.py")
t = P.read_text(encoding="utf-8")
lines = t.splitlines(keepends=True)
k = next(i for i, l in enumerate(lines)
         if l.startswith("class ") or l.startswith("def ") or l.startswith("@"))
BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）。
# 文件:   tests/test_sw_part_sketch_selection.py —— 本文件自身。
# 定位:   `scripts/sw_part.py` 的离线回归测试；轮 127 追加**边界框**那 3 条判据
#         （`GetBodyBox` 的原始值就是毫米、官方 approximate 声明要照抄、失败要抛）。
# 官方依据: `C:\\swapi\\types\\IBody2\\GetBodyBox.md`；
#           真机单位裁断见 `tools/verify_bbox_smoke.py` 与已知事实 71。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

"""
t = "".join(lines[:k]) + BLOCK + "".join(lines[k:])
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已插来源块（覆盖: 全文件）")
