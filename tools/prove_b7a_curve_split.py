"""★ B7-a 真机探针：分割线（投影/轮廓）/ 通过参考点的曲线 / 配合参考。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_b7a_curve_split.py
# 定位:   ★ 2026-10-03（轮 481）★ 给 `scripts/sw_curve_and_split.py` 留真机证据。
#
#   ★ 结构照抄**已被真机验证过的**骨架（`tools/prove_b6a_surface_edit.py`）：
#     · `sw, _ = connect_solidworks(wait_seconds=30)`（★ 它回元组）
#     · **每个用例一个新文档** ⇒ 失败不拖累后续
#     · 用本仓包装（`P.start_sketch` / `P.extrude_boss` / `P.feature_names`）
#     · **判据 = 特征树叶子名增量**（★ 轮 473 的教训：判据函数必须用本仓验证过的那个）
#
#   ★★ **前置（★ 三条各不相同）**：
#     · **通过参考点的曲线** ⇒ ★ **零前置**（★ 只要三个点）⇒ 最该先试 ✓
#     · **分割线（投影）** ⇒ 要一个**草图**当投影工具 + 要切的面 ⇒ 先建实体、在面上开草图
#     · **分割线（轮廓）** ⇒ 要选**面** ⇒ 先建实体 + 选面
#     · **配合参考** ⇒ 要一个 **`IEntity`**（★ 实体没名字 ⇒ 按对象选，事实 32）
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: 见 `scripts/sw_curve_and_split.py` 的模块头（三源逐条）。
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
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_curve_and_split as M  # noqa: E402

#: ★ 中转：COM 实体放这里（★ **不进 JSON**）
_LAST_ENTITY = []
import scripts.sw_sketch_primitives as SP  # noqa: E402


def _solid(doc, depth=0.02):
    """★ 建实体（★ 判据 = 树里真出现"凸台/拉伸" —— ★ 别信 `extrude_boss` 的 bool，轮 480 的教训）。"""
    before = P.feature_names(doc) or []
    P.start_sketch(doc, plane_name="Front Plane")
    SP.sketch_3point_corner_rectangle(doc, -20, -10, 20, -10, 20, 10)
    P.end_sketch(doc)
    rets = []
    for cand in ("草图1", "Sketch1"):
        try:
            r = P.extrude_boss(doc, cand, depth)
            rets.append(repr(r)[:40])
            if r:
                break
        except Exception as exc:  # noqa: BLE001
            rets.append("%s: %s" % (type(exc).__name__, str(exc)[:60]))
    after = P.feature_names(doc) or []
    added = [n for n in after if n not in before]
    return any(("凸台" in n) or ("拉伸" in n) for n in added), {
        "returns": rets,
        "added": added,
    }


def _pick_face(doc, idx=0, mark=0):
    """★ 按**对象**选一个面（★ 事实 32：面没有名字）⇒ 回来选中的计数。"""
    try:
        bs = list(C.get_com_member(doc, "GetBodies2", -1, True) or [])
        if not bs:
            return False, "无 body"
        fs = list(C.get_com_member(bs[0], "GetFaces") or [])
        if len(fs) <= idx:
            return False, "面不够"
        try:
            C.get_com_member(doc, "ClearSelection2", True)
        except Exception:  # noqa: BLE001
            pass
        ok = bool(P._select_com_object(fs[idx], append=False, mark=int(mark)))
        try:
            n = int(
                C.get_com_member(
                    C.get_com_member(doc, "SelectionManager"),
                    "GetSelectedObjectCount2",
                    -1,
                )
                or 0
            )
        except Exception:  # noqa: BLE001
            n = -1
        #: ★★ 2026-10-03（轮 481）**不要把 COM 对象放进结果** ——
        #:   ⚠ 我第一版这里写了 `"entity": fs[idx]` ⇒ ★ 最后的 `json.dumps` 报
        #:     `TypeError: Object of type CDispatch is not JSON serializable`
        #:     ★ 而**4 个用例其实都跑完了**（★ 只是写文件时炸）⚠
        #:   ★ 本仓的纪律就是这条：★ **工具层要把 COM 对象挡在里面**
        #: （★ 见 `solidworks_resolve_entity` 的注释：「★ 只回 JSON —— 把 COM 对象挡在里
        #: 面」）
        #:   ⇒ ★ 正解：★ 实体走**模块级中转**（`_LAST_ENTITY`），★ **不进 JSON** ✓
        _LAST_ENTITY.append(fs[idx])
        return ok, {"face": idx, "mark": int(mark), "sel": n, "n_faces": len(fs)}
    except Exception as exc:  # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:70])


def _one(sw, zh, fn):
    row = {"zh": zh, "verdict": "不能"}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        r = fn(doc)
        row.update(r if isinstance(r, dict) else {"returned": str(r)})
        row["verdict"] = "能" if row.get("ok") else "不能"
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def _case_curve(doc):
    """★ 通过参考点的曲线：★ **零前置**（★ 只要 3 个点）。"""
    return M.insert_curve_through_points(
        doc, [[0.0, 0.0, 0.0], [20.0, 0.0, 0.0], [40.0, 10.0, 0.0]]
    )


def _case_split_project(doc):
    """★ 分割线（投影）：★ 先用本仓包装把**实体 + 面上的草图**建好，再调。"""
    built, info = _solid(doc)
    #: ★ 在**体的一个面上**开草图（★ 投影分割线需要"要投影的草图"）
    ok, sel = _pick_face(doc, 0, 0)
    try:
        P.start_sketch(doc)
        SP.sketch_3point_corner_rectangle(doc, -5, -5, 5, -5, 5, 5)
        P.end_sketch(doc)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "op": "split_line_project",
            "solid": built,
            "err": "开草图失败：%s" % str(exc)[:110],
        }
    r = M.insert_split_line_project(doc, True, False)
    r["solid"] = built
    r["solid_info"] = info
    r["face_pick"] = sel if isinstance(sel, dict) else str(sel)
    return r


def _case_split_sil(doc):
    """★ 分割线（轮廓）：★ 先建实体 + 选一个面。"""
    built, info = _solid(doc)
    ok, sel = _pick_face(doc, 0, 0)
    r = M.insert_split_line_silhouette(doc)
    r["solid"] = built
    r["solid_info"] = info
    r["face_pick"] = sel if isinstance(sel, dict) else str(sel)
    return r


def _case_mate(doc):
    """★ 配合参考：★ 先建实体 + 选一个面当 `IEntity`。

    ⚠★ 2026-10-03（轮 481）**上一版把真错因吞了** —— 我写了个 `try/except` 循环"试两个枚举值"，
      结果两条都抛、★ 而我只回了一句 `"两次都抛了"` ⇒ ★ **真错因一个字都没留下** ⚠
      ⇒ ★ 那是本仓明令禁止的形态（★ 事实 53 一族：**"看起来试过了"不等于留了证据**）。
    ★ 现在：★ **不吞** —— 让异常直接冒到 `_one` 的 `err` 字段（★ 那才会被写进证据）✓
    """
    built, info = _solid(doc)
    ok, sel = _pick_face(doc, 0, 0)
    ent = _LAST_ENTITY[-1] if _LAST_ENTITY else None
    #: ★ `swMateReferenceType_e` 的成员名要**现查**（★ 本探针先用官方常见的 `PLANE`）
    r = M.insert_mate_reference(doc, "MCP_MateRef", ent, 0, 0, False)
    r["solid"] = built
    r["solid_info"] = info
    r["face_pick"] = sel if isinstance(sel, dict) else str(sel)
    r["entity_present"] = ent is not None
    return r


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "B7-a 分割线/曲线/配合参考逐个真机跑（specs/201-toolbar-gaps）",
        "judge": "特征树叶子名增量（sw_part.feature_names）",
        "items": [],
    }
    ev["items"].append(_one(sw, "通过参考点的曲线", _case_curve))
    ev["items"].append(_one(sw, "分割线（投影）", _case_split_project))
    ev["items"].append(_one(sw, "分割线（轮廓）", _case_split_sil))
    ev["items"].append(_one(sw, "配合参考", _case_mate))
    ev["passed"] = sum(1 for i in ev["items"] if i.get("verdict") == "能")
    ev["total"] = len(ev["items"])
    p = R / "output" / "b7a-curve-split-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u8bda\u5b9e %s / %s" % (ev["passed"], ev["total"]))
    for i in ev["items"]:
        print(
            "  %-16s %-4s %-30s \u65b0\u589e=%s"
            % (
                i.get("zh"),
                i.get("verdict"),
                i.get("verified_by") or "",
                i.get("new_features"),
            )
        )
        if i.get("err"):
            print("        err=%s" % str(i["err"])[:94])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
