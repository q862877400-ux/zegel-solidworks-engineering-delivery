"""★ B6-a 真机探针：平面区域 / 等距曲面 / 直纹曲面 / 删除面 / 替换面。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_b6a_surface_edit.py
# 定位:   ★ 2026-10-03（轮 473）★ 给 `scripts/sw_surface_edit_ops.py` 留真机证据。
#
#   ★ 结构照抄本仓**已被真机验证过**的两个骨架：
# · `tools/prove_b1_sketch_primitives.py`（★ `sw, _ = connect_solidworks(wait_seconds=30
# )` ·
#       **每个用例一个新文档** · 用本仓包装不裸调 · **判据 = 几何/树读数**）
# · `tools/prove_b4_sketch_modify.py`（★ 判据分级：量到了算量到，量不到就写 `no_exceptio
# n`）
#
#   ★★ **判据 = 特征树增量**（★ 本批 3/5 的官方返回是 `void` 或 `bool` 不可信，事实 8）
#     ⇒ ★ 用 `FeatureManager.GetFeatureCount(True)` + `FeatureByPositionReverse` 取叶子名，
#       比调用前后多出哪些名字。★ 取不到就**如实写** `tree_delta: null`。
#
#   ★ 前置（★ 每条各自建，互不污染）：
#     · 平面区域 ⇒ 一个**闭合矩形草图**（★ 官方语义是用选中边界生成平面）
#     · 等距/删除/替换 ⇒ 先建一张**拉伸曲面**（★ 本仓 `sw_surface.create_extrusion_surface`
#       已有），★ 于是有**曲面体与面**可选
#     · 直纹曲面 ⇒ 选曲面体的一条**边**（★ 官方 Remarks 要 **mark=4**）
#
#   ⚠ **全程走 `tools/sw_guard.py`**（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
#     ★★ 本仓 B5 曾经**连续崩 SW 三次** ⇒ ★ 本轮每条独立 try、失败不拖累后续。
# 官方依据: 见 `scripts/sw_surface_edit_ops.py` 的模块头（三源逐条）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每条回 `{"op","verdict","new_features","verified_by"}`，产物落 `output/`。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_sketch_primitives as sp  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_edit_ops as M  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402


def _bodies(model):
    """★ 全部 body（★ **`-1` = `swAllBodies`** —— 数值照本仓现成的
    `sw_surface_features._body_count`；★ 我第一版写的 `1`/`0` **是猜的、不对**）。"""
    try:
        return list(c.get_com_member(model, "GetBodies2", -1, True) or [])
    except Exception:  # noqa: BLE001
        return []


def _faces(model):
    """★ 取第一个体的面对象清单。"""
    bs = _bodies(model)
    if not bs:
        return []
    try:
        return list(c.get_com_member(bs[0], "GetFaces") or [])
    except Exception:  # noqa: BLE001
        return []


def _edges(model):
    """★ 取第一个体的边对象清单。"""
    bs = _bodies(model)
    if not bs:
        return []
    try:
        return list(c.get_com_member(bs[0], "GetEdges") or [])
    except Exception:  # noqa: BLE001
        return []


def _select(obj, mark=0, append=False):
    """★ 按**对象**选。

    ★★ 2026-10-03（轮 473）**用本仓现成的 `sw_part._select_com_object`** ——
      它的签名是 `(obj, append=False, mark=0)`，★ **mark 直接就能传**。
      ⚠ 我第一版裸调 `Select4` + `SetSelectedObjectMark` —— ★ 绕远、而且
        `SetSelectedObjectMark` 的参数顺序我是**猜**的。
    """
    if not hasattr(P, "_select_com_object"):
        return False
    return bool(P._select_com_object(obj, append=append, mark=int(mark)))


_SW = [None]


def _one(sw, zh, fn):
    """★ 每个用例**一个新文档**（★ B1 现成骨架）⇒ 失败不拖累后续。"""
    row = {"zh": zh, "verdict": "不能", "op": zh}
    doc = None
    try:
        doc = c.new_document(sw, "part")
        r = fn(doc)
        row.update(r if isinstance(r, dict) else {"returned": str(r)})
        row["verdict"] = "能" if row.get("ok") else "不能"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def _case_planar(doc):
    """★ 平面区域：闭合矩形草图 ⇒ 退出草图 ⇒ 选草图（★ 官方语义是用选中边界）⇒ 调。"""
    P.start_sketch(doc, plane_name="Front Plane")
    sp.sketch_3point_corner_rectangle(doc, -20, -10, 20, -10, 20, 10)
    P.end_sketch(doc)
    #: ★★ `IFeatureManager` 上**没有** `FeatureByName`（★ 我第一版报
    #:   `AttributeError: <unknown>.FeatureByName`）；真名是 **`FeatureName`**，
    #:   ★ 而本仓更干净的路是 `sw_part._select_sketch_feature_by_name`。
    for cand in ("草图1", "Sketch1"):
        try:
            if P._select_sketch_feature_by_name(doc, cand):
                break
        except Exception:  # noqa: BLE001
            continue
    return M.insert_planar_surface(doc)


def _make_surface(doc):
    """★ 建一张拉伸曲面当前置。

    ★★ 2026-10-03（轮 473）**用特征级那个，不用 `IModeler` 那个** ——
      本仓 `sw_surface.create_extrusion_surface` 走的是 `IModeler.CreateExtrusionSurface`，
      ★ 而那一族的返回值**跨次都会变**（**事实 40**）⇒ 拿它当前置**不可靠**。
      ★ 改用 `sw_surface_features.create_extruded_surface_report`（★ 走 `FeatureExtruRefSurface3`，
      **特征级、已真机验证**，判据 = 特征树增量）。
    """
    P.start_sketch(doc, plane_name="Front Plane")
    sp.sketch_3point_corner_rectangle(doc, -20, -10, 20, -10, 20, 10)
    P.end_sketch(doc)
    return sf.create_extruded_surface_report(doc, 30.0)


def _make_solid(doc):
    """★ 建一个**实体**当前置（★ 马上用于“删除面 / 替换面”）。

    ★★ 2026-10-03（轮 474）**为什么要换前置** ——
      上一轮这两条用的是“拉伸**曲面**”的面，而它们都回 `树 7→7 无新增`。
      ★ 而官方语义上：`InsertDeleteFace2` 是“删除选中的面”、
      `InsertFeatureReplaceFace` 是“把选中的面**替换成**另一些面”
      ⇒ ★ 它们要的是**实体的面**（★ 而拉伸曲面只有 4 个开放边界面）。
      ★ 故改用 `sw_part.extrude_boss`（★ 已验证的实体拉伸）。
    """
    P.start_sketch(doc, plane_name="Front Plane")
    sp.sketch_3point_corner_rectangle(doc, -20, -10, 20, -10, 20, 10)
    P.end_sketch(doc)
    for cand in ("\u8349\u56fe1", "Sketch1"):
        try:
            r = P.extrude_boss(doc, cand, 0.02)
            if r:
                return r
        except Exception:  # noqa: BLE001
            continue
    return None


def _case_offset(doc):
    _make_surface(doc)
    fs = _faces(doc)
    if fs:
        _select(fs[0], mark=0)
    return M.insert_offset_surface(doc, 5.0, False)


def _case_ruled(doc):
    _make_surface(doc)
    es = _edges(doc)
    if es:
        #: ★ 官方 Remarks：边要按 **mark = 4**
        _select(es[0], mark=4)
    return M.insert_ruled_surface(doc, 0, 10.0, trim_and_sew=True)


def _case_delete(doc):
    _make_solid(doc)
    fs = _faces(doc)
    if fs:
        _select(fs[0], mark=0)
    return M.insert_delete_face(doc, 0)


def _case_replace(doc):
    #: ★ 先建**实体**（★ 替换面的语义对象），再取它的两个面
    _make_solid(doc)
    fs = _faces(doc)
    if len(fs) >= 2:
        _select(fs[0], mark=1)
        _select(fs[1], mark=2, append=True)
    return M.insert_replace_face(doc)


def main() -> int:
    sw, _ = c.connect_solidworks(wait_seconds=30)
    _SW[0] = sw
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "B6-a 曲面特征第一组 5 条逐个真机跑（specs/201-toolbar-gaps）",
        "judge": "特征树叶子名增量（★ 3/5 的官方返回是 void，返回值单独不可信）",
        "items": [],
    }
    ev["items"].append(_one(sw, "平面区域", _case_planar))
    ev["items"].append(_one(sw, "等距曲面", _case_offset))
    ev["items"].append(_one(sw, "直纹曲面", _case_ruled))
    ev["items"].append(_one(sw, "删除面", _case_delete))
    ev["items"].append(_one(sw, "替换面", _case_replace))
    ev["passed"] = sum(1 for i in ev["items"] if i.get("verdict") == "能")
    ev["total"] = len(ev["items"])
    p = R / "output" / "b6a-surface-edit-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("  \u8bda\u5b9e %s / %s" % (ev["passed"], ev["total"]))
    for i in ev["items"]:
        print(
            "  %-10s %-4s %-28s %s"
            % (
                i.get("zh"),
                i.get("verdict"),
                i.get("verified_by") or "",
                (i.get("err") or "")[:46],
            )
        )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
