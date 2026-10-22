"""★ 真机：`InsertCutSurface` **返回的那个对象是什么**（★ 上一轮留的"新观测"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_cut_surface_returned.py
# 定位:   ★ 2026-10-03（轮 525）★ 执行**上一轮留在事实 405 里的那条下一步**：
#
#   > ★ **下一步该试的**：**把那个 `CDispatch` 读出来**（★ 看它的类型名 / 名字 ⇒
#   >   ★ 可能直接告诉我们"特征建了没有"）。
#
#   ★ 上一轮的观测（★ 事实 405）：
#   ```
#   全选曲面面 mark=0   ⇒ 选中=4 · 回 **None**
#   只选第一张 mark=0   ⇒ 选中=1 · 回 **CDispatch**   ← ★★ 一个对象！
#   只选第一张 mark=1   ⇒ 选中=1 · 回 **CDispatch**
#   全选曲面面 mark=1   ⇒ 选中=4 · 回 **None**
#   ```
#   ⇒ ★★ **参数不变、只动选区，返回值的**种类**就变了** ⇒ 选区真的进去了 ✓
#   ★ 而**那个对象是什么**尚未查明。
#
#   ★ 怎么读（★ 依次试，★ 每一步都记结果）：
#     ⓐ `IFeature.Name` / `GetTypeName2()`（★ 若是 Feature）
#     ⓑ `IEntity.GetType()`（★ 若是 Entity）
#     ⓒ 直接 `repr` 与 `type`
#   ★ 而**关键判据仍是特征树**（★ 事实 404：「调用层通了」与「特征建成」是两件事）——
#     ★ 故本探针**同时回读树**，看那个对象是否**真的对应一个新特征**。
#
#   ⚠ 全程走 `tools/sw_guard.py`。
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

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402


def _mk_solid(doc):
    P.start_sketch(doc, plane_name="Top Plane")
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
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            if sf.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _probe_members(obj):
    """★ 依次试几个**能说明它是什么**的成员（★ 每个都记结果，★ 不猜）。"""
    out = {}
    for label, fn in (
        ("Name", lambda o: c.get_com_member(o, "Name")),
        ("GetTypeName2", lambda o: c.get_com_member(o, "GetTypeName2")),
        ("GetType", lambda o: c.get_com_member(o, "GetType")),
        ("GetID", lambda o: c.get_com_member(o, "GetID")),
    ):
        try:
            v = fn(obj)
            out[label] = str(v)[:80]
        except Exception as exc:  # noqa: BLE001
            out[label] = "ERR %s" % str(exc)[:60]
    return out


def main() -> int:
    sw, _ = c.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "InsertCutSurface \u8fd4\u56de\u7684**\u90a3\u4e2a\u5bf9\u8c61\u662f\u4ec0\u4e48**",
        "why": "\u4e8b\u5b9e 405\uff1a\u53ea\u9009\u4e00\u5f20\u65f6\u56de `CDispatch`\u3001\u5168\u9009\u65f6\u56de `None`",
        "cases": [],
    }
    doc = None
    try:
        doc = c.new_document(sw, "part")
        _mk_solid(doc)
        _mk_surface(doc)
        #: \u2605 \u53ea\u9009**\u7b2c\u4e00\u5f20**\u66f2\u9762\u9762\uff08\u2605 \u4e8
        #: b\u5b9e 405 \u91cc\u56de\u5bf9\u8c61\u7684\u90a3\u79cd\u9009\u6cd5\uff09
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        from sw_connect import get_com_member as _get
        from sw_part import _select_com_object as _sel

        sel = 0
        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            faces = list(_get(b, "GetFaces") or [])
            if faces and _sel(faces[0], append=True, mark=0):
                sel += 1
            break
        ev["selected"] = sel
        before = list(P.feature_names(doc) or [])
        from sw_connect import out_i4 as _oi4

        fm = c.get_com_member(doc, "FeatureManager")
        ret = None
        try:
            ret = c.get_com_member(
                fm, "InsertCutSurface", False, 0, False, True, [], _oi4()
            )
        except Exception as exc:  # noqa: BLE001
            ev["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        ev["returned_type"] = type(ret).__name__ if ret is not None else "None"
        ev["returned_repr"] = repr(ret)[:120]
        if ret is not None:
            ev["members"] = _probe_members(ret)
        after = list(P.feature_names(doc) or [])
        ev["new_features"] = [n for n in after if n not in before]
        ev["tree_after"] = after
        ev["ok"] = bool(ev["new_features"])
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
    p = R / "output" / "cut-surface-returned-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u9009\u4e2d=%s \u00b7 \u8fd4\u56de\u7c7b\u578b=**%s**"
        % (ev.get("selected"), ev.get("returned_type"))
    )
    print("  repr=%s" % str(ev.get("returned_repr"))[:100])
    if ev.get("members"):
        for k, v in ev["members"].items():
            print("     %-14s %s" % (k, v))
    print("  \u7279\u5f81\u6811\u589e\u91cf=%s" % (ev.get("new_features"),))
    print("  \u6811\u672b=%s" % (ev.get("tree_after") or [])[-3:])
    if ev.get("call_err"):
        print("  call_err=%s" % ev["call_err"][:130])
    if ev.get("err"):
        print("  err=%s" % ev["err"][:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
