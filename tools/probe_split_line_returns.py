"""★ 真机：**分割线三条入口的返回值到底是什么**（★ 补记事实 406 那条教训下的缺口）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_split_line_returns.py
# 定位:   ★ 2026-10-03（轮 540）★ **补记一个我自己证据里的缺口**。
#
#   ★★ **缺口是什么**：轮 537-539 我对分割线只记了 **`new = []`**（树增量），
#     ★ **而没有记返回值是什么** ⚠
#     ★ 而**事实 406 的教训正相反**：`InsertCutSurface` 当时**回了对象**
#       （`Name` = 「使用曲面切除1」· `GetTypeName2` = `SurfCut`）——
#       ★ **特征其实建了、只是树回读看不见** ✓
#     ⇒ ★★ **故本探针要问**：★ **分割线那三条的返回值，是不是也带着名字/类型？**
#
#   ★ 若**带** ⇒ ★ **那"不建"是回读问题**（★ 与事实 406 同一类，★ 那会**推翻**三条结论）
#   ★ 若**是 `None`** ⇒ ★ 那"不建"是**真的**（★ 与加厚/直纹同类）
#
#   ★ 三条入口与前置（★ 照事实 417/418/419 已验的形态）：
#     · 轮廓型 `IModelDoc2.InsertSplitLineSil()` —— ★ 选一个**基准面**
# · 投影型 `IModelDoc2.InsertSplitLineProject(True, True)` —— ★ 特征 + 草图(mark 4) + 面
# (mark 1)
#     · 交叉型 `IFeatureManager.InsertSplitLineIntersect(0)` —— ★ 全部面
#
#   ★ 并**同时读**：返回值类型 · `Name` · `GetTypeName2` · 树增量 · 递归链里的类型名。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 事实 406）：**树增量** **或** **返回对象带类型名**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_feature_readback as FR  # noqa: E402
import scripts.sw_weldment as W  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402


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


def _mk_sketch2(doc):
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.01,
        -0.005,
        0.0,
        0.01,
        0.015,
        0.0,
    )
    P.end_sketch(doc)


def _probe_ret(ret):
    """★ 读返回对象的**身份**（★ 事实 406 的手法）。"""
    out = {"type": type(ret).__name__ if ret is not None else "None"}
    if ret is None:
        return out
    for k, m in (
        ("Name", "Name"),
        ("GetTypeName2", "GetTypeName2"),
        ("GetType", "GetType"),
        ("GetID", "GetID"),
    ):
        try:
            out[k] = str(C.get_com_member(ret, m))
        except Exception as exc:  # noqa: BLE001
            out[k] = "ERR %s" % str(exc)[:50]
    return out


def _all_types(doc):
    types = []
    try:
        for f in W.iter_features_recursive(doc):
            try:
                types.append(str(C.get_com_member(f, "GetTypeName2") or ""))
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass
    return types


def _one(sw, tag, kind):
    row = {"tag": tag, "kind": kind, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        _mk_solid(doc)
        if kind in ("project", "sil"):
            _mk_sketch2(doc)
        from sw_connect import get_com_member as _get
        from sw_part import _select_by_id as _sel_id
        from sw_part import _select_com_object as _sel

        ext = _get(doc, "Extension")
        picked = {}
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        ret = None
        if kind == "sil":
            for nm in ("\u524d\u89c6\u57fa\u51c6\u9762", "Front Plane"):
                if _sel_id(ext, nm, "PLANE", append=False, mark=0):
                    picked["plane"] = nm
                    break
            ret = C.get_com_member(doc, "InsertSplitLineSil")
        elif kind == "project":
            names = list(FR.feature_names(doc) or [])
            sk = [
                n
                for n in names
                if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
            ]
            for nm in ("\u51f8\u53f0-\u62c9\u4f381", "Boss-Extrude1"):
                if _sel_id(ext, nm, "BODYFEATURE", append=False, mark=0):
                    picked["feature"] = nm
                    break
            if len(sk) >= 2 and _sel_id(
                ext, sk[-1], "SKETCH", append=bool(picked), mark=4
            ):
                picked["sketch"] = sk[-1]
            try:
                for b in list(_get(doc, "GetBodies2", 0, True) or []):
                    for f in list(_get(b, "GetFaces") or [])[:1]:
                        if _sel(f, append=bool(picked), mark=1):
                            picked["face"] = True
                        break
                    break
            except Exception:  # noqa: BLE001
                pass
            before = list(FR.feature_names(doc) or [])
            ret = C.get_com_member(doc, "InsertSplitLineProject", True, True)
        else:
            n = 0
            for bt in (0, 1):
                for b in list(_get(doc, "GetBodies2", bt, True) or []):
                    for f in list(_get(b, "GetFaces") or []):
                        if _sel(f, append=(n > 0), mark=0):
                            n += 1
            picked["faces"] = n
            fm = C.get_com_member(doc, "FeatureManager")
            ret = C.get_com_member(fm, "InsertSplitLineIntersect", 0)
        row["picked"] = picked
        row["returned"] = _probe_ret(ret)
        if kind == "project":
            after = list(FR.feature_names(doc) or [])
            row["new"] = [x for x in after if x not in before]
        types = _all_types(doc)
        row["split_types"] = [t for t in types if "Split" in t]
        row["tree"] = list(FR.feature_names(doc) or [])
        #: \u2605\u2605 \u5224\u636e\uff08\u4e8b\u5b9e 406\uff09
        row["ok"] = bool(
            row.get("new") or row["returned"].get("GetTypeName2") or row["split_types"]
        )
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
        "_": "\u5206\u5272\u7ebf\u4e09\u6761\u5165\u53e3\u7684**\u8fd4\u56de\u503c\u5230\u5e95\u662f\u4ec0\u4e48**\uff08\u2605 \u8865\u8bb0\u7f3a\u53e3\uff09",
        "why": "\u4e8b\u5b9e 406 \u7684\u6559\u8bad\uff1a`InsertCutSurface` \u5f53\u65f6**\u56de\u4e86\u5bf9\u8c61**"
        "\uff08\u7279\u5f81\u5176\u5b9e\u5efa\u4e86\uff09\u2014\u2014 \u2605 \u800c\u5206\u5272\u7ebf\u6211\u53ea\u8bb0\u4e86 `new=[]`",
        "cases": [],
    }
    for tag, kind in (
        ("\u8f6e\u5ed3\u578b InsertSplitLineSil", "sil"),
        ("\u6295\u5f71\u578b InsertSplitLineProject", "project"),
        ("\u4ea4\u53c9\u578b InsertSplitLineIntersect", "intersect"),
    ):
        ev["cases"].append(_one(sw, tag, kind))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["named"] = sum(
        1 for c in ev["cases"] if (c.get("returned") or {}).get("GetTypeName2")
    )
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "returns_named_object" if ev["named"] else "returns_none_for_all"
    p = R / "output" / "split-line-returns-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08\u6709\u7c7b\u578b\u540d %d / %d\uff09"
        % (ev["verdict"], ev["named"], ev["total"])
    )
    for c in ev["cases"]:
        r = c.get("returned") or {}
        print(
            "  %-34s \u56de=%s \u540d=%s \u578b=%s"
            % (c.get("tag"), r.get("type"), r.get("Name"), r.get("GetTypeName2"))
        )
        print(
            "        picked=%s new=%s split_types=%s"
            % (
                json.dumps(c.get("picked"), ensure_ascii=False)[:52],
                c.get("new"),
                c.get("split_types"),
            )
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
