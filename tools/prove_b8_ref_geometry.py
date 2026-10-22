"""★ B8 真机探针：基准面 / 坐标系 / 点 / 质心 / 边界框。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_b8_ref_geometry.py
# 定位:   ★ 2026-10-03（轮 479）★ 给 `scripts/sw_ref_geometry.py` 留真机证据。
#
#   ★ 结构照抄**已被真机验证过的**骨架（`tools/prove_b6a_surface_edit.py`）：
#     · `sw, _ = connect_solidworks(wait_seconds=30)`（★ 它回元组）
#     · **每个用例一个新文档** ⇒ 失败不拖累后续
#     · 用本仓包装（`p_.start_sketch` / `p_.extrude_boss` / `sp.*`），**不裸调**
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
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_sketch_primitives as sp  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as p_  # noqa: E402
from scripts import sw_ref_geometry as m_  # noqa: E402


def _solid(doc, plane="Front Plane", pts=(-20, -10, 20, -10, 20, 10), depth=0.02):
    """★ 建一个**实体**当前置（★ 质心/边界框要有几何才有意义）。

    ★★★ 2026-10-03（轮 480）**判据改成"特征树里真出现了实体特征"** ——
      ⚠ 上一版 `return True if p_.extrude_boss(...)` —— ★★ **那个 bool 骗了我**：
        真机证据里两条失败用例的 `tree_after` **只有 `草图1`、没有「凸台-拉伸1」**
        ⇒ ★ **实体根本没建成**，★ 而 `solid_built` 却报了 `True` ⚠
        ⇒ ★★ 于是"基准面/点不成"被记成"前置没选对"，★ **而真因是更底下的实体就没建**。
      ⇒ ★ 现在**以树为准**：★ 出现了 `凸台`（或 `拉伸`）字样的新特征才算成 ✓
        （★ 与事实 8 同一条纪律：**不信返回值，信回读**。）
    :returns: `(bool, dict)` —— 成没成 + 取证用的细节。
    """
    info = {"depth": depth}
    before = p_.feature_names(doc) or []
    p_.start_sketch(doc, plane_name=plane)
    sp.sketch_3point_corner_rectangle(doc, *pts)
    p_.end_sketch(doc)
    info["after_sketch"] = list(p_.feature_names(doc) or [])
    rets = []
    for cand in ("草图1", "Sketch1"):
        try:
            r = p_.extrude_boss(doc, cand, depth)
            rets.append({cand: repr(r)[:60]})
            if r:
                break
        except Exception as exc:  # noqa: BLE001
            rets.append({cand: "%s: %s" % (type(exc).__name__, str(exc)[:80])})
    after = list(p_.feature_names(doc) or [])
    info["extrude_returns"] = rets
    info["after_extrude"] = after
    added = [n for n in after if n not in before]
    info["added"] = added
    #: ★ 判据：新增里要有"凸台/拉伸"字样的**实体特征**（★ 不是"有草图"就算）
    built = any(("凸台" in n) or ("拉伸" in n) for n in added)
    info["built_by_tree"] = built
    return built, info


def _one(sw, zh, fn):
    """★ 每个用例一个新文档（★ 现成骨架）。"""
    row = {"zh": zh, "verdict": "不能"}
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


def _case(zh, needs_solid, fn):
    """★ 包一层：按需先建实体（★ 并把**实体的取证细节**带回来）。"""

    def run(doc):
        if needs_solid:
            built, info = _solid(doc)
            r = fn(doc)
            r["solid_built"] = built
            r["solid_info"] = info  # ★ 取证：extrude 的返回值 + 树的前后
            return r
        return fn(doc)

    run.__name__ = zh
    return _one, run


def _after_pick(doc, idx, mark, fn):
    """★ **先选面（带 mark）⇒ 立刻调 `fn`** ⇒ 把选中情形并进返回值。

    ★★ 为什么"立刻"很要紧：★ 点那条在**诊断脚本里成了**（`new_features: ['点1']`）——
      那次是"建实体 → 选面 → **紧接着**调"；★ 而探针里中间隔了别的步骤 ⇒ **选区被清掉** ⚠
    """
    ok, info = _pick_face(doc, idx, mark)
    r = fn()
    if isinstance(r, dict):
        r["preselect"] = {
            "ok": ok,
            **({"info": info} if isinstance(info, dict) else {"why": info}),
        }
    return r


def _pick_face(doc, idx=0, mark=0):
    """★ 选中实体的第 `idx` 个面（★ 按**对象**选 —— 事实 32：面没有名字）。

    ★★★ 2026-10-03（轮 480）**这个函数是本轮的关键** ——
      · **基准面**：官方 Remarks 逐字给了 mark 表
        （`0 = First reference entity · 1 = Second · 2 = Third`）
        ⇒ ⚠ 而我上一轮**根本没选任何参考实体**就调了 ⇒ `回None=True`（★ 它没对象可回）✓
        ★ 而我上一轮还**写进 `limitations` 说"官方没给那张 mark 表"** —— ★★ **那是错的**，
          表**就在同一条 Remarks 里**（★ 铁律 5 的正确用法是"查到了要写明"，★ 而我当时没读到那一段）⚠
      · **点**：★ 它在**诊断脚本里成了**（`new_features: ['点1']`），★ 那次是
        "**先建实体 → 选一个面 → 立刻调**"；★ 而探针里中间隔了别的步骤 ⇒ ★ **选区被清掉了** ⚠
        ⇒ ★ 故这里**在调用前一刻**再选一次 ✓
    """
    try:
        bs = list(c.get_com_member(doc, "GetBodies2", -1, True) or [])
        if not bs:
            return False, "无 body"
        fs = list(c.get_com_member(bs[0], "GetFaces") or [])
        if len(fs) <= idx:
            return False, "面不够（%d）" % len(fs)
        #: ★ 先清选区（★ 免得上一次的残留把 mark 搞乱）
        try:
            c.get_com_member(doc, "ClearSelection2", True)
        except Exception:  # noqa: BLE001
            pass
        ok = bool(p_._select_com_object(fs[idx], append=False, mark=int(mark)))
        try:
            n = int(
                c.get_com_member(
                    c.get_com_member(doc, "SelectionManager"),
                    "GetSelectedObjectCount2",
                    -1,
                )
                or 0
            )
        except Exception:  # noqa: BLE001
            n = -1
        return ok, {
            "face_index": idx,
            "mark": int(mark),
            "sel_count": n,
            "n_faces": len(fs),
        }
    except Exception as exc:  # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:80])


def main() -> int:
    sw, _ = c.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%m_:%S"),
        "_": "B8 参考几何体 5 条逐个真机跑（specs/201-toolbar-gaps）",
        "judge": "特征树叶子名增量（sw_part.feature_names）",
        "items": [],
    }

    cases = [
        ("质心", True, lambda d: m_.insert_center_of_mass(d)),
        #: ★★★ 2026-10-03（轮 479）**换成员**：台账 T701 给的 `Create3DBoundingBox`
        #: 官方原话是「for a **cut list item in a weldment part**」⇒ ★ **焊件切割清单专
        #: 用**，
        #:   ★ 普通零件上不成是**应然的**。★ 工具栏那个的真名是
        #:   **`IFeatureManager.InsertGlobalBoundingBox2`** ✓
        ("边界框", True, lambda d: m_.insert_global_bounding_box(d, 1, 0, False, False)),
        #: ★★★ 基准面：★★ **必须先按 mark 选参考实体** —— 官方 Remarks 逐字给了表：
        #:   `0 = First reference entity · 1 = Second · 2 = Third`
        #:   ⚠ 我上一轮**根本没选**就调 ⇒ `回None=True`（它没对象可回）
        #:   ⇒ ★ 本轮：选第一个面当**第一参考实体（mark=0）**，用 `Coincident(4)`
        (
            "基准面",
            True,
            lambda d: _after_pick(
                d, 0, 0, lambda: m_.insert_ref_plane(d, 4, 0.0, 0, 0.0, 0, 0.0)
            ),
        ),
        ("坐标系", False, lambda d: m_.insert_coordinate_system(d, False, False, False)),
        #: ★ 点：★ FaceCenter（★ 要有面）⇒ **在调用前一刻再选一次**（★ 诊断里就是这样成
        #: 的）
        (
            "点",
            True,
            lambda d: _after_pick(
                d, 0, 0, lambda: m_.insert_reference_point(d, 4, 0, 0.0, 1)
            ),
        ),
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
        extra = (
            ("  \u6811 %d\u2192%d %s" % (len(tb), len(ta), i.get("new_features")))
            if tb and ta
            else ""
        )
        print(
            "  %-8s %-4s %-28s%s"
            % (i.get("zh"), i.get("verdict"), i.get("verified_by") or "", extra)
        )
        if i.get("err"):
            print("        err=%s" % str(i["err"])[:90])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
