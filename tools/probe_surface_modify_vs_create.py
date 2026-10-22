"""★ 验证假设：**"改动已有体"成、"新建体"不成**（跑缝合曲面作对照）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_surface_modify_vs_create.py
# 定位:   ★ 2026-10-03（轮 511）★ 验证一个**从差异推出来的假设**。
#
#   ★★ **假设是怎么推出来的**（★ 用上一轮实验的结果作前提）：
#     · 事实 394 证明**本机曲面特征能建**（填充曲面 + 延伸曲面 2/2 成）
#       ⇒ ★ 而它**排除**了「整类失效」。
#     · ★ 于是看**成与不成的差**：
#       ✓ **填充曲面**（`IFillSurfaceFeatureData`）—— ★ **在已有曲面上操作**
#       ✓ **延伸曲面**（`InsertExtendSurface`）—— ★ **改动已有曲面**
#       ✗ **加厚**（`FeatureBossThicken`）—— ★ 把曲面**变成实体**（★ **改变体类型**）
#       ✗ **直纹曲面**（`InsertRuledSurfaceFromEdge2`）—— ★ 从边**长出新曲面**
#       ✗ **扫描曲面**（`CreateDefinition(62)`）—— ★ 从两个草图**新建**
#     ⇒ ★★ **浮现的共同点**：★ **失败的那几条都要"新建一个独立体"**、
#       ★ **而成功的都是"改动已有的体"** ✓
#
#   ★★★ **可验证的形式**：★ 再跑一个**"改动已有体"**的曲面操作 ——
#     选**缝合曲面**（`knit_surfaces_report`），★ 因为本仓记着它 **PASS 过**，且它的语义是
#     「把选中的曲面**缝成一张**」（★ 改动而非新建）。
#     · ★ 若它**成** ⇒ ★ 假设得到支持（★ "改动类成、新建类不成"）
#     · ★ 若它**不成** ⇒ ★ 假设被否证（★ 那就不是"新建/改动"这条线）
#   ⇒ ★ **二分判别，两边都给出下一步** ✓
#
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：**特征树多了新特征**（★ 缝合那条另加 **body 数变少**）。

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
from scripts import sw_surface_features as sf  # noqa: E402


def _mk_two_surfaces(doc):
    """★ 造**两张**曲面（★ 缝合要有两张才缝得起来）。"""
    made = 0
    for i, plane in enumerate(("Front Plane", "Top Plane")):
        try:
            c_.get_com_member(doc, "ClearSelection2", True)
        except Exception:  # noqa: BLE001
            pass
        p_.start_sketch(doc, plane_name=plane)
        c_.get_com_member(
            c_.get_com_member(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.02,
            -0.02,
            0.0,
            0.02,
            0.02,
            0.0,
        )
        p_.end_sketch(doc)
        for cand in ("\u8349\u56fe%d" % (i + 1), "Sketch%d" % (i + 1)):
            try:
                if sf.create_extruded_surface_report(doc, 20.0, sketch_name=cand).get(
                    "ok"
                ):
                    made += 1
                    break
            except Exception:  # noqa: BLE001
                continue
    return made


def _case_knit(doc):
    """★ 对照（**改动已有体**）：把已有曲面**缝成一张**。"""
    n = _mk_two_surfaces(doc)
    r = sf.knit_surfaces_report(doc, 0.001, try_to_form_solid=False)
    r["surfaces_made"] = n
    return r


def main() -> int:
    sw, _ = c_.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u9a8c\u8bc1\uff1a\u300c\u6539\u52a8\u5df2\u6709\u4f53\u300d\u6210 \u00b7 \u300c\u65b0\u5efa\u4f53\u300d\u4e0d\u6210\uff1f\uff08\u8dd1\u7f1d\u5408\u66f2\u9762\uff09",
        "hypothesis": "\u4e0a\u4e00\u8f6e\u7684 2/2 \u6210\u90fd\u662f\u201c\u6539\u52a8\u5df2\u6709\u4f53\u201d\uff1b\u800c\u5931\u8d25\u7684 3 \u6761\u90fd\u8981\u201c\u65b0\u5efa\u72ec\u7acb\u4f53\u201d",
        "cases": [],
    }
    row = {
        "tag": "\u5bf9\u7167\uff1a\u7f1d\u5408\u66f2\u9762\uff08\u6539\u52a8\u5df2\u6709\u4f53\uff09",
        "ok": False,
    }
    doc = None
    try:
        doc = c_.new_document(sw, "part")
        r = _case_knit(doc)
        row["result"] = {k: v for k, v in (r or {}).items() if k != "\u2605"}
        row["ok"] = bool((r or {}).get("ok"))
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(c_.get_com_member(doc, "GetTitle") or "")
                if t:
                    c_.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    ev["cases"].append(row)
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "modify_ok_create_fail" if ev["passed"] else "hypothesis_rejected"
    p = R / "output" / "surface-modify-vs-create-evidence.json"
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
            "  %-34s ok=%-6s %s"
            % (
                c.get("tag"),
                c.get("ok"),
                json.dumps(c.get("result") or c.get("err"), ensure_ascii=False)[:190],
            )
        )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
