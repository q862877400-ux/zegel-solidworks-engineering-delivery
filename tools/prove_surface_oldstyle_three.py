"""★ 真机：三条**旧式**曲面方法（`IModelDoc2.Insert{Offset,PlanarRef,FeatureReplaceFace}*`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_surface_oldstyle_three.py
# 定位:   ★ 2026-10-03（轮 516）★ 走**事实 395 明确指出的那条方向**：
#
#   > ★ **旧式方法**那侧是成的（填充 `InsertFillSurface2` / 延伸 `InsertExtendSurface` /
#   >   缝合 `InsertSewRefSurface` / 曲面-拉伸 `FeatureExtruRefSurface3`）——
# >   ★★ 而**新架构**（`CreateDefinition` + `CreateFeature`）那侧对扫描面/加厚/直纹**静
# 默不成**。
#
# ★ B6 里剩的几条**恰好都有 `IModelDoc2` 上的旧式入口**（★ 与**成过**的 `InsertExtendSur
# face` 同层）：
#     ✓ `IModelDoc2.InsertPlanarRefSurface()`                0 参 · 回 bool  → T605 平面区域
#     ✓ `IModelDoc2.InsertOffsetSurface(Thickness, Reverse)` 2 参 · void     → T606 等距曲面
#     ✓ `IModelDoc2.InsertFeatureReplaceFace()`              0 参 · void     → T609 替换面
# ✗ `InsertTrimSurface`                                  ★ **swapi 里查不到** → T607（铁
# 律 5）
#
# 官方前置（★ md 的 `Remarks` 逐字）：
# · `InsertOffsetSurface` ⇒ 「Make the selections using `SelectByID2` **before** calling
#  this method」
#   · `InsertPlanarRefSurface` ⇒ 「select the surface's **boundary entities** using
#     `SelectByID2` with **Marks of 1**」
# · `InsertFeatureReplaceFace` ⇒ 「select the faces to **replace** … with **Marks of 1**
#  and
#     select the re[placement face] …」⇒ ★★ 两个 mark 分工（★ 而★ 本包装的选法是**推断** ⚠）
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：**特征树多了新特征**。

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
from scripts import sw_surface_features as SF  # noqa: E402


def _mk_surface(doc, plane="Front Plane", depth=20.0):
    """★ 建**一张曲面**（★ 用本仓已验过的 `create_extruded_surface_report`）。"""
    P.start_sketch(doc, plane_name=plane)
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.02,
        -0.02,
        0.0,
        0.02,
        0.02,
        0.0,
    )
    P.end_sketch(doc)
    for cand in ("\u8349\u56fe1", "Sketch1"):
        try:
            r = SF.create_extruded_surface_report(doc, depth, sketch_name=cand)
            if r.get("ok"):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _mk_solid(doc):
    """★ 建一个**实体盒**（★ 给替换面用）。"""
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
    for cand in ("\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _run(sw, tag, fn):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        prep = fn(doc)
        row["prep"] = prep
        if isinstance(prep, dict):
            row["result"] = {k: v for k, v in prep.items() if k != "\u2605"}
            row["ok"] = bool(prep.get("ok"))
        row["names"] = list(P.feature_names(doc) or [])
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


def _c_offset(doc):
    _mk_surface(doc)
    return SF.insert_offset_surface_report(doc, 5.0)


def _c_planar(doc):
    _mk_surface(doc)
    return SF.insert_planar_ref_surface_report(doc)


def _c_replace(doc):
    _mk_solid(doc)
    try:
        C.get_com_member(doc, "ClearSelection2", True)
    except Exception:  # noqa: BLE001
        pass
    _mk_surface(doc, plane="Right Plane")
    return SF.insert_replace_face_report(doc)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u4e09\u6761**\u65e7\u5f0f**\u66f2\u9762\u65b9\u6cd5\uff08IModelDoc2 \u90a3\u5c42\uff09",
        "why": "\u4e8b\u5b9e 395\uff1a\u65e7\u5f0f\u65b9\u6cd5\u90a3\u4fa7\u662f\u6210\u7684\uff08\u586b\u5145/\u5ef6\u4f38/\u7f1d\u5408/\u66f2\u9762-\u62c9\u4f38\uff09",
        "cases": [],
    }
    for tag, fn in (
        ("\u2605 T606 \u7b49\u8ddd\u66f2\u9762", _c_offset),
        ("\u2605 T605 \u5e73\u9762\u533a\u57df", _c_planar),
        ("\u2605 T609 \u66ff\u6362\u9762", _c_replace),
    ):
        ev["cases"].append(_run(sw, tag, fn))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "surface-oldstyle-three-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u6210\u4e86 **%d / %d**" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-22s ok=%-6s prep=%s" % (c.get("tag"), c.get("ok"), c.get("prep")))
        r = c.get("result") or {}
        if r:
            print(
                "        new=%-20s sel=%s err=%s"
                % (
                    r.get("new_features"),
                    r.get("faces_selected", r.get("edges_selected")),
                    str(r.get("error") or "")[:80],
                )
            )
        if c.get("err"):
            print("        ERR=%s" % str(c["err"])[:140])
        print("        tree=%s" % (c.get("names") or [])[-3:])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
