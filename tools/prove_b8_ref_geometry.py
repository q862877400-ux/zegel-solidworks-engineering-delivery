"""★ B8 真机探针：基准面 / 坐标系 / 点 / 质心 / 边界框。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_b8_ref_geometry.py
# 定位:   ★ 2026-10-03（轮 479）★ 给 `scripts/sw_ref_geometry.py` 留真机证据。
#
#   ★ 结构照抄**已被真机验证过的**骨架（`tools/prove_b6a_surface_edit.py`）：
#     · `sw, _ = connect_solidworks(wait_seconds=30)`（★ 它回元组）
#     · **每个用例一个新文档** ⇒ 失败不拖累后续
#     · 用本仓包装（`P.start_sketch` / `P.extrude_boss` / `SP.*`），**不裸调**
#     · **判据 = 特征树叶子名增量**（`sw_part.feature_names` —— ★ 轮 473 的教训）
#
#   ★★ **前置**（★ 这三条官方都要求"先选参考实体"）：
#     · **质心 / 边界框** ⇒ 要对**有几何的文档**才有意义 ⇒ ★ 先建一个**实体**（拉伸凸台）
#     · **基准面 / 坐标系 / 点** ⇒ ★ 官方说要先按 mark 选参考实体，而**没给 mark 表**
#       ⇒ ★ 本探针**先不选**试一次（★ 若不成，如实记，★ 不硬凑 —— ★ 上一批的教训）
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: 见 `scripts/sw_ref_geometry.py` 的模块头（三源逐条）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每条回 `verdict/new_features/verified_by`，产物落 `output/`。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                  # noqa: E402
from scripts import sw_part as P                                     # noqa: E402
from scripts import sw_ref_geometry as M                             # noqa: E402
import scripts.sw_sketch_primitives as SP                            # noqa: E402


def _solid(doc, plane="Front Plane", pts=(-20, -10, 20, -10, 20, 10), depth=0.02):
    """★ 建一个**实体**当前置（★ 质心/边界框要有几何才有意义）。"""
    P.start_sketch(doc, plane_name=plane)
    SP.sketch_3point_corner_rectangle(doc, *pts)
    P.end_sketch(doc)
    for cand in ("草图1", "Sketch1"):
        try:
            if P.extrude_boss(doc, cand, depth):
                return True
        except Exception:                                                # noqa: BLE001
            continue
    return False


def _one(sw, zh, fn):
    """★ 每个用例一个新文档（★ 现成骨架）。"""
    row = {"zh": zh, "verdict": "不能"}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        r = fn(doc)
        row.update(r if isinstance(r, dict) else {"returned": str(r)})
        row["verdict"] = "能" if row.get("ok") else "不能"
    except Exception as exc:                                             # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                            # noqa: BLE001
                pass
    return row


def _case(zh, needs_solid, fn):
    """★ 包一层：按需先建实体。"""
    def run(doc):
        built = _solid(doc) if needs_solid else None
        r = fn(doc)
        if needs_solid:
            r["solid_built"] = built
        return r
    run.__name__ = zh
    return _one, run


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "B8 参考几何体 5 条逐个真机跑（specs/201-toolbar-gaps）",
          "judge": "特征树叶子名增量（sw_part.feature_names）",
          "items": []}

    cases = [
        ("质心", True, lambda d: M.insert_center_of_mass(d)),
        #: ★★★ 2026-10-03（轮 479）**换成员**：台账 T701 给的 `Create3DBoundingBox`
        #:   官方原话是「for a **cut list item in a weldment part**」⇒ ★ **焊件切割清单专用**，
        #:   ★ 普通零件上不成是**应然的**。★ 工具栏那个的真名是
        #:   **`IFeatureManager.InsertGlobalBoundingBox2`** ✓
        ("边界框", True, lambda d: M.insert_global_bounding_box(d, 1, 0, False, False)),
        #: ★ 基准面：★ 上一轮用 `Parallel(1)` 且**不选**⇒不成；本轮改 **`Coincident(4)` + 先建实体**
        ("基准面", True, lambda d: M.insert_ref_plane(d, 4, 0.0, 0, 0.0, 0, 0.0)),
        ("坐标系", False, lambda d: M.insert_coordinate_system(d, False, False, False)),
        #: ★ 点：★ 用 FaceCenter（★ 要有面 ⇒ 先建实体）
        ("点", True, lambda d: M.insert_reference_point(d, 4, 0, 0.0, 1)),
    ]
    for zh, solid, fn in cases:
        _, run = _case(zh, solid, fn)
        ev["items"].append(_one(sw, zh, run))

    ev["passed"] = sum(1 for i in ev["items"] if i.get("verdict") == "能")
    ev["total"] = len(ev["items"])
    p = R / "output" / "b8-ref-geometry-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("  \u8bda\u5b9e %s / %s" % (ev["passed"], ev["total"]))
    for i in ev["items"]:
        tb, ta = i.get("tree_before"), i.get("tree_after")
        extra = ("  \u6811 %d\u2192%d %s" % (len(tb), len(ta), i.get("new_features"))) if tb and ta else ""
        print("  %-8s %-4s %-28s%s" % (i.get("zh"), i.get("verdict"),
                                       i.get("verified_by") or "", extra))
        if i.get("err"):
            print("        err=%s" % str(i["err"])[:90])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
