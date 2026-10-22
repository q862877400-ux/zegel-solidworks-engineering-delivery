"""★ 真机：**批量**测 `*FeatureData.AccessSelections` —— 给「指针族」画确定边界。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_access_selections_matrix.py
# 定位:   ★ 2026-10-03（轮 546）★ 把**事实 425 那条实验批量做**。
#
#   ★★ **为什么能批量**：事实 425 只验了一条（`ISurfaceCutFeatureData` ⇒ **通**）。
#     ★ 而**目标点名**那一族（`IAccessSelections` 指针族）需要**确定的边界**，不是一条样本。
#     ⇒ ★★ **关键手法**：★ **拿「已经建成」的特征当载体** ——
# ★ 它们**都有特征对象** ⇒ ★ **都能 `GetDefinition`** ⇒ ★ **都能测 `AccessSelections`**
# ✓
#       （★ 而加厚 / 分割线**连对象都没有** ⇒ ★ 它们**测不了这一层**，那是另一回事。）
#
#   ★ 载体（★ 全是本仓**真机验过建成**的）：等距曲面 · 平面区域 · 替换面 · 旋转曲面 ·
#     延伸曲面 · 缝合曲面 · 曲面切除。
# ★ 每个测三段：★ `GetDefinition` ⇒ `AccessSelections(doc, 空Dispatch)` ⇒ `ReleaseSelect
# ionAccess`。
# ★★ 而 `Component` **必须传空 Dispatch 变体**（★ 事实 425：传 `None` ⇒ 类型不匹配（位置
#  2））。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **本探针不求建成** —— ★ 它要的是**那一族的边界**这一个事实。

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
from scripts import sw_surface_features as sf  # noqa: E402
from scripts.sw_connect import create_empty_dispatch_variant as _av  # noqa: E402


def _mk_surface(doc, plane="Front Plane", rect=(-0.02, -0.02, 0.02, 0.02), depth=30.0):
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
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            return sf.create_extruded_surface_report(doc, depth, sketch_name=cand)
        except Exception:  # noqa: BLE001
            continue
    return {}


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


def _last_feature(doc, want_types=()):
    """★ 取**最后一个真特征对象**（★ 供 `GetDefinition`）。

    ★★★ 2026-10-03（轮 546）**修**：第一版我传了**猜的类型名**
      （`OffsetSurface` / `ExtendSurface` / `PlanarSurface` / `SewSurface` / `ReplaceFace`）
      ⇒ ★ **六条里五条拿到 `None`**（★ 即**没真试到**）⚠
      ⇒ ★★ **改用「取最后一个真特征」** —— ★ 不猜类型名（★ 而那正是**我老出错的地方**）✓
      ⚠ ★ 教训与事实 418/422 同族：★ **能不用猜的名字就不用**。
    """
    best = None
    try:
        f = C.get_com_member(doc, "FirstFeature")
        while f is not None:
            try:
                nm = str(C.get_com_member(f, "Name") or "")
                tn = str(C.get_com_member(f, "GetTypeName2") or "")
            except Exception:  # noqa: BLE001
                nm, tn = "", ""
            #: \u2605 \u53ea\u6392\u9664**\u5bb9\u5668\u8282\u70b9**\u4e0e**\u57fa\u51c6
            #: \u9762**\uff08\u2605 \u800c\u4e0d\u662f\u6b63\u5411\u7b5b\u7c7b\u578b\uff
            #: 09
            if (
                tn
                and tn not in ("RefPlane", "")
                and not nm.startswith(
                    (
                        "\u524d\u89c6",
                        "\u4e0a\u89c6",
                        "\u53f3\u89c6",
                        "Front",
                        "Top",
                        "Right",
                        "\u539f\u70b9",
                        "Origin",
                    )
                )
            ):
                best = f
            try:
                f = C.get_com_member(f, "GetNextFeature")
            except Exception:  # noqa: BLE001
                break
    except Exception:  # noqa: BLE001
        pass
    return best


def _probe(doc, feat, label):
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
        out["fd"] = type(fd).__name__ if fd is not None else "None"
    except Exception as exc:  # noqa: BLE001
        out["fd_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])
    if fd is None:
        return out
    try:
        r = C.get_com_member(fd, "AccessSelections", doc, _av())
        out["access_ok"] = True
        out["access_returns"] = str(r)
    except Exception as exc:  # noqa: BLE001
        out["access_ok"] = False
        s = str(exc)
        out["access_err"] = "%s: %s" % (type(exc).__name__, s[:140])
        for tok in ("0x80010105", "0x80028CA0", "80010105", "80028CA0"):
            if tok in s:
                out["error_code"] = tok
                break
    try:
        C.get_com_member(fd, "ReleaseSelectionAccess")
        out["release"] = "ok"
    except Exception as exc:  # noqa: BLE001
        out["release_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
    return out


def _run(sw, carrier, build, want_types):
    row = {"carrier": carrier, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        build(doc)
        feat = _last_feature(doc, want_types)
        row.update(_probe(doc, feat, carrier))
        row["ok"] = bool(row.get("access_ok"))
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
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
        "_": "\u6279\u91cf\u6d4b `*FeatureData.AccessSelections`\uff08\u2605 \u7528**\u5df2\u5efa\u6210**\u7684\u7279\u5f81\u5f53\u8f7d\u4f53\uff09",
        "why": "\u4e8b\u5b9e 425 \u53ea\u9a8c\u4e86\u4e00\u6761\uff1b\u76ee\u6807\u70b9\u540d\u90a3\u65cf\u9700\u8981**\u786e\u5b9a\u7684\u8fb9\u754c**",
        "cases": [],
    }

    def _offset(doc):
        _mk_surface(doc)
        return sf.insert_offset_surface_report(doc, 5.0)

    def _extend(doc):
        _mk_surface(doc)
        return sf.insert_extend_surface_report(doc, 5.0)

    def _planar(doc):
        _mk_surface(doc)
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name="Top Plane")
        C.get_com_member(
            C.get_com_member(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.01,
            -0.01,
            0.0,
            0.01,
            0.01,
            0.0,
        )
        P.end_sketch(doc)
        return sf.insert_planar_ref_surface_report(doc)

    def _revolve(doc):
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        C.get_com_member(sm, "CreateCenterLine", 0.0, -0.03, 0.0, 0.0, 0.03, 0.0)
        C.get_com_member(
            sm, "CreateCornerRectangle", 0.005, -0.02, 0.0, 0.02, 0.02, 0.0
        )
        P.end_sketch(doc)
        names = [
            n
            for n in (P.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        ext = C.get_com_member(doc, "Extension")
        for cand in P._get_sketch_name_candidates(
            names[-1] if names else "\u8349\u56fe1"
        ):
            try:
                if P._select_by_id(ext, cand, "SKETCH", append=False, mark=0):
                    break
            except Exception:  # noqa: BLE001
                continue
        import math

        return C.get_com_member(
            doc, "InsertRevolvedRefSurface", math.radians(360.0), False, 0.0, 0
        )

    def _thicken_then_knit(doc):
        _mk_solid(doc)
        _mk_surface(doc, plane="Front Plane")
        _mk_surface(doc, plane="Top Plane", rect=(-0.02, -0.01, 0.02, 0.01))
        return sf.knit_surfaces_report(doc, 0.001, try_to_form_solid=False)

    def _replace_face(doc):
        _mk_solid(doc)
        return sf.insert_replace_face_report(doc)

    CASES = (
        ("\u7b49\u8ddd\u66f2\u9762", _offset, ("OffsetSurface",)),
        ("\u5ef6\u4f38\u66f2\u9762", _extend, ("ExtendSurface",)),
        ("\u5e73\u9762\u533a\u57df", _planar, ("PlanarSurface",)),
        ("\u65cb\u8f6c\u66f2\u9762", _revolve, ("RevolvRefSurf",)),
        ("\u7f1d\u5408\u66f2\u9762", _thicken_then_knit, ("SewSurface", "KnitSurface")),
        ("\u66ff\u6362\u9762", _replace_face, ("ReplaceFace",)),
    )
    for carrier, build, wt in CASES:
        ev["cases"].append(_run(sw, carrier, build, wt))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["with_fd"] = sum(1 for c in ev["cases"] if (c.get("fd") or "None") != "None")
    ev["total"] = len(ev["cases"])
    ev["verdict"] = (
        "access_selections_broadly_works"
        if ev["passed"] >= max(1, ev["with_fd"])
        else "access_selections_partial"
    )
    p = R / "output" / "access-selections-matrix-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08AccessSelections \u8fc7 %d \u00b7 \u62ff\u5230\u5bf9\u8c61 %d / %d\uff09"
        % (ev["verdict"], ev["passed"], ev["with_fd"], ev["total"])
    )
    for c in ev["cases"]:
        print("  %-12s \u7279\u5f81=%s" % (c.get("carrier"), c.get("feat")))
        print(
            "        GetDefinition=%-11s AccessSelections\u8fc7=%-6s \u9519\u7801=%s"
            % (c.get("fd"), c.get("access_ok"), c.get("error_code"))
        )
        for k in ("fd_err", "access_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:130]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
