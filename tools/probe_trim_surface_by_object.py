"""★ 真机：剪裁曲面 —— 照官方例子的**顺序**，而把 `SURFACEBODY` 改成**按对象选**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_trim_surface_by_object.py
# 定位:   ★ 2026-10-03（轮 535）★ 执行**上一轮留在事实 415 里的下一步**：
#
#   > ★ **下一步明确**：★ **按**对象**选曲面体**（★ 而不是按坐标）——
#   >   即 `_select_com_object(surface_body)`。
#
#   ★ 背景（事实 415）：官方例子（第六种源）给出的**调用序**是
#     ```
#     ② PreTrimSurface(False, True, False, False)   ← 先调它（此时未选任何东西）
#     ③ SelectByID2("", "SURFACEBODY", x, y, z, True, 0, Nothing, 0)   ← 选曲面**体**
#     ④ PostTrimSurface(True)
#     ```
#     ★ 而轮 534 我照做时 **`SelectByID2` 五次全失败**（★ 猜的坐标没落在曲面上）
#     ⇒ ★ 故“照例子”那条**没真试到**；★ 本轮**换成按对象选**，把它补上 ✓
#
#   ★ 试的组：
#     ⓐ ★ **Pre → 按对象选曲面体 → Post**（★ 例子的顺序 + 本仓的选法）
#     ⓑ ★ **Pre → 按对象选曲面体 + 面 → Post**（★ 两种都选上）
#     ⓒ 对照：按对象选曲面体 **在 Pre 之前**（★ 即轮 519 那种反序）
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

import scripts.sw_feature_readback as FR  # noqa: E402
import scripts.sw_weldment as W  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_features as SF  # noqa: E402


def _mk_two_crossing_surfaces(doc):
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
        P.start_sketch(doc, plane_name=plane)
        C.get_com_member(
            C.get_com_member(doc, "SketchManager"),
            "CreateCornerRectangle",
            rect[0],
            rect[1],
            0.0,
            rect[2],
            rect[3],
            0.0,
        )
        P.end_sketch(doc)
        names = [
            n
            for n in (P.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        for cand in ((names[-1],) + tuple(names) + ("\u8349\u56fe%d" % (i + 1),))[:4]:
            try:
                if SF.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get(
                    "ok"
                ):
                    made += 1
                    break
            except Exception:  # noqa: BLE001
                continue
    return made


def _pick_bodies_by_object(doc, faces_too=False):
    """★ **按对象**选曲面体（★ 事实 32：实体没有名字 ⇒ 只能按对象选）。"""
    from sw_connect import get_com_member as _get
    from sw_part import _select_com_object as _sel

    n = 0
    for b in list(_get(doc, "GetBodies2", 1, True) or []):
        try:
            if _sel(b, append=(n > 0), mark=0):
                n += 1
        except Exception:  # noqa: BLE001
            continue
        if faces_too:
            try:
                for f in list(_get(b, "GetFaces") or [])[:2]:
                    if _sel(f, append=True, mark=0):
                        n += 1
            except Exception:  # noqa: BLE001
                pass
    return n


def _one(sw, tag, mode):
    row = {"tag": tag, "mode": mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["surfaces_made"] = _mk_two_crossing_surfaces(doc)
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        fm = C.get_com_member(doc, "FeatureManager")
        before = list(FR.feature_names(doc) or [])
        if mode == "pre_then_bodies":
            pre = C.get_com_member(fm, "PreTrimSurface", False, True, False, False)
            row["pre"] = str(pre)
            row["picked"] = _pick_bodies_by_object(doc)
        elif mode == "pre_then_bodies_faces":
            pre = C.get_com_member(fm, "PreTrimSurface", False, True, False, False)
            row["pre"] = str(pre)
            row["picked"] = _pick_bodies_by_object(doc, faces_too=True)
        else:  # bodies_then_pre
            row["picked"] = _pick_bodies_by_object(doc)
            pre = C.get_com_member(fm, "PreTrimSurface", False, True, False, False)
            row["pre"] = str(pre)
        try:
            row["sel"] = int(
                C.get_com_member(
                    C.get_com_member(doc, "SelectionManager"),
                    "GetSelectedObjectCount2",
                    -1,
                )
                or 0
            )
        except Exception:  # noqa: BLE001
            row["sel"] = -1
        post = None
        try:
            post = C.get_com_member(fm, "PostTrimSurface", True)
            row["post"] = type(post).__name__ if post is not None else "None"
            if post is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(C.get_com_member(post, m))
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            row["post_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
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
        row["new_types"] = [t for t in types if "Trim" in t or "Surf" in t]
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
        "_": "\u526a\u88c1\u66f2\u9762\uff1a\u4f8b\u5b50\u7684**\u987a\u5e8f** + \u6309**\u5bf9\u8c61**\u9009\u66f2\u9762\u4f53",
        "why": '\u4e8b\u5b9e 415 \u7684\u4e0b\u4e00\u6b65\uff1a\u8f6e 534 \u7684 `SelectByID2("\u2026SURFACEBODY\u2026")` \u5168\u5931\u8d25'
        "\uff08\u5750\u6807\u731c\u504f\uff09\u21d2 \u6362**\u6309\u5bf9\u8c61\u9009**",
        "cases": [],
    }
    for tag, mode in (
        (
            "\u2605 Pre \u2192 \u6309\u5bf9\u8c61\u9009\u66f2\u9762\u4f53 \u2192 Post",
            "pre_then_bodies",
        ),
        (
            "\u2605 Pre \u2192 \u6309\u5bf9\u8c61\u9009\u4f53+\u9762 \u2192 Post",
            "pre_then_bodies_faces",
        ),
        (
            "\u5bf9\u7167\uff1a\u9009\u4f53 **\u5728 Pre \u4e4b\u524d**",
            "bodies_then_pre",
        ),
    ):
        ev["cases"].append(_one(sw, tag, mode))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "trim_works" if ev["passed"] else "still_fails"
    p = R / "output" / "trim-surface-by-object-evidence.json"
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
            "  %-40s ok=%-6s \u9762=%s picked=%s sel=%s pre=%s post=%s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("surfaces_made"),
                c.get("picked"),
                c.get("sel"),
                c.get("pre"),
                c.get("post"),
            )
        )
        print(
            "        \u540d=%s \u578b=%s new=%s new_types=%s"
            % (c.get("ret_name"), c.get("ret_type"), c.get("new"), c.get("new_types"))
        )
        for k in ("post_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:130]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
