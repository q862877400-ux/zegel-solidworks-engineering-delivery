"""★ 真机：**扫描曲面**走它的**专用方法** `IFeatureManager.InsertSweepSurface2/3`。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_sweep_surface_dedicated.py
# 定位:   ★ 2026-10-03（轮 532）★ 用那把钥匙的**第三次命中**开 T602（扫描曲面）。
#
#   ★★ **钥匙**（事实 410）：★ **官方文档里的每个名词都要落实**。
# ★ 前两次：旋转曲面**成了**（缺 `centerline`）· 加厚与直纹**没成**（那两个词不是关键）
# 。
#
#   ★★★ **本次怎么找到的**（★ 顺着一页的 `See Also` 走）：
# · 先读 `IFeatureManager.InsertProtrusionSwept4` 的 **Remarks** ⇒ 「SOLIDWORKS 2018 int
# roduces a
#       new sweep architecture, making this method obsolete…」★ 而它的 `## See Also` 里列着
#       **`IFeatureManager::InsertSweepSurface2 Method`** ⚠
#     · ⇒ ★★ **那正是"扫描**曲面**"的专用方法**（★ 名字里就有 `SweepSurface`）——
# ★ **而本仓从来没查过它**（★ 我查的是 `InsertSweepRefSurface*` 与 `CreateDefinition(62)
# `）✓
#
#   ★ 官方对 `InsertSweepSurface2` 的 `Remarks` 逐字（★ 关键那句在最前面）：
#     > "**Because you are creating a surface, the sections can be open.**"
#     ★★ ⇒ ★ **它明说在建**曲面**** ✓
#     ★ mark 分工：「1 = Profile selection · 2 = Guide curve selection, if provided ·
#       **4 = Sweep path**」
#     ★ 参数（11 个）：Propagate · TwistCtrlOption · KeepTangency · BAdvancedSmoothing ·
#       StartMatchingType · EndMatchingType · PathAlign · UseFeatScope · UseAutoSelect ·
#       TwistAngle · BMergeSmoothFaces
# ★ 而它标 **Obsolete. Superseded by `IFeatureManager::InsertSweepSurface3`** ⚠ ⇒ ★ **两
# 个都试** ✓
#
# ★ 前置（★ 事实 384 的正解）：轮廓 **mark=1** · 路径 **mark=4**（★ 用 `SelectByID2` 带
# mark）。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6 + 事实 406）：**树增量** **或** **返回对象带类型名**。

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
import scripts.sw_feature_readback as FR  # noqa: E402
import scripts.sw_weldment as W  # noqa: E402


def _mk_profile_path(doc):
    """★ 轮廓（上视面圆）+ 路径（前视面直线，★ 起点在 Z=0 上 —— 方向 1 的硬约束）。"""
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCircleByRadius",
        0.0,
        0.0,
        0.0,
        5.0 / 1000.0,
    )
    P.end_sketch(doc)
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateLine",
        0.0,
        0.0,
        0.0,
        40.0 / 1000.0,
        0.0,
        0.0,
    )
    P.end_sketch(doc)


def _pick(doc):
    """★ 轮廓 mark=1 · 路径 mark=4（★ 官方逐字）。"""
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    ext = C.get_com_member(doc, "Extension")
    picked = {}
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    for label, idx, mark in (("profile", 0, 1), ("path", 1, 4)):
        if idx >= len(names):
            continue
        for cand in P._get_sketch_name_candidates(names[idx]):
            try:
                if P._select_by_id(ext, cand, "SKETCH", append=bool(picked), mark=mark):
                    picked[label] = (cand, mark)
                    break
            except Exception:  # noqa: BLE001
                pass
    per = {}
    for m in (1, 4):
        try:
            per[str(m)] = int(
                C.get_com_member(
                    C.get_com_member(doc, "SelectionManager"),
                    "GetSelectedObjectCount2",
                    m,
                )
            )
        except Exception:  # noqa: BLE001
            per[str(m)] = -1
    return picked, per


def _one(sw, tag, method):
    row = {"tag": tag, "method": method, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        _mk_profile_path(doc)
        picked, per = _pick(doc)
        row["picked"] = {k: list(v) for k, v in picked.items()}
        row["sel_by_mark"] = per
        before = list(FR.feature_names(doc) or [])
        fm = C.get_com_member(doc, "FeatureManager")
        ret = None
        try:
            #: \u2605 \u53c2\u6570\uff1aPropagate \u00b7 TwistCtrlOption \u00b7 KeepTang
            #: ency \u00b7 BAdvancedSmoothing \u00b7
            #: StartMatchingType \u00b7 EndMatchingType \u00b7 PathAlign \u00b7 UseFeatS
            #: cope \u00b7
            #:   UseAutoSelect \u00b7 TwistAngle \u00b7 BMergeSmoothFaces
            args = (True, 0, True, False, 0, 0, 0, False, True, 0.0, True)
            ret = C.get_com_member(fm, method, *args)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(C.get_com_member(ret, m))
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        types = []
        try:
            for f in W.iter_features_recursive(doc):
                try:
                    types.append(str(C.get_com_member(f, "GetTypeName2") or ""))
                except Exception:  # noqa: BLE001
                    pass
        except Exception:  # noqa: BLE001
            pass
        row["new_types"] = [t for t in types if "Sweep" in t or "Surf" in t]
        row["ok"] = bool(row["new"] or row.get("ret_type"))
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u626b\u63cf\u66f2\u9762\uff1a**\u4e13\u7528\u65b9\u6cd5** `IFeatureManager.InsertSweepSurface2/3`",
        "found_by": "\u4ece `InsertProtrusionSwept4` \u7684 **See Also** \u91cc\u6316\u5230\u7684 "
        "\u2014\u2014 \u2605 \u800c\u672c\u4ed3\u4ece\u6765\u6ca1\u67e5\u8fc7\u8fd9\u4e2a\u540d\u5b57",
        "cases": [],
    }
    for tag, m in (
        ("\u2605 InsertSweepSurface2", "InsertSweepSurface2"),
        (
            "\u2605 InsertSweepSurface3\uff08\u2605 \u7ee7\u4efb\u8005\uff09",
            "InsertSweepSurface3",
        ),
    ):
        ev["cases"].append(_one(sw, tag, m))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "sweep_surface_works" if ev["passed"] else "still_fails"
    p = R / "output" / "sweep-surface-dedicated-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09"
        % (ev["verdict"], ev["passed"], ev["total"])
    )
    for c in ev["cases"]:
        print(
            "  %-34s ok=%-6s sel=%s" % (c.get("tag"), c.get("ok"), c.get("sel_by_mark"))
        )
        print(
            "        \u56de=%-9s \u540d=%s \u578b=%s new=%s new_types=%s"
            % (
                c.get("returned"),
                c.get("ret_name"),
                c.get("ret_type"),
                c.get("new"),
                c.get("new_types"),
            )
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
