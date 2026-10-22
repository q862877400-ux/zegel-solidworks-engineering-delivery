"""★ 真机验：段 3 的 2 个工具（`current_sketch_name` · `auto_dimension_sketch`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_part_read_and_dimension.py
# 定位:   ★ 2026-10-03（轮 399）24h 计划 v2 **段 3** 的真机探针（无单位歧义的两条）。
# 被验的工具见 `mcp-server/tool_specs_batch55.py`。★ 另两条（`add_dimension` / `linear_p
# attern`）
#   **故意不在本批** —— 它们的包装不做换算而官方 API 吃米（文档却写毫米）⇒ 先测单位再挂。
# 官方依据: `ISketch.AutoDimension2`（★ 5 参）· `IModelDoc2.GetActiveSketch2` ·
#   `ISketchManager.ActiveSketch`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 正例 + 三条可证伪的负例）：
# ```
# ① `current_sketch_name` 在**草图打开时**回**真名**（★ 中文 UI 应是「草图N」而不是回退
# 值）
# ② `auto_dimension_sketch` 在**有活动草图**时 `status` = `pass` 且 `status_code` = 0
# ③ ★ 负例：**没有活动草图**时 `auto_dimension_sketch` ⇒ `blocked` + `SKETCH_NOT_ACTIVE`
# ④ ★ 负例：草图**关闭后** `current_sketch_name(fallback="...")` ⇒ 回**那个回退值**
#    （★ 那验证的是**已文档化的局限**：★ 回退值 ≠ 真名 ⇒ 别拿它去按名取草图）
# ```
# ★ 全程走 `sw_guard` 护栏（AGENTS.md 的常驻纪律）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "part-read-dimension-evidence.json"
)


def main() -> int:
    import sw_connect
    from sw_part import (
        auto_dimension_sketch,
        current_sketch_name,
        end_sketch,
        sketch_corner_rectangle,
        start_sketch,
    )

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["doc"] = {
            "ok": True,
            "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""),
        }
        #: ★ 负例③：**先**在没有草图时调 auto_dimension（★ 顺序很重要 —— 一旦开过草图，
        #:   后面"没有活动草图"的状态就不好造了）
        r0 = auto_dimension_sketch(doc)
        ev["steps"]["neg_auto_dim_no_sketch"] = {
            "ok": (
                r0.get("status") == "blocked"
                and r0.get("error_code") == "SKETCH_NOT_ACTIVE"
            ),
            "value": {k: r0.get(k) for k in ("status", "status_code", "error_code")},
        }
        #: ① 草图打开时读名字
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        name = current_sketch_name(doc)
        ev["steps"]["current_sketch_name_open"] = {
            "ok": bool(name) and not name.startswith("Fallback"),
            "value": str(name)[:40],
            "note": "★ 中文 UI 下应是「草图N」；★ 若回了 English fallback 则说明取不到",
        }
        #: ② 有活动草图时自动标注
        r1 = auto_dimension_sketch(doc)
        ev["steps"]["auto_dimension_active"] = {
            "ok": r1.get("status") == "pass",
            "value": {
                k: r1.get(k)
                for k in ("status", "status_code", "error_code", "selected")
            },
        }
        end_sketch(doc)
        #: ④ 负例：草图关闭后用自定义 fallback ⇒ 应回那个回退值（★ 已文档化的局限）
        fb = current_sketch_name(doc, "MY_FALLBACK_XYZ")
        ev["steps"]["neg_name_after_close"] = {
            "ok": fb == "MY_FALLBACK_XYZ",
            "value": str(fb)[:40],
            "note": "★ 验证的是**已文档化的局限**：★ 关闭后回退值 ≠ 真名",
        }
        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = (
            "★ 段 3 的两条（无单位歧义）；★ `add_dimension` / `linear_pattern` 因**单位存疑**"
            "（包装不换算而官方吃米、文档写毫米）**留到下一轮先测**。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
