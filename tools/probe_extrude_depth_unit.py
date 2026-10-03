"""★ 定案：`extrude_boss(20.0)` 建出来的实体，★ **真实的 bounding box 是多少毫米**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_part.py::extrude_boss`（★ docstring 写「毫米」、★ 而 `D1` 原样透传）·
#         `scripts/sw_part.py::get_bounding_box`（★ 量实体）
# 定位:   ★★★★ **判据（★ 一个数就能定案）**：★ docstring 说 `depth` 是**毫米** ⇒
#   ★ 若 `extrude_boss(model, "Sketch1", 20.0)` 建出来的板**厚 20 mm** ⇒ 函数对；
#   ★★ **若厚 20000 mm（= 20 米）** ⇒ ★★★ **函数把毫米当米传了** ✓
#   ★ **而上一轮的读数矛盾正是这么来的**：★ 尺寸值被读成 20000 ⇒ ★ 那是**真的 20000 毫米** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "extrude-depth-unit-evidence.json"


def main() -> int:
    import sw_part as P
    from sw_connect import connect_solidworks, new_document

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    #: ★ 画一个 100×60 的矩形（★ 那两维走 `sketch_corner_rectangle`，★ 单位是**米**——见下）
    P.sketch(model, "Front Plane")
    P.sketch_corner_rectangle(model, -50.0, -30.0, 50.0, 30.0)
    P.end_sketch(model)
    #: ★★ 关键调用：★ docstring 说这里是**毫米**
    P.extrude_boss(model, "Sketch1", 20.0)
    bb = P.get_bounding_box(model)
    R = {
        "★_判据": "★ docstring 说 `depth` 是毫米 ⇒ 厚应为 **20 mm**；"
                  "★ 若厚 **20000 mm** ⇒ ★ 函数把毫米当米传了",
        "★_调用": "extrude_boss(model, 'Sketch1', **20.0**)",
        "bounding_box": bb,
        "features": P.feature_names(model)[:8],
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(R, ensure_ascii=False, indent=1, default=str)[:1200])
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
