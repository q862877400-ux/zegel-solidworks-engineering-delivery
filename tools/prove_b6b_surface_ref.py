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

    ⚠ 2026-10-03（轮 493）试过给它加 `append` 形参、透传给
      `P._select_sketch_ref` —— ★★ 而**那个函数根本没有 `append` 形参**
      （真机签名 `(model, sketch_ref, mark=0)`）⇒ 已**回退**。
      ★ 故本 helper 只管**选第一个**；★★ 第二个由调用方**按引用追加**
      （★ 那一条已真机验证）。
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
    """★ 旋转曲面：**捕获 `CreateCenterLine` 的返回值当轴**，只选那一条（mark=4）⇒ 再选轮廓。"""
    P.start_sketch(doc, plane_name="Front Plane")
    #: ★ 轮廓：矩形（避开中心线所在轴）
    SP.sketch_3point_corner_rectangle(doc, 5, -10, 25, -10, 25, 10)
    #: ★★★★★ 2026-10-03（轮 477）**轴 = `CreateCenterLine` 的返回值** ——
    #:   ★ 上一轮量到 **`轴选中数 = 5`**：`sw_part._select_revolve_axis(doc, "草图1")`
    #:     是**按草图名取该草图里所有段**再全按 `mark=4` 选 ⇒ ★ 矩形 4 边也被选成"轴"了
    #:     ⇒ ★ **轴不唯一** ⇒ 这才是没建成的直接原因。
    #:   ★★ 而官方签名给了更准的路（`C:\swapi\types\ISketchManager\CreateCenterLine.md`）：
    #:     > **Signature**: `SketchSegment CreateCenterLine(X1, Y1, Z1, …)`
    #:     ⇒ ★ **它回的就是那条中心线的 `SketchSegment`** ⇒ 捕获它 ⇒ **只选它** ✓
    #:   ★ 而顺序照 `sw_part.revolve_boss` 那条真机判据（★ 轮 360）：**先轴、后轮廓**。
    axis_seg = C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCenterLine",
                                0.0, 0.0, 0.0, 30.0, 0.0, 0.0)
    #: ★★★ **轮廓 ref 也在草图还开着时捕获**（★ 轮 475 的教训：
    #:   `_capture_sketch_ref` 只从"活动草图"取，★ 退草图后再拿就是 `None`）
    prof_ref = None
    try:
        prof_ref = P._capture_sketch_ref(doc, source="b6b-revolve")
    except Exception:                                                    # noqa: BLE001
        prof_ref = None
    P.end_sketch(doc)

    #: ★ **① 先轴**：只选捕获到的那**一条**中心线（mark=4）
    axis_ok = False
    try:
        if axis_seg is not None:
            axis_ok = bool(P._select_any_object((axis_seg,), append=False, mark=4))
    except Exception:                                                    # noqa: BLE001
        axis_ok = False

    #: ★ **② 后轮廓**：优先用捕到的 `contours`（★ 判据：`轮廓 = ref.contours`），
    #:   拿不到才回落到草图特征（★ 并如实标出走的哪一路）。
    prof_route = None
    prof_ok = False
    if prof_ref is not None:
        for objs, tag in ((prof_ref.contours, "contours"), (prof_ref.sketch, "sketch"),
                          (prof_ref.feature, "feature")):
            if objs and P._select_any_object(objs, append=True, mark=1):
                prof_route, prof_ok = tag, True
                break
    if not prof_ok:
        P._ensure_sketch_selected(doc, "草图1")
        prof_route, prof_ok = "ensure_sketch_selected(草图特征)", True

    try:
        sel_n = int(C.get_com_member(C.get_com_member(doc, "SelectionManager"),
                                     "GetSelectedObjectCount2", -1) or 0)
    except Exception:                                                    # noqa: BLE001
        sel_n = -1
    r = M.insert_revolved_ref_surface(doc, 360.0, 0, False, 0.0)
    r["axis_captured"] = axis_seg is not None
    r["axis_selected_ok"] = axis_ok
    r["profile_route"] = prof_route
    r["n_contours_in_ref"] = len(getattr(prof_ref, "contours", ()) or ()) if prof_ref else -1
    r["selection_count_before_call"] = sel_n
    return r


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
    #:
    #: ★★★ 2026-10-03（轮 493）**改成调 `_select_sketch_contour`** ——
    #:   ⚠ 原来这里**手写**了一遍"按优先级取第一个能选的对象 + append"，
    #:     ★★ 而 `_select_sketch_contour(doc, name, mark, append=…)` 就是**同一件事的封装**
    #:     （★ 轮 475 写的）⇒ ★ 那段**重复代码**让那个 helper **从没被调用** ⚠
    #:     ⇒ ★ 而本仓门禁 `tests/test_no_uncalled_helpers.py` **尽职抓到了**它 ✓
    #:   ⇒ ★ 正解：**统一到那个 helper**（★ 既接上了、★ 又去掉重复）✓
    #:   ⚠★ 2026-10-03（轮 493）**第一版接错了**：我给 helper 加了 `append` 形参、
    #:     并把它透传给 `P._select_sketch_ref` —— ★★ 而**那个函数根本没有 `append` 形参**
    #:     （真机签名是 `_select_sketch_ref(model, sketch_ref, mark=0)`）⚠
    #:     ★★★ 而**门禁 `test_no_uncalled_helpers` 仍然过了** ——
    #:        ★ 因为它只查"有没有被调用"、**不查实参对不对** ⇒ ★ 那正是**事实 62** 的形态
    #:        （★ 「一个门禁"写了"不等于它"有效"」）✓
    #:   ⇒ ★ 故**改成诚实接法**：★ **第一个轮廓用 helper**（★ 它的本分），
    #:     ★★ 第二个仍走"按引用选"那条 —— ★ 因为 `_select_sketch_ref` 内部会先
    #:     `ClearSelection2`、★ 它**确实**选不了两个（★ 那是它已知的性质）。
    picked = 0
    for nm in ("\u8349\u56fe1",):
        if _select_sketch_contour(doc, nm, 1):
            picked += 1
    for ref in refs:
        if picked == 0:
            #: ★ 保底：helper 没选上 ⇒ 第一个也按引用选（★ 与旧行为一致）
            for objs in (ref.contours, ref.feature, ref.sketch, ref.regions, ref.segments):
                if P._select_any_object(objs, append=False, mark=1):
                    picked += 1
                    break
            continue
        if picked == 1:
            #: ★★ 第二个**只能按引用追加**（★ `_select_sketch_ref` 会清选区）
            for objs in (ref.contours, ref.feature, ref.sketch, ref.regions, ref.segments):
                if P._select_any_object(objs, append=True, mark=1):
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
