"""★ 真机试：**曲面扫描**（`CreateDefinition(swFmRefSurface = 62)`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_sweep_surface.py
# 定位:   ★ 2026-10-03（轮 486）★ 给 `scripts/sw_sweep.create_sweep_surface_report` 留真机证据。
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
# 官方依据: `C:\swapi\types\IFeatureManager\CreateDefinition.md`（★ `swFmRefSurface` (surface sweep)）·
#   `D:\AI\SW\_raw\enum_values_sldworks.txt`（`swFmRefSurface = 62`）·
#   `C:\swapi\types\IModelDoc2\InsertSweepRefSurface{,2}.md`（★ 两条 Obsolete 行）
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
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                  # noqa: E402
from scripts import sw_part as P                                     # noqa: E402
from scripts import sw_sweep as S                                    # noqa: E402
import scripts.sw_sketch_primitives as SPK                           # noqa: E402


def _mark(obj, mark):
    """★ 按**对象**选并打 mark（★ 事实 32：实体没名字）⇒ 回来读计数。"""
    try:
        C.get_com_member(obj, "Select4", False, P._empty_callout())
        sel = C.get_com_member(C.get_com_member(_SW[0], "SelectionManager"), "GetSelectedObjectCount2", -1)
        return True
    except Exception:                                                    # noqa: BLE001
        return False


_SW = [None]


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    _SW[0] = sw
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u66f2\u9762\u626b\u63cf\uff1aCreateDefinition(swFmRefSurface=62) \u771f\u673a\u8bd5",
          "judge": "\u7279\u5f81\u6811\u589e\u91cf **\u4e14** \u7c7b\u578b\u540d = Sweep\uff08\u4e8b\u5b9e 242\uff09",
          "classify": "auto",
          "steps": []}
    doc = C.new_document(sw, "part")
    try:
        #: ① 轮廓：在前视基准面画一个圆（★ 扫描轮廓）
        P.start_sketch(doc, plane_name="Front Plane")
        SPK.sketch_3point_corner_rectangle(doc, -5, -5, 5, -5, 5, 5)
        P.end_sketch(doc)
        ev["steps"].append({"step": "profile_sketch", "tree": P.feature_names(doc)})

        #: ② 路径：在右视基准面画一条直线（★ 起点落在轮廓平面上 —— 官方约束）
        #: ★★★ 2026-10-03（轮 486）**先清选区再开第二个草图** ——
        #:   ⚠ 真机第一次跑：`profile_sketch` 建出了 `草图1`，而 `path_sketch` 那一步
        #:     **树里没有「草图2」** ⇒ ★ 第二个草图**根本没建成** ⚠
        #:   ★ 最可能的原因：★ `end_sketch` 之后**上一次的选区还在** ⇒ `start_sketch` 选不中基准面。
        #:   ⇒ ★ 故这里**显式清一次**、并把**开草图前后的选区数**记进证据（★ 不猜）✓
        for _lbl in ("path_sketch",):
            try:
                C.get_com_member(doc, "ClearSelection2", True)
            except Exception:                                            # noqa: BLE001
                pass
        try:
            ev["sel_before_path_sketch"] = int(C.get_com_member(
                C.get_com_member(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                # noqa: BLE001
            ev["sel_before_path_sketch"] = None
        P.start_sketch(doc, plane_name="Right Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateLine",
                         0.0, 0.0, 0.0, 0.0, 40.0, 0.0)
        P.end_sketch(doc)
        ev["steps"].append({"step": "path_sketch", "tree": P.feature_names(doc)})

        #: ③ ★ 选 **轮廓 mark=1** + **路径 mark=4**（★ 官方专文给的 mark）
        #: ★★★★ 2026-10-03（轮 486）**两个坑都在这一步，而第二个更隐蔽** ——
        #:   ① ⚠ 我第一版写 `get_com_member(fm, "FeatureName", name)` —— ★ 而
        #:      **`FeatureName` 是 `IFeatureManager` 上的属性**（取值，不是取特征）；
        #:      ★★ **真名是 `IModelDoc2.FeatureByName(name)`**（**方法**）⚠ 两个名字极像。
        #:   ② ⚠ 第二版改用本仓的 `_select_sketch_feature_by_name` ⇒ ★ 真机 `mark1=0 · mark4=1`
        #:      —— ★★ 因为**它内部用 `append=False`**（见 `sw_part.py` L350）⇒
        #:      **第二次调用把第一次的挤掉了** ⚠
        #:   ⇒ ★ 正解：**用 `FeatureByName` 拿对象** ⇒ **用 `append=True` 逐个追加** ✓
        picked = {}
        for cand, mark, label in (("\u8349\u56fe1", 1, "profile"), ("\u8349\u56fe2", 4, "path")):
            for name in P._get_sketch_name_candidates(cand):
                try:
                    feat = C.get_com_member(doc, "FeatureByName", name)
                except Exception:                                        # noqa: BLE001
                    feat = None
                if feat is not None and P._select_com_object(feat, append=True, mark=mark):
                    picked[label] = name
                    break
        ev["picked"] = picked
        try:
            sel = C.get_com_member(C.get_com_member(doc, "SelectionManager"), "GetSelectedObjectCount2", -1)
            ev["sel_total"] = int(sel or 0)
        except Exception:                                                # noqa: BLE001
            ev["sel_total"] = None
        #: ★ 逐 mark 回读（★ 那才是判据 —— 事实 8）
        per = {}
        for m in (1, 4):
            try:
                per[m] = int(C.get_com_member(C.get_com_member(doc, "SelectionManager"),
                                              "GetSelectedObjectCount2", m))
            except Exception:                                            # noqa: BLE001
                per[m] = -1
        ev["sel_by_mark"] = per

        #: ④ 调本仓的曲面扫描
        ev["result"] = S.create_sweep_surface_report(doc)
    except Exception as exc:                                             # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            t = str(C.get_com_member(doc, "GetTitle") or "")
            if t:
                C.get_com_member(sw, "CloseDoc", t)
        except Exception:                                                # noqa: BLE001
            pass

    p = R / "output" / "sweep-surface-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    r = ev.get("result") or {}
    print("  \u5224\u636e\uff1a**%s**" % ("\u6210" if r.get("ok") else "\u4e0d\u6210"))
    print("  \u9009\u533a\uff1a%s  \u9010mark\uff1a%s" % (ev.get("picked"), ev.get("sel_by_mark")))
    for k in ("stage", "error", "feature_name", "new_features", "type_name", "access_selections", "sw_fm_const"):
        if r.get(k) is not None:
            print("  %-20s %s" % (k, str(r[k])[:150]))
    if ev.get("err"):
        print("  err=%s" % str(ev["err"])[:180])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
