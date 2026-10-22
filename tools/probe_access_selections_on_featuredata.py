"""★ 真机：对"静默 `None`"那几条试 `*FeatureData.AccessSelections`（事实 424 给的新路）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_access_selections_on_featuredata.py
# 定位:   ★ 2026-10-03（轮 545）★ 执行**上一轮（事实 424）给出的那条可试新路**：
#
#   > ★ 对那六条中任一条，**先 `GetDefinition` 拿到数据对象、试 `AccessSelections`** ——
#   >   ★ 而它**能不能过**就是那一族的**直接实验**。
#
#   ★★ **为什么这是那族的直接实验**：
#     · 出厂**类型库**（第 3 源 · 裁决者）证明那六个 `*FeatureData` 接口**都带**
#       `AccessSelections(TopDoc, Component)` + `ReleaseSelectionAccess` ✓
#     · 而 **`IAccessSelections` / `IAccessSelections2` 在类型库里**查不到** ⚠
#       —— ★ 它们**正是 `*FeatureData.AccessSelections` 底下要走的那层**（事实 47 那族）。
#     ⇒ ★ 故**调一次 `*FeatureData.AccessSelections`** 就能回答：
#       ★ **它是走托管层（能过）还是走指针层（`0x80010105`）** ✓
#
#   ★★ **载体选谁**：★ 选 **`InsertCutSurface`（曲面切除）** ——
#     ★ 因为**它回了对象**（事实 406：`Name` = 使用曲面切除1 · `GetTypeName2` = `SurfCut`）
#     ⇒ ★ **故能对它 `GetDefinition` 拿到 `ISurfaceCutFeatureData`** ✓
#     ★ 并**同样试另外两条能拿到对象的**（★ 若 `GetDefinition` 也回对象）。
#
#   ★ 每组都读三段证据：★ `GetDefinition` 回什么 · `AccessSelections` 回什么 / 报什么错 ·
#     ★ 以及**错误码**（★ 事实 47 的 `0x80010105` 是那个指针族的指纹）。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **本探针不求建成** —— ★ 它要的是**那一族能不能过**这一个事实。

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

#: ★ 空 Dispatch 变体（★ 事实 12/33：`VARIANT(VT_DISPATCH, None)`）
from scripts.sw_connect import create_empty_dispatch_variant as _av  # noqa: E402


def _mk(doc):
    """★ 造两张相交曲面（★ 曲面切除的前置）。"""
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


def _mk_faces_and_solid(doc):
    """★ 实体 + 曲面（★ 给加厚/直纹用）。"""
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
            break
        except Exception:  # noqa: BLE001
            continue
    _mk(doc)


def _try_access(doc, feat, label):
    """★ 三段：`GetDefinition` ⇒ `AccessSelections` ⇒ 记账（★ 含错误码）。"""
    out = {"on": label}
    if feat is None:
        out["feat"] = "None"
        return out
    try:
        out["feat"] = "%s / %s" % (
            str(C.get_com_member(feat, "Name")),
            str(C.get_com_member(feat, "GetTypeName2")),
        )
    except Exception:  # noqa: BLE001
        pass
    fd = None
    try:
        fd = C.get_com_member(feat, "GetDefinition")
        out["getdefinition"] = type(fd).__name__ if fd is not None else "None"
    except Exception as exc:  # noqa: BLE001
        out["getdefinition_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
    if fd is None:
        return out
    try:
        r = C.get_com_member(fd, "AccessSelections", doc, _av())
        out["access_returns"] = str(r)
        out["access_ok"] = True
    except Exception as exc:  # noqa: BLE001
        out["access_ok"] = False
        out["access_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        #: \u2605 \u628a\u9519\u7801\u62bd\u51fa\u6765\uff08\u2605 \u4e8b\u5b9e 47 \u768
        #: 4\u6307\u7eb9\u662f 0x80010105\uff09
        s = str(exc)
        for tok in ("0x80010105", "0x80028CA0", "80010105", "80028CA0"):
            if tok in s:
                out["error_code"] = tok
                break
        #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 545\uff09**\u7b2c\u4e8c\u6b21\u8bd5
        #: **\uff1a
        #: \u7b2c\u4e00\u6b21\u4f20 `None` \u21d2 **\u7c7b\u578b\u4e0d\u5339\u914d\uff08
        #: \u4f4d\u7f6e 2\uff09**\uff08\u2605 \u4f4d\u7f6e 2 = `Component`\uff09
        #: \u21d2 \u2605 \u6539\u4f20**\u7a7a Dispatch \u53d8\u4f53**\uff08\u2605 \u4e8b
        #: \u5b9e 12/33 \u90a3\u5957\uff1a
        #: `VARIANT(VT_DISPATCH, None)`\uff09\u3002\u2605 \u800c\u8fd9\u6b63\u662f**\u67
        #: 2c\u4ed3\u73b0\u6210\u7684
        #: `create_empty_dispatch_variant()`** \u2014\u2014 \u2605 \u4e0d\u624b\u6413\uf
        #: f08\u4e8b\u5b9e 418 \u7684\u6559\u8bad\uff09\u3002
        try:
            r2 = C.get_com_member(fd, "AccessSelections", doc, _av())
            out["access2_returns"] = str(r2)
            out["access2_ok"] = True
        except Exception as exc2:  # noqa: BLE001
            out["access2_ok"] = False
            out["access2_err"] = "%s: %s" % (type(exc2).__name__, str(exc2)[:160])
            s2 = str(exc2)
            for tok in ("0x80010105", "0x80028CA0", "80010105", "80028CA0"):
                if tok in s2:
                    out["error_code2"] = tok
                    break
    try:
        C.get_com_member(fd, "ReleaseSelectionAccess")
        out["release"] = "ok"
    except Exception as exc:  # noqa: BLE001
        out["release_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:80])
    return out


def _run(sw, tag, build, entry_call):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        build(doc)
        feat = entry_call(doc)
        row.update(_try_access(doc, feat, tag))
        row["ok"] = bool(row.get("access_ok"))
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
        "_": "\u5bf9\u201c\u9759\u9ed8 None\u201d\u90a3\u51e0\u6761\u8bd5 `*FeatureData.AccessSelections`"
        "\uff08\u2605 \u4e8b\u5b9e 424 \u7ed9\u7684\u65b0\u8def\uff09",
        "why": "\u7c7b\u578b\u5e93\u8bc1\u660e\u90a3\u516d\u4e2a *FeatureData \u90fd\u5e26 AccessSelections\uff1b"
        "\u800c IAccessSelections \u4e0d\u5728\u7c7b\u578b\u5e93\u91cc \u21d2 \u8c03\u4e00\u6b21\u5c31\u80fd\u5206\u8fa8\u8d70\u54ea\u5c42",
        "cases": [],
    }

    def _surfcut(doc):
        from sw_connect import get_com_member as _get
        from sw_connect import out_i4 as _oi4
        from sw_part import _select_com_object as _sel

        _mk(doc)
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            fs = list(_get(b, "GetFaces") or [])
            if fs:
                _sel(fs[0], append=True, mark=0)
            break
        fm = C.get_com_member(doc, "FeatureManager")
        return C.get_com_member(
            fm, "InsertCutSurface", False, 0, False, True, [], _oi4()
        )

    def _thicken(doc):
        _mk_faces_and_solid(doc)
        from sw_connect import get_com_member as _get
        from sw_part import _select_com_object as _sel

        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        n = 0
        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            for f in list(_get(b, "GetFaces") or []):
                if _sel(f, append=(n > 0), mark=0):
                    n += 1
        fm = C.get_com_member(doc, "FeatureManager")
        return C.get_com_member(
            fm, "FeatureBossThicken", 0.003, 0, 0, True, True, False, True
        )

    def _splitline(doc):
        _mk_faces_and_solid(doc)
        from sw_connect import get_com_member as _get
        from sw_part import _select_com_object as _sel

        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        n = 0
        for bt in (0, 1):
            for b in list(_get(doc, "GetBodies2", bt, True) or []):
                for f in list(_get(b, "GetFaces") or []):
                    if _sel(f, append=(n > 0), mark=0):
                        n += 1
        fm = C.get_com_member(doc, "FeatureManager")
        return C.get_com_member(fm, "InsertSplitLineIntersect", 0)

    for tag, build, call in (
        (
            "\u66f2\u9762\u5207\u9664\uff08\u2605 \u5b83\u56de\u5bf9\u8c61\uff09",
            _mk,
            _surfcut,
        ),
        ("\u52a0\u539a", _mk_faces_and_solid, _thicken),
        ("\u5206\u5272\u7ebf\uff08\u4ea4\u53c9\uff09", _mk_faces_and_solid, _splitline),
    ):
        ev["cases"].append(_run(sw, tag, build, call))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["with_fd"] = sum(
        1 for c in ev["cases"] if (c.get("getdefinition") or "None") != "None"
    )
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "access_selections_works"
        if ev["passed"]
        else (
            "no_featuredata_reachable"
            if not ev["with_fd"]
            else "access_selections_fails"
        )
    )
    p = R / "output" / "access-selections-on-featuredata-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08AccessSelections \u8fc7 %d / %d \u00b7 \u62ff\u5230\u6570\u636e\u5bf9\u8c61 %d\uff09"
        % (ev["verdict"], ev["passed"], ev["total"], ev["with_fd"])
    )
    for c in ev["cases"]:
        print("  %-24s \u7279\u5f81=%s" % (c.get("tag"), c.get("feat")))
        print(
            "        GetDefinition=%s \u00b7 AccessSelections \u8fc7=%s"
            % (c.get("getdefinition"), c.get("access_ok"))
        )
        print(
            "        \u56de=%s \u9519\u7801=%s"
            % (c.get("access_returns"), c.get("error_code"))
        )
        for k in ("getdefinition_err", "access_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:140]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
