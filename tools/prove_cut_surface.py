"""★ 真机：**曲面切除**（`IFeatureManager.InsertCutSurface`）—— 与"剪裁曲面"是**两件事**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_cut_surface.py
# 定位:   ★ 2026-10-03（轮 521）★ 给 `sw_surface_features.cut_surface_report` 留真机证
#           据。
#   它是从**通配筛**（★ 事实 401 那条手法）里抓到的**第二个候选**。
#
#   ★★ **先纠正一个极易混的地方**：
#     · **剪裁曲面**（B6/T607）= `PreTrimSurface`/`PostTrimSurface` —— **剪的是曲面**
#     · **曲面切除**（本条）= `InsertCutSurface` —— ★ 官方逐字
#       「**Inserts a surface-cut feature** using the **preselected surface or plane**」
#       ⇒ ★★ **拿一个曲面/基准面去**切实体**** ✓
#     ⚠ 两者中文名都含"裁/切"、API 名都含 `TrimSurface`/`CutSurface` ⇒ **极易混**。
#
# 官方三源（★ 铁律 4）：`IFeatureManager.InsertCutSurface` ⇒
#   `(Flip, KeepPieceIndex, UseFeatScope, UseAutoSelect, Bodies, Error(out), Retval(out))`
#   ★ **5 个 in + 2 个 out**；`IModelDoc2` 那个 ⇒ **Obsolete**。
#   参数语义（md 逐字）：`Flip` 反向 · `KeepPieceIndex` **有歧义时留哪一块** ·
#   `UseFeatScope` 只切传给 `Bodies` 的体 · `UseAutoSelect` 自动切**所有**相交体 ·
#   `Bodies` 空数组 ⇒ 「**cut all bodies**」。
#
# ★ 前置：★ **选一个曲面或基准面**（官方：「using the **preselected** surface or plane」
# ）。
# ⚠ 而探针里我**两种都试**：① 曲面面（★ 需要一个实体 + 一张曲面）② 基准面（★ 只要实体）
# 。
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


def _mk_solid(doc):
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
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _mk_surface(doc, plane="Front Plane"):
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
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
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            if SF.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _run(sw, tag, prep, **kw):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["prep"] = prep(doc)
        r = SF.cut_surface_report(doc, **kw)
        row["result"] = {k: v for k, v in (r or {}).items() if k != "\u2605"}
        row["ok"] = bool((r or {}).get("ok"))
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
        "_": "\u66f2\u9762\u5207\u9664\uff1a`IFeatureManager.InsertCutSurface`",
        "note": "\u5b83\u4e0e\u300c\u526a\u88c1\u66f2\u9762\u300d\uff08Pre/PostTrimSurface\uff09**\u662f\u4e24\u4ef6\u4e8b** "
        "\u2014\u2014 \u672c\u6761\u62ff\u9762/\u57fa\u51c6\u9762**\u5207\u5b9e\u4f53**",
        "cases": [],
    }
    #: \u2605 \u2460 \u53ea\u6709\u5b9e\u4f53\uff08\u2605 \u7528\u57fa\u51c6\u9762\u4f5c
    #: \u5207\u9762\uff09
    ev["cases"].append(
        _run(
            sw,
            "\u53ea\u5b9e\u4f53 \u00b7 \u57fa\u51c6\u9762\u4f5c\u5207\u9762",
            _mk_solid,
        )
    )

    #: \u2605 \u2461 \u5b9e\u4f53 + \u4e00\u5f20\u76f8\u4ea4\u66f2\u9762\uff08\u2605 \u7
    #: 528\u66f2\u9762\u4f5c\u5207\u9762\uff09
    def _both(d):
        a = _mk_solid(d)
        b = _mk_surface(d)
        return {"solid": a, "surface": b}

    ev["cases"].append(_run(sw, "\u5b9e\u4f53 + \u76f8\u4ea4\u66f2\u9762", _both))
    #: \u2605 \u2462 \u53d8\u4f53\uff1aflip=True
    ev["cases"].append(
        _run(sw, "\u5b9e\u4f53 + \u66f2\u9762 \u00b7 flip=True", _both, flip=True)
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "cut_surface_works" if ev["passed"] else "cut_surface_fails"
    p = R / "output" / "cut-surface-evidence.json"
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
        r = c.get("result") or {}
        print(
            "  %-30s ok=%-6s prep=%s"
            % (c.get("tag"), c.get("ok"), str(c.get("prep"))[:70])
        )
        if r:
            print(
                "        new=%-22s sel=%-4s picked=%s \u56de=%s"
                % (
                    r.get("new_features"),
                    r.get("selected"),
                    r.get("picked"),
                    r.get("returned"),
                )
            )
            if r.get("error"):
                print("        err=%s" % str(r["error"])[:130])
        if c.get("err"):
            print("        ERR=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
