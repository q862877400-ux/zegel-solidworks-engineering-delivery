"""★ A/B 对比：同一套选区下，**实体扫描（17）** vs **曲面扫描（62）**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_sweep_ab.py
# 定位:   ★ 2026-10-03（轮 488）★ **一次只改一个变量**的对比实验 ——
#   回答：**曲面扫描（`CreateDefinition(62)`）建不成，是因为"我的前置不对"，
#   还是因为"它本身对 `AccessSelections` 是硬依赖"？**
#
#   ★★ 线索来自两处，而它们**互相矛盾**：
#     · `scripts/sw_sweep.py` 的注释（★ 轮 315 真机定的）：
#       > ★★ **即使这一步（`AccessSelections`）报错，特征仍然建成了**（`扫描1` · type=`Sweep`）
#       > ⇒ ★ **所以它不是必需的**
#       ⇒ ★ 而**那条说的是 `swFmSweep = 17`（实体扫描）** ⚠
#     · 轮 487 真机（曲面扫描，62）：`access_selections = 0x80010105` **且 `new_features = []`** ⚠
#       ⇒ ★★ **即：62 这一路，报错就真的没建成** ✓（★ 假设）
#
#   ★ 做法：★ **同一份几何**（轮廓 = 上视面的圆 · 路径 = 前视面从原点沿 X 的线）
#     + ★ **同一套选区**（★ 用 `SelectByID2` 带 mark ⇒ 轮廓 1 / 路径 4，★ 事实 384 的正解）
#     + ★★ **唯一的变量 = `CreateDefinition` 的常量**（17 或 62）。
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: `C:\swapi\types\IFeatureManager\CreateDefinition.md`
#   （★ `swFmSweep` (boss sweep) · ★ `swFmRefSurface` (surface sweep)）·
#   `D:\AI\SW\_raw\enum_values_sldworks.txt`（`swFmSweep = 17` · `swFmRefSurface = 62`）·
#   `C:\swapi\docs\Programming with the SOLIDWORKS API\Sweep Features and SweepFeatureData Objects.md`（mark 表）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 事实 242）：**特征树多了新特征** **且** **类型名 = `Sweep`**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                  # noqa: E402
from scripts import sw_part as P                                     # noqa: E402
from scripts import sw_sweep as S                                    # noqa: E402


def _feature_type_name(model, name):
    try:
        fm = C.get_com_member(model, "FeatureManager")
        f = C.get_com_member(model, "FeatureByName", name)
        if f is None:
            return None
        for m in ("GetTypeName2", "GetTypeName"):
            try:
                t = str(C.get_com_member(f, m) or "")
                if t:
                    return t
            except Exception:                                            # noqa: BLE001
                continue
        return None
    except Exception:                                                    # noqa: BLE001
        return None


def _one(sw, const):
    """★ 跑一路：`CreateDefinition(const)` → 设选区 → `CreateFeature`。"""
    row = {"const": const, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: ★ 轮廓：上视面（XY · Z=0）的圆
        P.start_sketch(doc, plane_name="Top Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCircleByRadius",
                         0.0, 0.0, 0.0, 5.0 / 1000.0)
        P.end_sketch(doc)
        #: ★ 路径：前视面（XZ · Y=0）从原点沿 X ⇒ ★ 起点 (0,0,0) 的 Z=0（★ 官方：路径起点须在轮廓平面上）
        try:
            C.get_com_member(doc, "ClearSelection2", True)
        except Exception:                                                # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name="Front Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateLine",
                         0.0, 0.0, 0.0, 40.0, 0.0, 0.0)
        P.end_sketch(doc)
        row["tree_after_sketches"] = list(P.feature_names(doc) or [])

        #: ★ 选区：轮廓 mark=1 + 路径 mark=4（★ 用 `SelectByID2` —— 事实 384 的正解）
        ext = C.get_com_member(doc, "Extension")
        picked = {}
        for cand, mark, label in (("\u8349\u56fe1", 1, "profile"), ("\u8349\u56fe2", 4, "path")):
            for name in P._get_sketch_name_candidates(cand):
                try:
                    ok = P._select_by_id(ext, name, "SKETCH", append=bool(picked), mark=mark)
                except Exception:                                        # noqa: BLE001
                    ok = False
                if ok:
                    picked[label] = name
                    break
        row["picked"] = picked
        per = {}
        for m in (1, 4):
            try:
                per[m] = int(C.get_com_member(C.get_com_member(doc, "SelectionManager"),
                                              "GetSelectedObjectCount2", m))
            except Exception:                                            # noqa: BLE001
                per[m] = -1
        row["sel_by_mark"] = per

        #: ★ 唯一变量：常量
        fm = C.get_com_member(doc, "FeatureManager")
        before = list(P.feature_names(doc) or [])
        data = C.get_com_member(fm, "CreateDefinition", const)
        row["data"] = type(data).__name__ if data is not None else None
        if data is None:
            row["stage"] = "CreateDefinition"
            return row
        access = None
        try:
            access = bool(C.get_com_member(data, "AccessSelections", doc, P._empty_callout()))
        except Exception as exc:                                         # noqa: BLE001
            access = "ERR %s" % str(exc)[:90]
        row["access_selections"] = access
        try:
            feat = C.get_com_member(fm, "CreateFeature", data)
            row["create_feature_type"] = type(feat).__name__ if feat is not None else "None"
        except Exception as exc:                                         # noqa: BLE001
            row["create_feature_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        after = list(P.feature_names(doc) or [])
        new = [n for n in after if n not in before]
        tname = _feature_type_name(doc, new[-1]) if new else None
        row.update({"new_features": new, "type_name": tname,
                    "ok": bool(new) and (tname == "Sweep")})
    except Exception as exc:                                             # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                            # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "A/B\uff1a\u540c\u4e00\u5957\u9009\u533a\u4e0b \u5b9e\u4f53\u626b\u63cf(17) vs \u66f2\u9762\u626b\u63cf(62)",
          "judge": "\u7279\u5f81\u6811\u589e\u91cf **\u4e14** \u7c7b\u578b\u540d = Sweep\uff08\u4e8b\u5b9e 242\uff09",
          "cases": []}
    ev["cases"].append(_one(sw, 17))
    ev["cases"].append(_one(sw, 62))
    p = R / "output" / "sweep-ab-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    for c in ev["cases"]:
        print("  const=%-3s \u5224\u636e=%s  \u9009\u533a=%s  access=%s" % (
            c.get("const"), "\u6210" if c.get("ok") else "\u4e0d\u6210", c.get("sel_by_mark"),
            str(c.get("access_selections"))[:44]))
        print("        \u65b0\u589e=%s \u7c7b\u578b=%s CreateFeature=%s %s" % (
            c.get("new_features"), c.get("type_name"), c.get("create_feature_type"),
            (c.get("create_feature_err") or c.get("err") or "")[:70]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
