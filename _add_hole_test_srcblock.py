import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_hole_features.py")
t = P.read_text(encoding="utf-8")

BLOCK = '''# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）。
# 文件:   tests/test_sw_hole_features.py —— 本文件自身。
# 定位:   复杂孔槽创建封装（`scripts/sw_hole_features.py`）的离线回归测试；
#         轮 124 追加的部分覆盖**把孤儿包装接成可用 API** 之后的 6 条契约判据。
# 官方依据: 出厂类型库反射 `iface_*.txt`；
#           `C:\\swapi\\types\\ISldWorks\\GetHoleStandardsData.md`；
#           `C:\\swapi\\types\\IHoleStandardsData\\GetHoleStandards.md`；
#           真机裁断见已知事实 68（`tools/probe_outparam_object_byref.py`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

'''

#: 插在**第一个 class/def 之前**（紧跟 import 段）
lines = t.splitlines(keepends=True)
k = next(i for i, l in enumerate(lines)
         if l.startswith("class ") or l.startswith("def ") or l.startswith("@"))
t = "".join(lines[:k]) + BLOCK + "".join(lines[k:])
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已插来源块（覆盖: 全文件）；语法 OK")
