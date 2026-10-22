"""★ 真机试：**曲面扫描**（`CreateDefinition(swFmRefSurface = 62)`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_sweep_surface.py
# 定位:   ★ 2026-10-03（轮 486）★ 给 `scripts/sw_sweep.create_sweep_surface_report` 留
#           真机证据。
#
#   ★★ **为什么这条路**（★ 一轮前已核过两源）：
#     · 台账给的是 `InsertProtrusionSwept4(Surface)` —— ★ 而
#       `IModelDoc2.InsertSweepRefSurface` 与 `…RefSurface2` **两个都标 Obsolete**，
#       ★ 且继任者指向 `IFeatureManager::InsertProtrusionSwept3`（★ **实体**那族）⚠
#     · ★ 而官方 `CreateDefinition.md` 的**合法常量表**里有一条逐字是
#       「**`swFmRefSurface` (surface sweep)**」，★ 反射转储给出 **`swFmRefSurface = 62`**
#       ⇒ ★★ **故正解是 `CreateDefinition(62)` → `ISweepFeatureData` → `CreateFeature`** ✓
#
#   ★ 前置（★ 官方专文给的 mark，与本仓 `sw_loft` 注释里那张表同源）：
#     **轮廓 mark = 1** · **路径 mark = 4**
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: `c:\swapi\types\IFeatureManager\CreateDefinition.md`（★ `swFmRefSurface` (su
#           rface sweep)）·
#   `D:\AI\SW\_raw\enum_values_sldworks.txt`（`swFmRefSurface = 62`）·
#   `c:\swapi\types\IModelDoc2\InsertSweepRefSurface{,2}.md`（★ 两条 Obsolete 行）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 与本仓 `create_sweep_report` 同口径 —— 事实 242）：
#   **特征树多了新特征** **且** **类型名 = `Sweep`**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_sweep as S  # noqa: E402


def _mark(obj, mark):
    """★ 按**对象**选并打 mark（★ 事实 32：实体没名字）⇒ 回来读计数。"""
    try:
        c.get_com_member(obj, "Select4", False, P._empty_callout())
        sel = c.get_com_member(
            c.get_com_member(_SW[0], "SelectionManager"), "GetSelectedObjectCount2", -1
        )
        return True
    except Exception:  # noqa: BLE001
        return False


_SW = [None]


def main() -> int:
    sw, _ = c.connect_solidworks(wait_seconds=30)
    _SW[0] = sw
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u66f2\u9762\u626b\u63cf\uff1aCreateDefinition(swFmRefSurface=62) \u771f\u673a\u8bd5",
        "judge": "\u7279\u5f81\u6811\u589e\u91cf **\u4e14** \u7c7b\u578b\u540d = Sweep\uff08\u4e8b\u5b9e 242\uff09",
        "classify": "auto",
        "steps": [],
    }
    doc = c.new_document(sw, "part")
    try:
        #: ① 轮廓：在**上视基准面**（XY · **Z=0**）画一个**圆**（★ 扫描最标准的轮廓）
        #: ★★★ 2026-10-03（轮 487）**换成圆，并把两个草图都安排成"路径起点在轮廓平面上"*
        #: * ——
        #:   ★ 官方逐字（`…\Sweep Features and SweepFeatureData Objects.md`）：
        #: > 「the **start point of the path must lie on the plane of the profile**」（1
        #:  方向扫描）
        #:   ★★ 而★ 轮廓在上视面（Z=0）⇒ ★ **路径的起点必须 Z=0** ⇒
        #:     路径画在**前视面**（XZ · Y=0）上、**从 (0,0) 沿 X** ⇒ 起点 (0,0,0) 的 Z=0 ✓
        P.start_sketch(doc, plane_name="Top Plane")
        c.get_com_member(
            c.get_com_member(doc, "SketchManager"),
            "CreateCircleByRadius",
            0.0,
            0.0,
            0.0,
            5.0 / 1000.0,
        )
        P.end_sketch(doc)
        ev["steps"].append({"step": "profile_sketch", "tree": P.feature_names(doc)})

        #: ② 路径：在右视基准面画一条直线（★ 起点落在轮廓平面上 —— 官方约束）
        #: ★★★ 2026-10-03（轮 486）**先清选区再开第二个草图** ——
        #:   ⚠ 真机第一次跑：`profile_sketch` 建出了 `草图1`，而 `path_sketch` 那一步
        #:     **树里没有「草图2」** ⇒ ★ 第二个草图**根本没建成** ⚠
        #: ★ 最可能的原因：★ `end_sketch` 之后**上一次的选区还在** ⇒ `start_sketch` 选不
        #: 中基准面。
        #:   ⇒ ★ 故这里**显式清一次**、并把**开草图前后的选区数**记进证据（★ 不猜）✓
        for _lbl in ("path_sketch",):
            try:
                c.get_com_member(doc, "ClearSelection2", True)
            except Exception:  # noqa: BLE001
                pass
        try:
            ev["sel_before_path_sketch"] = int(
                c.get_com_member(
                    c.get_com_member(doc, "SelectionManager"),
                    "GetSelectedObjectCount2",
                    -1,
                )
                or 0
            )
        except Exception:  # noqa: BLE001
            ev["sel_before_path_sketch"] = None
        P.start_sketch(doc, plane_name="Front Plane")
        c.get_com_member(
            c.get_com_member(doc, "SketchManager"),
            "CreateLine",
            0.0,
            0.0,
            0.0,
            40.0,
            0.0,
            0.0,
        )
        P.end_sketch(doc)
        ev["steps"].append({"step": "path_sketch", "tree": P.feature_names(doc)})

        #: ③ ★ 选 **轮廓 mark=1** + **路径 mark=4**（★ 官方专文给的 mark）
        #: ★★★★★ 2026-10-03（轮 487）**改用 `SelectByID2`（`sw_part._select_by_id`）** —
        #: —
        #:   ★★ 真因（★ 前三版的 `sel_by_mark` 已经把线索给全了）：
        #:     `sw_part._select_com_object` 的实现是
        #:     ```
        #:     for method_name in ("Select2", "Select4"):
        #:         if method_name == "Select2":  method(append, mark)      # ★ 带 mark
        #: elif bool(method(append, _empty_callout())): ...        # ★★ **Select4 没有 m
        #: ark** ⚠
        #:     ```
        #: ⇒ ★★ **若 `Select2(append, mark)` 失败而 `Select4` 成功 ⇒ 那一次「没有 mark」
        #: ** ⚠
        #: ⇒ ★ 那正是真机 `{1:1, 4:0}` 的形态（★ 轮廓进了，★ 而路径那次走了 `Select4`）
        #: 。
        #:   ★★★ 而**特征是有名字的**（★ **事实 32**：「按名字选**只对特征成立**」）
        #:     ⇒ ★ 故正解是官方的 **`SelectByID2(名, "SKETCH", …, mark)`** ✓
        #:   ★ 官方专文给的 mark（★ `…\Sweep Features and SweepFeatureData Objects.md`）：
        #:     **草图轮廓 = 1** · **路径 = 4** · 引导线 = 2 · 方向向量 = 128
        ext = c.get_com_member(doc, "Extension")
        picked = {}
        for cand, mark, label in (
            ("\u8349\u56fe1", 1, "profile"),
            ("\u8349\u56fe2", 4, "path"),
        ):
            for name in P._get_sketch_name_candidates(cand):
                try:
                    ok = P._select_by_id(
                        ext, name, "SKETCH", append=bool(picked), mark=mark
                    )
                except Exception:  # noqa: BLE001
                    ok = False
                if ok:
                    picked[label] = name
                    break
        ev["picked"] = picked
        try:
            sel = c.get_com_member(
                c.get_com_member(doc, "SelectionManager"), "GetSelectedObjectCount2", -1
            )
            ev["sel_total"] = int(sel or 0)
        except Exception:  # noqa: BLE001
            ev["sel_total"] = None
        #: ★ 逐 mark 回读（★ 那才是判据 —— 事实 8）
        per = {}
        for m in (1, 4):
            try:
                per[m] = int(
                    c.get_com_member(
                        c.get_com_member(doc, "SelectionManager"),
                        "GetSelectedObjectCount2",
                        m,
                    )
                )
            except Exception:  # noqa: BLE001
                per[m] = -1
        ev["sel_by_mark"] = per

        #: ④ 调本仓的曲面扫描
        ev["result"] = S.create_sweep_surface_report(doc)
    except Exception as exc:  # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            t = str(c.get_com_member(doc, "GetTitle") or "")
            if t:
                c.get_com_member(sw, "CloseDoc", t)
        except Exception:  # noqa: BLE001
            pass

    p = R / "output" / "sweep-surface-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    r = ev.get("result") or {}
    print("  \u5224\u636e\uff1a**%s**" % ("\u6210" if r.get("ok") else "\u4e0d\u6210"))
    print(
        "  \u9009\u533a\uff1a%s  \u9010mark\uff1a%s"
        % (ev.get("picked"), ev.get("sel_by_mark"))
    )
    for k in (
        "stage",
        "error",
        "feature_name",
        "new_features",
        "type_name",
        "access_selections",
        "sw_fm_const",
    ):
        if r.get(k) is not None:
            print("  %-20s %s" % (k, str(r[k])[:150]))
    if ev.get("err"):
        print("  err=%s" % str(ev["err"])[:180])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
