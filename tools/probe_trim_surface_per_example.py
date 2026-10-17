"""★ 真机：剪裁曲面**照官方例子重做** —— 顺序是 `PreTrimSurface` → 选 `SURFACEBODY` → `PostTrimSurface`。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_trim_surface_per_example.py
# 定位:   ★ 2026-10-03（轮 534）★ 剪裁曲面（B6/T607）—— ★ **照**官方例子**重做**。
#
#   ★★ **怎么找到例子的**（★ 那把钥匙的第四次使用 · 而这次走到了**第六种源**）：
#     · 前三次用「官方原话里的每个名词都要落实」（事实 410/413）—— 一次成、两次否；
#     · 本轮读 `IFeatureManager.PreTrimSurface` 的 **CHM 页**，★ 而那页顶上写着
#       「See Also **Example**」⇒ ★★ **顺着走** ⇒ 落到
#       `Create_Trimmed_Surface_Feature_Example_{CSharp,VB,VBNET}.htm` ✓
#   ⇒ ★★★ **那是本仓从未用过的源：官方**例子**（★ 它给的是**调用序** —— 签名与 Remarks 都给不了）**
#
#   ★★★★★ **官方例子的完整调用序**（`Create_Trimmed_Surface_Feature_Example_VBNET.htm` 逐字）：
#     ```
#     ① 建两张相交曲面（FeatureExtruRefSurface2 ×2）
#     ② **PreTrimSurface(False, True, False, False)**   ← ★ **先调它！且此时尚未选任何东西** ⚠
#     ③ **SelectByID2("", "SURFACEBODY", x, y, z, True, 0, Nothing, 0)**
#          ← ★★ **选的是 `SURFACEBODY` 类型（按坐标）**，★ 而 `True` = append ⚠
#     ④ **PostTrimSurface(True)**                       ← ★ **然后才提交**
#     ```
#
#   ★★ **而本仓轮 519 的错**（★ 现在一目了然）：
#     · ★ **顺序**反了 —— 我**先选面**、**再**调 `PreTrimSurface` ⚠
#     · ★ **选择类型**也不同 —— 我按**对象选 FACE**，★ 而例子选的是 **`SURFACEBODY`** ⚠
#
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

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import sw_surface_features as SF                         # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402
import scripts.sw_weldment as W                                       # noqa: E402


def _mk_two_crossing_surfaces(doc):
    """★ 两张相交曲面（★ 与轮 519 同款前置）。"""
    made = 0
    for i, (plane, rect) in enumerate((("Front Plane", (-0.02, -0.02, 0.02, 0.02)),
                                       ("Top Plane", (-0.02, -0.01, 0.02, 0.01)))):
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name=plane)
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                         rect[0], rect[1], 0.0, rect[2], rect[3], 0.0)
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or [])
                 if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
        for cand in ((names[-1],) + tuple(names) + ("\u8349\u56fe%d" % (i + 1),))[:4]:
            try:
                if SF.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
                    made += 1
                    break
            except Exception:                                             # noqa: BLE001
                continue
    return made


def _one(sw, tag, pick_mode):
    row = {"tag": tag, "pick_mode": pick_mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["surfaces_made"] = _mk_two_crossing_surfaces(doc)
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        fm = C.get_com_member(doc, "FeatureManager")
        ext = C.get_com_member(doc, "Extension")
        before = list(FR.feature_names(doc) or [])
        #: \u2605\u2605 **\u6b65\u9aa4\u2461\uff1a\u5148\u8c03 PreTrimSurface**\uff08\u2605 \u800c\u6b64\u65f6\u5c1a\u672a\u9009\u4efb\u4f55\u4e1c\u897f\uff09
        pre = None
        try:
            pre = C.get_com_member(fm, "PreTrimSurface", False, True, False, False)
            row["pre"] = str(pre)
        except Exception as exc:                                          # noqa: BLE001
            row["pre_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        #: \u2605\u2605 **\u6b65\u9aa4\u2462\uff1a\u9009 `SURFACEBODY`\uff08\u6309\u5750\u6807\uff09** \u2014\u2014 \u2605 \u800c\u4e0d\u662f\u6309\u5bf9\u8c61\u9009 FACE
        picked = False
        if pick_mode == "surfacebody_by_coord":
            for pt in ((0.0, 0.0, 0.0), (0.005, 0.0, 0.005), (-0.005, 0.0, -0.005),
                       (0.0, 0.005, 0.0), (0.0, -0.005, 0.0)):
                try:
                    if C.get_com_member(ext, "SelectByID2", "", "SURFACEBODY",
                                        pt[0], pt[1], pt[2], True, 0, None, 0):
                        picked = True
                        row["picked_at"] = list(pt)
                        break
                except Exception:                                         # noqa: BLE001
                    continue
        else:
            #: \u2605 \u5bf9\u7167\uff1a\u6309**\u5bf9\u8c61**\u9009**\u6240\u6709\u66f2\u9762\u9762**\uff08\u2605 \u672c\u4ed3\u539f\u6765\u7684\u505a\u6cd5\uff09
            picked = SF._select_all_surface_faces(doc, mark=0) > 0
        row["picked"] = picked
        try:
            row["sel"] = int(C.get_com_member(C.get_com_member(doc, "SelectionManager"),
                                              "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                 # noqa: BLE001
            row["sel"] = -1
        #: \u2605\u2605 **\u6b65\u9aa4\u2463\uff1aPostTrimSurface(True)**
        post = None
        try:
            post = C.get_com_member(fm, "PostTrimSurface", True)
            row["post"] = type(post).__name__ if post is not None else "None"
            if post is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(C.get_com_member(post, m))
                    except Exception:                                     # noqa: BLE001
                        pass
        except Exception as exc:                                          # noqa: BLE001
            row["post_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        types = []
        try:
            for f in W.iter_features_recursive(doc):
                try:
                    types.append(str(C.get_com_member(f, "GetTypeName2") or ""))
                except Exception:                                         # noqa: BLE001
                    pass
        except Exception:                                                     # noqa: BLE001
            pass
        row["new_types"] = [t for t in types if "Trim" in t or "Surf" in t]
        row["ok"] = bool(row["new"] or row.get("ret_type"))
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u526a\u88c1\u66f2\u9762\uff1a**\u7167\u5b98\u65b9\u4f8b\u5b50**\u91cd\u505a\uff08PreTrimSurface \u2192 \u9009 SURFACEBODY \u2192 PostTrimSurface\uff09",
          "example": "Create_Trimmed_Surface_Feature_Example_VBNET.htm",
          "cases": []}
    for tag, mode in (("\u2605 \u7167\u4f8b\u5b50\uff1aPre \u2192 \u9009 SURFACEBODY \u2192 Post", "surfacebody_by_coord"),
                      ("\u5bf9\u7167\uff1aPre \u2192 \u6309\u5bf9\u8c61\u9009\u9762 \u2192 Post", "faces_by_object")):
        ev["cases"].append(_one(sw, tag, mode))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "trim_per_example_works" if ev["passed"] else "still_fails"
    p = R / "output" / "trim-surface-per-example-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-44s ok=%-6s" % (c.get("tag"), c.get("ok")))
        print("        \u9762=%s pre=%s picked=%s sel=%s post=%s" % (
            c.get("surfaces_made"), c.get("pre"), c.get("picked"), c.get("sel"), c.get("post")))
        print("        \u540d=%s \u578b=%s new=%s new_types=%s" % (
            c.get("ret_name"), c.get("ret_type"), c.get("new"), c.get("new_types")))
        for k in ("pre_err", "post_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:120]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
