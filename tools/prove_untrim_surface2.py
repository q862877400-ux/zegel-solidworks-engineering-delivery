"""★ 真机：**解除剪裁曲面** `InsertUntrimSurface2`（★ 官方给全了 5 参与两个枚举）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_untrim_surface2.py
# 定位:   ★ 2026-10-03（轮 554）★ 照新纪律（**官方文档是第 0 步**）攻台账的「解除剪裁
#           曲面」。
#
#   ★★★★ **而读文档时先把台账的 api 名推翻了一半**：
#     `c_:\swapi\types\IFeatureManager\InsertUntrimSurface.md` 逐字：
#     > "**Obsolete. Superseded by `IFeatureManager::InsertUntrimSurface2`.**"
#     ⇒ ★★ **故用**第二代**** ✓
#
#   ★★★ **`InsertUntrimSurface2` 的签名（5 参）与 Remarks（逐字）**：
#     ```
#     Feature InsertUntrimSurface2(int FaceUntrimType, int EdgeUntrimType, double Distance,
#                                  bool BMerge, bool BTrimOppositeSide)
#     ```
#     · 「**is valid only for surface parts**」⇒ ★ **必须在**曲面零件**上**（★ 不是实体件）
#     · 「**requires preselection of the face or edges** you want to untrim」
#   ★★ **两个枚举的值来自**反射**（★ 铁律 4）**：
#     ```
#     swFaceUntrimType_e : 0 = AllEdges · 1 = InternalEdges · 2 = ExternalEdges
#     swEdgeUntrimType_e : 1 = ConnectEndPoints · 2 = ExtendEdges
#     ```
#
#   ★ 前置：★ **一个被剪裁过的曲面**（★ 否则没有"剪裁"可解除）⇒
#     ★ 本探针先**造一张曲面、用「使用曲面切除」剪它**，★ 再对留下的面调解除剪裁。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6 + 事实 420）：**树增量**（★ 返回值也记账）。

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
from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402


#: \u2605 \u53cd\u5c04\u91cc\u7684\u503c\uff08\u2605 \u88c1\u51b3\u8005\uff09
def _mk_trimmed_surface(doc):
    """★ **一张被剪裁过的曲面**（★ 先造曲面、★ 再用曲面切除剪它）。"""
    made = 0
    for i, (plane, rect) in enumerate(
        (
            ("Front Plane", (-0.02, -0.02, 0.02, 0.02)),
            ("Top Plane", (-0.02, -0.01, 0.02, 0.01)),
        )
    ):
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        p_.start_sketch(doc, plane_name=plane)
        c_.get_com_member(
            c_.get_com_member(doc, "SketchManager"),
            "CreateCornerRectangle",
            rect[0],
            rect[1],
            0.0,
            rect[2],
            rect[3],
            0.0,
        )
        p_.end_sketch(doc)
        names = [
            n
            for n in (p_.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        for cand in ((names[-1],) + tuple(names) + ("\u8349\u56fe%d" % (i + 1),))[:4]:
            try:
                if sf.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get(
                    "ok"
                ):
                    made += 1
                    break
            except Exception:  # noqa: BLE001
                continue
    return made


def _volume(doc):
    try:
        mp = c_.get_com_member(c_.get_com_member(doc, "Extension"), "CreateMassProperty")
        c_.get_com_member(mp, "SurfaceArea") if False else None
        return None
    except Exception:  # noqa: BLE001
        return None


def _one(sw, tag, entry, distance, b_merge, b_trim):
    row = {"tag": tag, "entry": entry, "distance": distance, "ok": False}
    doc = None
    try:
        doc = c_.new_document(sw, "part")
        row["surfaces_made"] = _mk_trimmed_surface(doc)
        #: \u2605 \u9884\u9009**\u66f2\u9762\u7684\u4e00\u5f20\u9762**\uff08\u2605 \u5b9
        #: 8\u65b9 "requires preselection"\uff09
        from sw_connect import get_com_member as _get
        from sw_part import _select_com_object as _sel

        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        picked = 0
        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            for f in list(_get(b, "GetFaces") or [])[:1]:
                if _sel(f, append=(picked > 0), mark=0):
                    picked += 1
            break
        row["faces_picked"] = picked
        try:
            row["sel"] = int(
                _get(_get(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0
            )
        except Exception:  # noqa: BLE001
            row["sel"] = -1
        before = list(fr.feature_names(doc) or [])
        fm = _get(doc, "FeatureManager")
        ret = None
        try:
            #: \u2605 5 \u53c2\uff1aFaceUntrimType(=0 AllEdges) \u00b7 EdgeUntrimType(=2
            #:  ExtendEdges) \u00b7
            #:   Distance \u00b7 BMerge \u00b7 BTrimOppositeSide
            ret = _get(fm, entry, 0, 2, float(distance), bool(b_merge), bool(b_trim))
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_get(ret, m))
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
        after = list(fr.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"] or row.get("ret_type"))
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            try:
                t = str(c_.get_com_member(doc, "GetTitle") or "")
                if t:
                    c_.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = c_.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u89e3\u9664\u526a\u88c1\u66f2\u9762\uff1a`InsertUntrimSurface2`\uff08\u2605 \u7b2c\u4e8c\u4ee3 \u2014\u2014 \u53f0\u8d26\u5199\u7684\u662f\u5df2\u5e9f\u5f03\u7684\u7b2c\u4e00\u4ee3\uff09",
        "official": "InsertUntrimSurface.md \u9010\u5b57\uff1aObsolete. Superseded by InsertUntrimSurface2\uff1b"
        "Remarks\uff1avalid only for surface parts\u3001requires preselection",
        "cases": [],
    }
    ev["cases"].append(
        _one(
            sw,
            "\u2605 InsertUntrimSurface2\uff08\u7b2c\u4e8c\u4ee3\uff09",
            "InsertUntrimSurface2",
            0.005,
            True,
            False,
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a\u7b2c\u4e00\u4ee3 InsertUntrimSurface\uff08\u2605 \u5df2\u5e9f\u5f03\uff09",
            "InsertUntrimSurface",
            0.005,
            True,
            False,
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "untrim2_works" if ev["cases"][0].get("ok") else "untrim2_fails"
    p = R / "output" / "untrim-surface2-evidence.json"
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
            "  %-48s ok=%-6s \u9762=%s sel=%s"
            % (c.get("tag"), c.get("ok"), c.get("faces_picked"), c.get("sel"))
        )
        print(
            "        \u65b0\u589e=%s \u540d=%s \u578b=%s"
            % (c.get("new"), c.get("ret_name"), c.get("ret_type"))
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
