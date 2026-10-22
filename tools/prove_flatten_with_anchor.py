"""★ 真机：曲面展平 —— **补 `mark = 16`（锚点）**（★ 事实 434 说缺的就是它）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_flatten_with_anchor.py
# 定位:   ★ 2026-10-03（轮 556）★ 执行**事实 434 留的下一步**。
#
#   ★★ 事实 434 已把入口与 arity 定死：
#     · `InsertFlattenSurface2(AccuracyFactor, ShouldUseTears)` —— **2 参**；
#     · 面-only（mark=1）**不够** ⇒ ★ 而官方 Remarks 还列了
#       **2 = 引导边 · 4 = 映射边 · 8 = 撕裂边 · 16 = 锚点**。
#
#   ★ 本探针照"最可能的那个"补：★ **锚点 `mark = 16`**（★ 展平总得从一个点开始铺）。
#   ★ 试四组（★ 每组**新开一个文档**）：
#     ⓐ 面(mark=1) + **顶点(mark=16)**
#     ⓑ 面(mark=1) + **边(mark=2)**（★ 引导边）
#     ⓒ 面(mark=1) + 顶点(16) + 边(2)
#     ⓓ 对照：只给面(mark=1)（★ 即事实 434 那组）
#
#   ★ 判据（★ 规则 6 + 事实 420）：**树增量** **或** **返回对象带类型名**。
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

import scripts.sw_feature_readback as fr  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402


def _mk_surface(doc):
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateLine",
        -0.03,
        0.0,
        0.0,
        0.03,
        0.0,
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
            return sf.create_extruded_surface_report(doc, 40.0, sketch_name=cand)
        except Exception:  # noqa: BLE001
            continue
    return {}


def _one(sw, tag, want_vertex, want_edge):
    row = {"tag": tag, "anchor": want_vertex, "guide": want_edge, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["surface"] = bool((_mk_surface(doc) or {}).get("ok"))
        from sw_connect import get_com_member as _get
        from sw_part import _select_com_object as _sel

        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        marks = {}
        #: \u2605 mark=1 \u2014\u2014 \u8981\u5c55\u5e73\u7684\u9762
        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            fs = list(_get(b, "GetFaces") or [])
            if fs and _sel(fs[0], append=False, mark=1):
                marks["1"] = 1
            #: \u2605 mark=16 \u2014\u2014 \u951a\u70b9\uff08\u2605 \u7528\u8be5\u66f2\u
            #: 9762\u7684**\u4e00\u4e2a\u9876\u70b9**\uff09
            if want_vertex:
                for e in list(_get(b, "GetEdges") or [])[:1]:
                    for m in ("GetStartVertex", "GetEndVertex"):
                        try:
                            v = _get(e, m)
                            if v is not None and _sel(v, append=True, mark=16):
                                marks["16"] = 1
                                break
                        except Exception:  # noqa: BLE001
                            continue
                    if "16" in marks:
                        break
            #: \u2605 mark=2 \u2014\u2014 \u5f15\u5bfc\u8fb9
            if want_edge:
                for e in list(_get(b, "GetEdges") or [])[:1]:
                    try:
                        if _sel(e, append=True, mark=2):
                            marks["2"] = 1
                    except Exception:  # noqa: BLE001
                        pass
            break
        row["marks"] = marks
        before = list(fr.feature_names(doc) or [])
        fm = _get(doc, "FeatureManager")
        ret = None
        try:
            ret = _get(fm, "InsertFlattenSurface2", 4, False)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_get(ret, m))
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        after = list(fr.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"] or row.get("ret_type"))
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
        "_": "\u66f2\u9762\u5c55\u5e73\uff1a**\u8865 mark\uff08\u951a\u70b9 16 / \u5f15\u5bfc\u8fb9 2\uff09**\uff08\u2605 \u4e8b\u5b9e 434 \u7684\u4e0b\u4e00\u6b65\uff09",
        "official": "\u7b2c\u4e8c\u4ee3 2 \u53c2\uff1bmark\uff1a1=\u9762 \u00b7 2=\u5f15\u5bfc\u8fb9 \u00b7 4=\u6620\u5c04\u8fb9 \u00b7 8=\u6495\u88c2\u8fb9 \u00b7 **16=\u951a\u70b9**",
        "cases": [],
    }
    for tag, v, e in (
        ("\u2460 \u9762 + **\u951a\u70b9(16)**", True, False),
        ("\u2461 \u9762 + **\u5f15\u5bfc\u8fb9(2)**", False, True),
        ("\u2462 \u9762 + \u951a\u70b9(16) + \u5f15\u5bfc\u8fb9(2)", True, True),
        (
            "\u2463 \u5bf9\u7167\uff1a\u53ea\u7ed9\u9762(1)\uff08\u2605 \u4e8b\u5b9e 434 \u90a3\u7ec4\uff09",
            False,
            False,
        ),
    ):
        ev["cases"].append(_one(sw, tag, v, e))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "flatten_with_marks_works" if ev["passed"] else "still_fails"
    p = R / "output" / "flatten-with-anchor-evidence.json"
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
        print("  %-42s ok=%-6s marks=%s" % (c.get("tag"), c.get("ok"), c.get("marks")))
        print(
            "        \u65b0\u589e=%s \u540d=%s \u578b=%s"
            % (c.get("new"), c.get("ret_name"), c.get("ret_type"))
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
