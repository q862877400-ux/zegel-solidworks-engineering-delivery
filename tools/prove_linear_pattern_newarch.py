"""★ 真机试：线性阵列的**新架构**（`CreateDefinition` + `ILinearPatternFeatureData`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_linear_pattern_newarch.py
# 定位:   ★ 2026-10-03（轮 484）★ 回答一个**悬了很久的问题**：
#   **`sw_pattern.py`（线性阵列的新架构）到底能不能真机跑通？**
#
#   ★★ **为什么值得单独问**（★ 三层证据指向同一处）：
# · 轮 482 我核 `specs/201-toolbar-gaps` 的 X 段时，看到旧入口 `FeatureLinearPattern3/4/
# 5`
#       全标 `Obsolete`、继任者写「`CreateFeature` + `ILinearPatternFeatureData`」，
#       ★ 而本仓**有** `scripts/sw_pattern.py`（428 行）⇒ ★ 我当时判「不是后端到不了」⚠
# · 轮 483 复核证据时发现：`output/linear-pattern-*-evidence.json` **verdict 都是 `fail`
# **
#       ⇒ ★ 旧入口**确实没建成** ✓
#     · 而 `sw_pattern.py` 的**模块头**写着：它所有装配函数一律走
#       **`AccessSelections(Object, Object)`** —— ★★ **而 `AccessSelections` 正是「指针族」**
#       （★ **事实 47**：pywin32 下报 **`0x80010105`**）⚠
#     ⇒ ★★★ **故本轮直接试**：★ 若它也报 `0x80010105`，那「线性阵列族」的归因**其实成立**，
# ★ 只是**理由不同**（★ 不是"旧入口废弃"，★ 而是**新旧两条路都要 `AccessSelections`**）
# 。
#
#   ★★★★ **顺带更正一处**：`sw_pattern.py` 注释里引用的常量名
#     `swFmLinearPattern` / `swFmCurveDrivenPattern` **在反射转储里都不存在** ⚠
#     —— ★ 真名是 **`swFmLPattern = 6`** / **`swFmCurvePattern = 103`**
#     （★ 见 `_raw/enum_values_sldworks.txt`）。★ 本探针**用真名** ✓
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: `C:\swapi\types\IFeatureManager\FeatureLinearPattern5.md`（Obsolete 行）·
#   `C:\swapi\types\ILinearPatternFeatureData\_overview.md` ·
#   `D:\AI\SW\_raw\enum_values_sldworks.txt`（`swFmLPattern = 6`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **三判据并列**（★ 与既有 `linear-pattern-geometry-evidence.json` 同口径）：
#   ① 特征树名字增量 ② 体数 ③ 包围盒。★ 并**单独记下 `AccessSelections` 那一步的结果** ✓

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
from scripts import sw_pattern as SP  # noqa: E402
import scripts.sw_sketch_primitives as SPK  # noqa: E402

#: ★ 真名（★ 来自 `_raw/enum_values_sldworks.txt`，**不是**注释里那个 `swFmLinearPattern
#: `）
SW_FM_LPATTERN = 6
SW_FM_CURVE_PATTERN = 103


def _geom(model):
    """★ 几何判据：**体数 + 第一个体的包围盒**（★ 与既有证据同口径）。"""
    try:
        bs = list(C.get_com_member(model, "GetBodies2", -1, True) or [])
        out = {"bodies": len(bs)}
        if bs:
            bb = C.get_com_member(bs[0], "GetBodyBox")
            out["box"] = [round(float(x), 3) for x in (bb or [])]
        return out
    except Exception as exc:  # noqa: BLE001
        return {"err": "%s: %s" % (type(exc).__name__, str(exc)[:60])}


def _pick_seed(model):
    """★ 选**种子特征**（★ 一个实体特征；★ 按对象选 —— 事实 32：特征可按名选，★ 而本探针走对象）。"""
    try:
        fm = C.get_com_member(model, "FeatureManager")
        n = int(C.get_com_member(fm, "GetFeatureCount", True) or 0)
        for i in range(n):
            f = C.get_com_member(fm, "FeatureByPositionReverse", i)
            if f is None:
                continue
            nm = str(C.get_com_member(f, "Name") or "")
            if "\u51f8\u53f0" in nm or "\u62c9\u4f38" in nm:
                if P._select_com_object(f, append=False, mark=0):
                    return nm
        return None
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u7ebf\u6027\u9635\u5217\u65b0\u67b6\u6784\uff08CreateDefinition + ILinearPatternFeatureData\uff09\u771f\u673a\u8bd5",
        "judge": "\u4e09\u5224\u636e\u5e76\u5217\uff1a\u7279\u5f81\u6811\u540d\u589e\u91cf / \u4f53\u6570 / \u5305\u56f4\u76d2",
        "swFmLPattern": SW_FM_LPATTERN,
        "steps": [],
    }

    doc = C.new_document(sw, "part")
    try:
        #: ① 建实体（★ 判据是树里出现"凸台/拉伸"，★ 别信 bool —— 轮 480 的教训）
        before = P.feature_names(doc) or []
        P.start_sketch(doc, plane_name="Front Plane")
        SPK.sketch_3point_corner_rectangle(doc, -8, -8, 8, -8, 8, 8)
        P.end_sketch(doc)
        for cand in ("\u8349\u56fe1", "Sketch1"):
            try:
                P.extrude_boss(doc, cand, 0.02)
                break
            except Exception:  # noqa: BLE001
                continue
        after = P.feature_names(doc) or []
        ev["steps"].append(
            {"step": "solid", "added": [n for n in after if n not in before]}
        )
        ev["before"] = {"tree": len(after), "geom": _geom(doc)}

        #: ② 选种子特征
        ev["seed"] = _pick_seed(doc)

        #: ③ **取 FeatureData**（★ 用真名 `swFmLPattern = 6`）
        fm = C.get_com_member(doc, "FeatureManager")
        data = None
        try:
            data = C.get_com_member(fm, "CreateDefinition", SW_FM_LPATTERN)
            ev["create_definition"] = {
                "ok": data is not None,
                "type": type(data).__name__,
            }
        except Exception as exc:  # noqa: BLE001
            ev["create_definition"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }

        #: ④ **装配** —— ★★ **这一步里会走 `AccessSelections`**（★ 关键观察点）
        if data is not None:
            try:
                r = SP.configure_linear_pattern(
                    data, doc, d1_spacing=0.015, d1_total_instances=3
                )
                ev["configure"] = {"ok": True, "returned": str(r)[:220]}
            except Exception as exc:  # noqa: BLE001
                ev["configure"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                    "err_code": getattr(exc, "args", (None,))[0],
                }

            #: ⑤ 建特征
            try:
                feat = C.get_com_member(fm, "CreateFeature", data)
                ev["create_feature"] = {
                    "ok": feat is not None,
                    "type": type(feat).__name__,
                }
            except Exception as exc:  # noqa: BLE001
                ev["create_feature"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                }

        after2 = P.feature_names(doc) or []
        ev["after"] = {
            "tree": len(after2),
            "geom": _geom(doc),
            "new": [n for n in after2 if n not in after],
        }
        ev["geom_changed"] = ev["after"]["geom"] != ev["before"]["geom"]
        ev["verdict"] = "pass" if ev["geom_changed"] else "fail"
    except Exception as exc:  # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        ev["verdict"] = "fail"
    finally:
        try:
            t = str(C.get_com_member(doc, "GetTitle") or "")
            if t:
                C.get_com_member(sw, "CloseDoc", t)
        except Exception:  # noqa: BLE001
            pass

    p = R / "output" / "linear-pattern-newarch-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u636e\uff1a**%s**" % ev.get("verdict"))
    for k in ("create_definition", "configure", "create_feature"):
        if k in ev:
            print("  %-20s %s" % (k, json.dumps(ev[k], ensure_ascii=False)[:170]))
    print(
        "  \u51e0\u4f55\u53d8\u4e86\uff1a%s  before=%s after=%s"
        % (
            ev.get("geom_changed"),
            ev.get("before", {}).get("geom"),
            ev.get("after", {}).get("geom"),
        )
    )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
