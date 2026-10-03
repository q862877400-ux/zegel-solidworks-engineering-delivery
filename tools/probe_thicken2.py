"""★ 真机：`IModelDoc2.FeatureBossThicken2`（4 参）——「加厚」的一个**没试过的变体**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_thicken2.py
# 定位:   ★ 2026-10-03（轮 520）★ 用**上一轮留下的方法论**（「拿后缀去类型库里加通配筛一遍」）
#   扫出来的一个**没试过的入口**。
#
#   ★★ **它怎么被找到的**：
#     轮 519 我在「剪裁曲面」上栽了一次 —— 我按**猜的名字** `InsertTrimSurface` 查，
#     查不到就按**铁律 5** 记了「查不到」；★ 而真名（`PreTrimSurface`/`PostTrimSurface`）
#     是从**类型库 dump** 里翻出来的。
#     ⇒ ★★ **教训：铁律 5 的「查不到」应当限定在查过的名字上** ——
#       下一步该是「**拿后缀去类型库里加通配筛一遍**」✓
#
#   ★ 本轮照做（筛 `Surface` / `Trim` / `Radiate` / `Offset` / `Knit` / `Thicken` / `Ruled` / `Planar`），
#     ★★ **立刻抓到一个没试过的入口**：
#     ```
#     FeatureBossThicken   IModelDoc2       in=3   ← ★ 轮 504 试过（3 组，全 None）
#     FeatureBossThicken   IFeatureManager  in=7   ← ★ 轮 502-503 试过（8 组，全 None）
#     FeatureBossThicken2  IModelDoc2       in=4   ← ★★ **没试过！**
#     FeatureCutThicken2   IModelDoc2       in=4   ← ★★ **没试过！**
#     ```
#
#   ⇒ ★★★ **故本探针要问**：★ **`FeatureBossThicken2`（4 参）成不成？**
#     · ★ 若**成** ⇒ ★★ 「加厚到不了」这条（★ 已试 11 组的那条）要**推翻** ✓
#     · ★ 若**不成** ⇒ ★ 那 11 组之上再添几组（★ 而结论更硬）
#
#   ★ 前置（★ 与轮 502-504 同款）：★ **一张曲面体、零个实体** ⇒ 加厚该把它变成实体。
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：**特征树多了新特征**（★ 并记账实体数 / 曲面体数的变化）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                    # noqa: E402
from scripts import sw_part as P                                       # noqa: E402
from scripts import sw_surface_features as SF                          # noqa: E402


def _build_surface(sw):
    doc = C.new_document(sw, "part")
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.02, -0.02, 0.0, 0.02, 0.02, 0.0)
    P.end_sketch(doc)
    for cand in ("\u8349\u56fe1", "Sketch1"):
        try:
            if SF.create_extruded_surface_report(doc, 20.0, sketch_name=cand).get("ok"):
                break
        except Exception:                                                 # noqa: BLE001
            continue
    return doc


def _one(sw, tag, fn):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = _build_surface(sw)
        row["pre"] = {"solid": SF._solid_body_count(doc), "surface": SF._surface_body_count(doc)}
        before = list(P.feature_names(doc) or [])
        try:
            ret = fn(doc)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
            row["code"] = getattr(exc, "args", (None,))[0]
        after = list(P.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["post"] = {"solid": SF._solid_body_count(doc), "surface": SF._surface_body_count(doc)}
        row["ok"] = bool(row["new"])
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
          "_": "\u52a0\u539a\uff1a`IModelDoc2.FeatureBossThicken2`\uff084 \u53c2\uff09\u2014\u2014 **\u6ca1\u8bd5\u8fc7\u7684\u5165\u53e3**",
          "found_by": "\u8f6e 519 \u7684\u6559\u8bad\u21d2\u7528\u901a\u914d\u7b5b\u7c7b\u578b\u5e93\uff0c\u800c\u5b83\u5f53\u573a\u6293\u5230\u8fd9\u4e2a\u540d\u5b57",
          "cases": []}
    #: \u2605 \u2460 4 \u53c2\uff08\u2605 \u7c7b\u578b\u5e93\u8bf4\u7684 in=4\uff09
    ev["cases"].append(_one(sw, "FeatureBossThicken2\uff084 \u53c2\uff09",
                            lambda d: C.get_com_member(d, "FeatureBossThicken2",
                                                       3.0 * 0.001, 0, 0, True)))
    #: \u2605 \u2461 \u53ea\u4f20 3 \u53c2\uff08\u2605 \u56de\u9000\u5230 3 \u53c2\u5f62\u72b6\uff09
    ev["cases"].append(_one(sw, "FeatureBossThicken2\uff083 \u53c2\uff09",
                            lambda d: C.get_com_member(d, "FeatureBossThicken2",
                                                       3.0 * 0.001, 0, 0)))
    #: \u2605 \u2462 \u5bf9\u7167\uff1aFeatureCutThicken2\uff084 \u53c2\uff09
    ev["cases"].append(_one(sw, "FeatureCutThicken2\uff084 \u53c2\uff09",
                            lambda d: C.get_com_member(d, "FeatureCutThicken2",
                                                       3.0 * 0.001, 0, 0, True)))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "thicken2_works" if ev["passed"] else "thicken2_also_fails"
    p = R / "output" / "thicken2-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-32s ok=%-6s pre=%s \u56de=%-8s new=%s post=%s" % (
            c.get("tag"), c.get("ok"), c.get("pre"), c.get("returned"), c.get("new"), c.get("post")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
