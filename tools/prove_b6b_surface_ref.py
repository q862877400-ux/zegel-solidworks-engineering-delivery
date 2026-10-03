"""★ B6-b 真机探针：旋转曲面 / 放样曲面（另 2 条单列，见实现层模块尾）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_b6b_surface_ref.py
# 定位:   ★ 2026-10-03（轮 475）★ 给 `scripts/sw_surface_ref_ops.py` 留真机证据。
#
#   ★ 结构照抄**本仓已被真机验证过的**骨架（`tools/prove_b6a_surface_edit.py`）：
#     · `sw, _ = connect_solidworks(wait_seconds=30)`（★ 它回元组）
#     · **每个用例一个新文档** ⇒ 失败不拖累后续
#     · `P.start_sketch` / `SP.sketch_3point_corner_rectangle` / `P.end_sketch`（★ 本仓包装）
#     · **判据 = 特征树叶子名增量**（`sw_part.feature_names`）
#
#   ★★ **两条各自的"前置"（官方 Remarks 要求先选）**：
#     · **旋转曲面** ⇒ 要**轮廓 + 中心线**。★ 官方 Remarks 只说用 `SelectByID2` 选、
#       **没给 mark** ⇒ ★ 本探针按**轮廓草图**选（★ 若不成，如实记，不硬凑）。
#     · **放样曲面** ⇒ 要**至少两个轮廓**，★ 官方逐字 "profile selections should be **1**"
#       ⇒ ★ 本探针按 **mark=1** 选两个草图。
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: 见 `scripts/sw_surface_ref_ops.py` 的模块头（三源逐条）。
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
from scripts import sw_surface_ref_ops as M                          # noqa: E402
import scripts.sw_sketch_primitives as SP                            # noqa: E402


def _mk_sketch(doc, plane, pts):
    """★ 开草图 → 画矩形 → **趁草图还开着捕获 ref** → 退草图 → 回那个 ref。

    ★★★ 2026-10-03（轮 475）**这是本轮的真因修正** ——
      `sw_part._capture_sketch_ref` 的**第一句**是：
      ```python
      if sketch_obj is None:
          sketch_obj = _safe_com_member(model.SketchManager, "ActiveSketch")
      ```
      ⇒ ★ **它只从「活动草图」取**。
      ★ 而我前两版都是**先 `end_sketch` 再去拿 ref** ⇒ `ActiveSketch` 为 `None`
        ⇒ ref 为 `None` ⇒ 选不中 ⇒ 两条全回“树无增量”。
      ★ 而 `SketchSelectionRef` 里存的是**对象引用**（`sketch` / `feature` / `contours`）
        ⇒ ★ **退草图后仍可用** ✓
    """
    P.start_sketch(doc, plane_name=plane)
    SP.sketch_3point_corner_rectangle(doc, *pts)
    ref = None
    try:
        ref = P._capture_sketch_ref(doc, source="b6b-probe")
    except Exception:                                                    # noqa: BLE001
        ref = None
    P.end_sketch(doc)
    return ref


def _select_sketch_contour(doc, name, mark):
    """★ 用**本仓现成机制**选草图（★ 带 mark）。

    ★★ 2026-10-03（轮 475）**这是本轮的关键修正** ——
      我第一版用 `_select_sketch_feature_by_name(doc, "草图1")`，
      ★ 而那选的是**草图特征**、**不是轮廓**，且**传不了 mark** ⚠
      ⇒ 两条全回“树无增量”。

    ★ 本仓的正路（`scripts/sw_part.py`）：
      `_capture_sketch_ref(model, fallback=name)` 拿到引用 ⇒
      `_select_sketch_ref(model, ref, mark=mark)` 按**稳定优先级**选：
      `feature` → `sketch` → **`contours`** → `regions` → `segments`
      ★ 而它底下走 `_select_any_object(objects, append, **mark**)` —— ★ mark 能传进去 ✓
    """
    try:
        ref = P._capture_sketch_ref(doc, fallback=name)
        if ref is None:
            return False
        return bool(P._select_sketch_ref(doc, ref, mark=int(mark)))
    except Exception:                                                    # noqa: BLE001
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


def _case_revolve(doc):
    """★ 旋转曲面：草图轮廓 + 一条**中心线** ⇒ 选轮廓 ⇒ 调（★ 官方没给 mark）。"""
    P.start_sketch(doc, plane_name="Front Plane")
    #: ★ 轮廓：矩形（避开中心线所在轴）
    SP.sketch_3point_corner_rectangle(doc, 5, -10, 25, -10, 25, 10)
    #: ★ 中心线：过原点、X 方向（★ 旋转轴）
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCenterLine",
                     0.0, 0.0, 0.0, 30.0, 0.0, 0.0)
    P.end_sketch(doc)
    #: ★ 选轮廓草图（★ 官方 Remarks 未给 mark ⇒ 先按 mark=0 试）
    #: ★ 用本仓机制选**轮廓**（★ 官方 Remarks 没给 mark ⇒ 先试 mark=0）
    for cand in ("草图1", "Sketch1"):
        if _select_sketch_contour(doc, cand, 0):
            break
    return M.insert_revolved_ref_surface(doc, 360.0, 0, False, 0.0)


def _case_loft(doc):
    """★ 放样曲面：**两个**草图（不同基准面）⇒ 按 **mark=1** 各选一次 ⇒ 调。"""
    refs = [r for r in (_mk_sketch(doc, "Front Plane", (-20, -10, 20, -10, 20, 10)),
                        _mk_sketch(doc, "Top Plane", (-10, -8, 10, -8, 10, 8))) if r is not None]
    try:
        C.get_com_member(doc, "ClearSelection2", True)
    except Exception:                                                    # noqa: BLE001
        pass
    #: ★ 两个轮廓，★★ **mark = 1**（官方 Remarks 逐字：
    #:   "The mark for: **profile selections should be 1**"）
    #:   ★ 而 `_select_sketch_ref` 内部会先 `ClearSelection2` ⇒ **选不了两个** ⚠
    #:   ⇒ 故改成：直接用 `_select_any_object` 在**同一个选区**里追加第二个。
    picked = 0
    for ref in refs:
        #: ★ 按本仓的优先级取第一个能选的对象；★★ mark = 1（官方 Remarks）
        for objs in (ref.contours, ref.feature, ref.sketch, ref.regions, ref.segments):
            if P._select_any_object(objs, append=(picked > 0), mark=1):
                picked += 1
                break
    return M.insert_lofted_ref_surface(doc, False, True, False, 0.0, 0, 0)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "B6-b 曲面特征第二组 2 条逐个真机跑（specs/201-toolbar-gaps）",
          "judge": "特征树叶子名增量（sw_part.feature_names）",
          "items": []}
    ev["items"].append(_one(sw, "旋转曲面", _case_revolve))
    ev["items"].append(_one(sw, "放样曲面", _case_loft))
    ev["passed"] = sum(1 for i in ev["items"] if i.get("verdict") == "能")
    ev["total"] = len(ev["items"])
    p = R / "output" / "b6b-surface-ref-evidence.json"
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
