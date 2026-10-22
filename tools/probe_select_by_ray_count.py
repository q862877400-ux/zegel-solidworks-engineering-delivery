"""★ 真机：`SelectByRay` 之后选区里**到底有几个东西、分别是什么**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_select_by_ray_count.py
# 定位:   ★ 2026-10-03（轮 607）★ 执行**事实 478 留的下一步**。
#
#   ★★ **为什么**：★ 自由样式的五步链（★ 事实 478）里**第 1 步**是
# 「Select the **face**」（★ **单数**），★ 而实测 `GetSelectedObjectCount2(-1)` 回 **2**
#  ⚠
#     ⇒ ★ 故先弄清**那 2 个是什么**（★ 面 + 环？面 + 边？），★ 再决定怎么只留一个。
#
#   ★ 做法：① `ClearSelection2(True)` → ② `SelectByRay(..., Mark=0)` →
#     ③ **逐个** `GetSelectedObjectType3(i, -1)` / `GetSelectedObject6(i, -1)` 枚举。
#     ★ 再试**带 Mark** 与**再清一次**的对照。
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402

#: \u2605 `swSelectType_e` \u91cc\u6700\u5e38\u89c1\u7684\u51e0\u4e2a\uff08\u2605 \u4ece
#: \u53cd\u5c04\uff09
SEL_TYPES = {
    0: "NOTHING",
    1: "EDGE",
    2: "FACE",
    3: "VERTEX",
    4: "DATUMPLANE",
    5: "DATUMAXIS",
    6: "DATUMPOINT",
    7: "BODY",
    8: "SKETCH",
    9: "COMPONENT",
    10: "SKETCHSEGMENT",
    11: "SKETCHPOINT",
    12: "REFCURVE",
    39: "SURFACE",
}


def _box(doc, size=0.03):
    p_.start_sketch(doc, plane_name="Front Plane")
    c_.get_com_member(
        c_.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -size,
        -size,
        0.0,
        size,
        size,
        0.0,
    )
    p_.end_sketch(doc)
    names = [
        n
        for n in (p_.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in ((names[-1] if names else "\u8349\u56fe1"), "\u8349\u56fe1", "Sketch1"):
        try:
            p_.extrude_boss(doc, cand, size * 2.0)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _dump(doc, tag: str) -> dict:
    mgr = c_.get_com_member(doc, "SelectionManager")
    n = int(c_.get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
    out = {"tag": tag, "count": n, "objects": []}
    for i in range(1, n + 1):
        row = {"i": i}
        try:
            t = int(c_.get_com_member(mgr, "GetSelectedObjectType3", i, -1) or -1)
            row["type"] = t
            row["type_name"] = SEL_TYPES.get(t, "?")
        except Exception as exc:  # noqa: BLE001
            row["type_err"] = str(exc)[:70]
        try:
            obj = c_.get_com_member(mgr, "GetSelectedObject6", i, -1)
            row["obj"] = type(obj).__name__ if obj is not None else "None"
            if obj is not None:
                #: \u2605 \u82e5\u662f\u9762\uff0c\u8bfb\u5b83\u81ea\u5df1\u7684\u6210\u
                #: 5458\uff08\u2605 \u4e8b\u5b9e 163\uff1a"
                #: \u2605 \u4e24\u683c\u90fd\u56de\u540c\u4e00\u5bf9\u8c61\u65f6\u5fc5\u
                #: 987b\u8bfb\u90a3\u4e2a\u5bf9\u8c61\u81ea\u5df1\u7684\u6210\u5458\u624
                #: d\u80fd\u533a\u5206\uff09
                for m in ("GetArea", "GetSurface", "Name"):
                    try:
                        v = c_.get_com_member(obj, m)
                        row[m] = (
                            round(float(v), 6)
                            if m == "GetArea" and v is not None
                            else str(v)[:40]
                        )
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            row["obj_err"] = str(exc)[:70]
        out["objects"].append(row)
    return out


def main() -> int:
    sw, _ = c_.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "`SelectByRay` \u4e4b\u540e\u9009\u533a\u91cc**\u5230\u5e95\u6709\u51e0\u4e2a\u3001\u5206\u522b\u662f\u4ec0\u4e48**",
        "cases": [],
    }
    doc = None
    try:
        doc = c_.new_document(sw, "part")
        ev["box"] = _box(doc)
        ext = c_.get_com_member(doc, "Extension")
        #: \u2605 \u56db\u79cd\u53d6\u6cd5\u5bf9\u7167
        for tag, pre_clear, mark in (
            (
                "\u2605 \u4e0d\u6e05\u5c31\u9009\uff08\u2605 \u65e7\u63a2\u9488\u90a3\u6837\uff09",
                False,
                0,
            ),
            ("\u2605 **\u5148\u6e05\u518d\u9009**", True, 0),
            ("\u2605 \u5148\u6e05\u518d\u9009 \u00b7 **Mark=1**", True, 1),
            ("\u2605 \u9009\u5b8c**\u518d\u6e05\u4e00\u6b21**\u518d\u9009", True, 0),
        ):
            if pre_clear:
                try:
                    doc.ClearSelection2(True)
                except Exception:  # noqa: BLE001
                    pass
            ok = c_.get_com_member(
                ext,
                "SelectByRay",
                0.0,
                0.0,
                0.2,
                0.0,
                0.0,
                -1.0,
                1e-4,
                2,
                False,
                int(mark),
                0,
            )
            if tag.endswith("\u518d\u9009"):
                #: \u2605 \u5148\u6e05\u4e00\u6b21\uff08\u2605 \u5206\u79bb\u201c\u4e0a\
                #: u4e00\u6b21\u7684\u6b8b\u7559\u201d\u8fd9\u4e2a\u53d8\u91cf\uff09
                try:
                    doc.ClearSelection2(True)
                except Exception:  # noqa: BLE001
                    pass
                ok = c_.get_com_member(
                    ext,
                    "SelectByRay",
                    0.0,
                    0.0,
                    0.2,
                    0.0,
                    0.0,
                    -1.0,
                    1e-4,
                    2,
                    False,
                    0,
                    0,
                )
            row = _dump(doc, tag)
            row["ray_ok"] = bool(ok)
            ev["cases"].append(row)
    except Exception as exc:  # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    finally:
        if doc is not None:
            try:
                t = str(c_.get_com_member(doc, "GetTitle") or "")
                if t:
                    c_.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    ev["verdict"] = "counts=" + ",".join(str(c.get("count")) for c in ev["cases"])
    p = R / "output" / "select-by-ray-count-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print(
            "  %-44s count=%s ray=%s" % (c.get("tag"), c.get("count"), c.get("ray_ok"))
        )
        for o in c.get("objects") or []:
            print(
                "        [%d] type=%s(%s) obj=%s GetArea=%s Name=%s"
                % (
                    o.get("i"),
                    o.get("type"),
                    o.get("type_name"),
                    o.get("obj"),
                    o.get("GetArea"),
                    o.get("Name"),
                )
            )
    if ev.get("err"):
        print("  err=%s" % ev["err"])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
