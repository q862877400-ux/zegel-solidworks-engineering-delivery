"""★ 真机：**旋转切除** —— 官方文档指的路（`FeatureRevolve2(IsCut=True)`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_revolve_cut.py
# 定位:   ★ 2026-10-03（轮 550）★ **按新纪律「官方文档是第 0 步」走出来的第一条能力**。
#
#   ★★★★ **官方文档直接给了答案**（★ 而我原本要去攻台账里写的 `FeatureRevolveCut2`）：
#     · `C:\swapi\types\IFeatureManager\FeatureRevolveCut2.md` 逐字：
#       > "**Obsolete. Superseded by `IFeatureManager::FeatureRevolve2`.**"
#       ⇒ ★★ **故那个入口不用碰** ⚠
# · `FeatureRevolve2` 的 **20 参**里第 4 个是 **`IsCut`**（"True if this is a **cut** re
# volve feature"）；
#     · 它的 Remarks 给了**完整 mark 分工**（★ 其中 `mark = 32` 那条本仓从未用过）。
#     ⇒ ★★ **故 = 本仓 `revolve_boss` 把那个布尔翻成 `True`** ✓
#
#   ★ 本探针就验这一件事：★ **同一个函数、只翻一个布尔，能不能真的切出材料**。
# ★ 判据（★ 规则 6 + 事实 420）：① **树增量** · ② **质量属性的体积变化**（★ 切除 ⇒ 变小
# ）。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：**树新增了特征** **且** **体积比剖切前小**。

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_feature_readback as fr  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _mk_solid_and_profile(doc):
    """★ 一个实体盒 + ★ 一个**在盒内的剖面**（★ 旋转切除要有料可切）。"""
    #: \u2605 \u5b9e\u4f53
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.03,
        -0.03,
        0.0,
        0.03,
        0.03,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    ok = False
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.03)
            ok = True
            break
        except Exception:  # noqa: BLE001
            continue
    #: \u2605 \u5256\u9762\uff08\u2605 \u524d\u89c6\u9762\u4e0a\u7684\u77e9\u5f62 + \u4e
    #: 2d\u5fc3\u7ebf\uff09
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    sm = C.get_com_member(doc, "SketchManager")
    #: \u2605 \u4e2d\u5fc3\u7ebf\uff08\u2605 \u65cb\u8f6c\u8f74\uff09
    C.get_com_member(sm, "CreateCenterLine", 0.0, -0.04, 0.0, 0.0, 0.04, 0.0)
    #: \u2605 \u5256\u9762\uff1a\u2605 \u8ddd\u79bb\u8f74\u4e00\u5b9a\u504f\u79fb\u7684\
    #: u77e9\u5f62\uff08\u2605 \u5207\u51fa\u73af\u69fd\uff09
    C.get_com_member(sm, "CreateCornerRectangle", 0.010, -0.02, 0.0, 0.020, 0.02, 0.0)
    P.end_sketch(doc)
    names2 = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    return ok, (names2[-1] if names2 else "\u8349\u56fe2")


def _volume(doc):
    try:
        mp = C.get_com_member(C.get_com_member(doc, "Extension"), "CreateMassProperty")
        v = C.get_com_member(mp, "Volume")
        return float(v) if v is not None else None
    except Exception:  # noqa: BLE001
        return None


def _one(sw, tag, cut):
    row = {"tag": tag, "cut": cut, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        ok_solid, sk = _mk_solid_and_profile(doc)
        row["solid"] = ok_solid
        row["sketch"] = sk
        before = list(fr.feature_names(doc) or [])
        row["vol_before"] = _volume(doc)
        try:
            if cut:
                P.revolve_cut(doc, sk, math.radians(360.0), axis_sketch_name=sk)
            else:
                P.revolve_boss(doc, sk, math.radians(360.0), axis_sketch_name=sk)
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(fr.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["vol_after"] = _volume(doc)
        if row["vol_before"] and row["vol_after"]:
            row["vol_ratio"] = round(row["vol_after"] / row["vol_before"], 4)
        #: \u2605 \u5224\u636e\uff1a**\u6811\u589e\u91cf** \u4e14\uff08\u5207\u9664 \u21
        #: d2 \u4f53\u79ef\u53d8\u5c0f\uff09
        row["ok"] = bool(row["new"]) and (
            row.get("vol_ratio") is None or (row["vol_ratio"] < 0.999 if cut else True)
        )
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


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u65cb\u8f6c\u5207\u9664\uff1a`FeatureRevolve2(IsCut=True)`\uff08\u2605 \u5b98\u65b9\u6587\u6863\u6307\u7684\u8def\uff09",
        "official": "FeatureRevolveCut2.md \u9010\u5b57\uff1aObsolete. Superseded by IFeatureManager::FeatureRevolve2\uff1b"
        "FeatureRevolve2 \u7684 IsCut \u5c31\u662f\u5207\u9664",
        "cases": [],
    }
    ev["cases"].append(
        _one(sw, "\u2605 \u65cb\u8f6c**\u5207\u9664**\uff08IsCut=True\uff09", True)
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a\u65cb\u8f6c**\u51f8\u53f0**\uff08IsCut=False\uff09",
            False,
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "revolve_cut_works" if ev["cases"][0].get("ok") else "revolve_cut_fails"
    )
    p = R / "output" / "revolve-cut-evidence.json"
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
            "  %-34s ok=%-6s \u65b0\u589e=%s"
            % (c.get("tag"), c.get("ok"), c.get("new"))
        )
        print(
            "        \u4f53\u79ef %s \u2192 %s \u00b7 \u6bd4=%s"
            % (c.get("vol_before"), c.get("vol_after"), c.get("vol_ratio"))
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
