"""★ 真机：**`FirstFeature` 全链 dump** —— 为什么 `feature_names` 看不见 `SurfCut`。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_feature_names_blindspot.py
# 定位:   ★ 2026-10-03（轮 525）★ 查一个**本会话最重要的自我纠错**的根因。
#
#   ★★ **上一轮（事实 405）之后的发现**：
#     `InsertCutSurface` 的返回值（★ 那个 `CDispatch`）读出来是：
#     ```
#     Name          ⇒ 「使用曲面切除1」
#     GetTypeName2  ⇒ 「SurfCut」
#     GetType      ⇒ 22
#     GetID        ⇒ 87
#     ```
#     ⇒ ★★★ **特征其实**建了**！** —— ★ 而**我的判据（特征树增量）没抓到它** ⚠⚠⚠
#
#   ★ 而 `feature_names`（`scripts/sw_feature_readback.py` L77-L95）走的是
#     `model.FirstFeature` → `GetNextFeature` 链，★ 且有**两层过滤**：
#       ① `_is_real_feature(feat)`（★ 只收 `GetTypeName2` 非空的）
#       ② 排除 `_CONTAINER_NODES`
#
#   ⇒ ★★ **本探针要回答**：★ **`使用曲面切除1` 到底在不在那条链上？**
#     ⓐ ★ 若**在** ⇒ ★ 那是 `_is_real_feature` 或容器名单把它挡了
#     ⓑ ★ 若**不在** ⇒ ★ 那是 `FirstFeature` 链**本身不覆盖它**（★ 更深的坑）
#
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 本探针**不求建成** —— ★ 它要的是**链上到底有什么**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_feature_readback as fr  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as p_  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402


def _mk_solid(doc):
    p_.start_sketch(doc, plane_name="Top Plane")
    c.get_com_member(
        c.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.03,
        -0.03,
        0.0,
        0.03,
        0.03,
        0.0,
    )
    p_.end_sketch(doc)
    names = [
        n
        for n in (p_.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            p_.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _mk_surface(doc, plane="Front Plane"):
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    p_.start_sketch(doc, plane_name=plane)
    c.get_com_member(
        c.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.02,
        -0.02,
        0.0,
        0.02,
        0.02,
        0.0,
    )
    p_.end_sketch(doc)
    names = [
        n
        for n in (p_.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            if sf.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _dump_chain(model, use_safe=True):
    """★ **逐节点 dump**：名字 · `GetTypeName2` · `_is_real_feature` 的判定。"""
    rows = []
    try:
        feat = c.get_com_member(model, "FirstFeature")
    except Exception as exc:  # noqa: BLE001
        return [{"err": "%s: %s" % (type(exc).__name__, str(exc)[:100])}]
    i = 0
    while feat is not None and i < 200:
        row = {"i": i}
        try:
            row["name"] = str(c.get_com_member(feat, "Name") or "")
        except Exception as exc:  # noqa: BLE001
            row["name"] = "ERR %s" % str(exc)[:50]
        try:
            row["type"] = str(c.get_com_member(feat, "GetTypeName2") or "")
        except Exception as exc:  # noqa: BLE001
            row["type"] = "ERR %s" % str(exc)[:50]
        try:
            row["is_real"] = bool(fr._is_real_feature(feat))
        except Exception as exc:  # noqa: BLE001
            row["is_real"] = "ERR %s" % str(exc)[:50]
        try:
            row["in_container"] = str(row.get("name")) in fr._CONTAINER_NODES
        except Exception:  # noqa: BLE001
            row["in_container"] = None
        rows.append(row)
        try:
            feat = c.get_com_member(feat, "GetNextFeature")
        except Exception:  # noqa: BLE001
            break
        i += 1
    return rows


def main() -> int:
    sw, _ = c.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "FirstFeature \u5168\u94fe dump \u2014\u2014 \u4e3a\u4ec0\u4e48 feature_names \u770b\u4e0d\u89c1 SurfCut",
        "steps": [],
    }
    doc = None
    try:
        doc = c.new_document(sw, "part")
        _mk_solid(doc)
        _mk_surface(doc)
        ev["chain_before"] = _dump_chain(doc)
        ev["names_before"] = list(fr.feature_names(doc) or [])
        #: \u2605 \u53ea\u9009\u7b2c\u4e00\u5f20\u66f2\u9762\u9762 + 6 \u53c2\u8c03\u752
        #: 8
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        from sw_connect import get_com_member as _get
        from sw_connect import out_i4 as _oi4
        from sw_part import _select_com_object as _sel

        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            faces = list(_get(b, "GetFaces") or [])
            if faces:
                _sel(faces[0], append=True, mark=0)
            break
        fm = c.get_com_member(doc, "FeatureManager")
        ret = None
        try:
            ret = c.get_com_member(
                fm, "InsertCutSurface", False, 0, False, True, [], _oi4()
            )
        except Exception as exc:  # noqa: BLE001
            ev["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        ev["returned"] = {
            "type": type(ret).__name__ if ret is not None else "None",
            "Name": None,
            "GetTypeName2": None,
        }
        if ret is not None:
            for k in ("Name", "GetTypeName2"):
                try:
                    ev["returned"][k] = str(c.get_com_member(ret, k))
                except Exception as exc:  # noqa: BLE001
                    ev["returned"][k] = "ERR %s" % str(exc)[:60]
        ev["chain_after"] = _dump_chain(doc)
        ev["names_after"] = list(fr.feature_names(doc) or [])
        ev["ok"] = bool(ev["returned"].get("Name"))
    except Exception as exc:  # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    p = R / "output" / "feature-names-blindspot-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u8c03\u7528\u524d \u94fe\u4e0a %d \u8282\u70b9 \u00b7 feature_names %d \u4e2a"
        % (len(ev.get("chain_before") or []), len(ev.get("names_before") or []))
    )
    print(
        "  \u8fd4\u56de\uff1a%s"
        % json.dumps(ev.get("returned"), ensure_ascii=False)[:140]
    )
    print(
        "  \u8c03\u7528\u540e \u94fe\u4e0a %d \u8282\u70b9 \u00b7 feature_names %d \u4e2a"
        % (len(ev.get("chain_after") or []), len(ev.get("names_after") or []))
    )
    print("  \u2605 \u8c03\u7528\u540e\u7684\u94fe\uff1a")
    for r in ev.get("chain_after") or []:
        print(
            "     %-3s %-26s %-14s is_real=%-6s container=%s"
            % (
                r.get("i"),
                str(r.get("name"))[:26],
                str(r.get("type"))[:14],
                r.get("is_real"),
                r.get("in_container"),
            )
        )
    print("  \u2605 feature_names\uff1a%s" % (ev.get("names_after"),))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
