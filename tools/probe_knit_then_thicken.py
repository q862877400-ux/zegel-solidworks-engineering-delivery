"""★ 真机：**先缝合、再加厚**（★ 官方原话里的 "knitted surface" 直指这条路）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_knit_then_thicken.py
# 定位:   ★ 2026-10-03（轮 530）★ 用上一轮挣来的钥匙开另一把锁。
#
#   ★★ **钥匙**（★ 事实 410 固化的教训）：★ **官方原话里的每个名词都要落实**。
#
#   ★★ **锁**：`IFeatureManager.FeatureBossThicken`（加厚）。它到上一轮为止的账是
#     **14 组 / 5 种入口 · 前置每次完美（`solid = 0 · surface = 1`）· 全回 `None`**（事实 401）。
#
#   ★★★ **而官方对该方法 `FillVolume` 参数的原话逐字是**：
#     > "True if you want to make a **solid from the knitted surface**, false if not"
#     ⇒ ★★ **"knitted surface"** —— ★ 那**直指一个前置：先把曲面缝合（knit）成一张** ⚠
#     ★ 而本仓 `knit_surfaces_report` **真机验过能成**（事实 395，`曲面-缝合1` · body 2→1）。
#
#   ★ 而且**那条正是我自己在事实 403 里写下的未查项**：
#     > ⚠ **未查**：① 能否先 `knit` 成一张再加厚…
#   ⇒ ★ 故本轮把它试掉 ✓
#
#   ★ 试的组：
#     ⓐ **先缝合再加厚**（★ 官方原话直指）· `IFeatureManager.FeatureBossThicken`
#     ⓑ **先缝合再加厚** · `IModelDoc2.FeatureBossThicken`（3 参 · 旧式）
#     ⓒ 对照：**不缝合**直接加厚（★ 前几轮那组）
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6 + 事实 406）：**树增量** **或** **返回对象带类型名**；
#   ★ 并记账**实体数 / 曲面体数**的变化（★ 加厚的语义就是那个变化）。

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


def _mk_two_surfaces(doc):
    """★ 造**两张**曲面（★ 缝合要有两张才缝得起来 —— ★ 与事实 395 同款）。"""
    made = 0
    for i, plane in enumerate(("Front Plane", "Top Plane")):
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name=plane)
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                         -0.02, -0.02, 0.0, 0.02, 0.02, 0.0)
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or [])
                 if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
        for cand in ((names[-1],) + tuple(names) + ("\u8349\u56fe%d" % (i + 1),))[:4]:
            try:
                if SF.create_extruded_surface_report(doc, 20.0, sketch_name=cand).get("ok"):
                    made += 1
                    break
            except Exception:                                             # noqa: BLE001
                continue
    return made


def _one(sw, tag, do_knit, entry):
    row = {"tag": tag, "do_knit": do_knit, "entry": entry, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["surfaces_made"] = _mk_two_surfaces(doc)
        row["pre"] = {"solid": SF._solid_body_count(doc), "surface": SF._surface_body_count(doc)}
        if do_knit:
            k = SF.knit_surfaces_report(doc, 0.001, try_to_form_solid=False)
            row["knit"] = {"ok": k.get("ok"), "new": k.get("new_features"),
                           "body_before": k.get("body_before"), "body_after": k.get("body_after")}
            row["after_knit"] = {"solid": SF._solid_body_count(doc),
                                 "surface": SF._surface_body_count(doc)}
        before = list(FR.feature_names(doc) or [])
        ret = None
        try:
            if entry == "modeldoc":
                ret = C.get_com_member(doc, "FeatureBossThicken", 3.0 * 0.001, 0, 0)
            else:
                fm = C.get_com_member(doc, "FeatureManager")
                ret = C.get_com_member(fm, "FeatureBossThicken", 3.0 * 0.001, 0, 0, True,
                                       True, False, True)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(C.get_com_member(ret, m))
                    except Exception:                                     # noqa: BLE001
                        pass
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["post"] = {"solid": SF._solid_body_count(doc), "surface": SF._surface_body_count(doc)}
        #: \u2605\u2605 \u5224\u636e\uff08\u4e8b\u5b9e 406\uff09\uff1a\u6811 \u6216 \u8fd4\u56de\u5bf9\u8c61\u5e26\u7c7b\u578b\u540d \u6216 **\u4f53\u7c7b\u578b\u53d8\u4e86**
        row["ok"] = bool(row["new"] or row.get("ret_type")
                         or row["post"]["solid"] > row["pre"]["solid"])
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
          "_": "\u5148\u7f1d\u5408\u3001\u518d\u52a0\u539a\uff08\u2605 \u5b98\u65b9\u539f\u8bdd\u7684 **knitted surface** \u76f4\u6307\u8fd9\u6761\u8def\uff09",
          "why": "\u4e8b\u5b9e 403 \u91cc\u6211\u81ea\u5df1\u5199\u7684\u672a\u67e5\u9879\uff1a\u80fd\u5426\u5148 knit \u6210\u4e00\u5f20\u518d\u52a0\u539a",
          "cases": []}
    for tag, knit, entry in (("\u2605 **\u5148\u7f1d\u5408** + \u52a0\u539a\uff08IFeatureManager\uff09", True, "featuremanager"),
                             ("\u2605 **\u5148\u7f1d\u5408** + \u52a0\u539a\uff08IModelDoc2 \u65e7\u5f0f\uff09", True, "modeldoc"),
                             ("\u5bf9\u7167\uff1a\u4e0d\u7f1d\u5408\u76f4\u63a5\u52a0\u539a", False, "featuremanager")):
        ev["cases"].append(_one(sw, tag, knit, entry))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "knit_then_thicken_works" if ev["passed"] else "still_fails"
    p = R / "output" / "knit-then-thicken-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-42s ok=%-6s" % (c.get("tag"), c.get("ok")))
        print("        \u9762=%s \u7f1d=%s \u540e=%s \u56de=%-9s \u540d=%s \u578b=%s" % (
            c.get("surfaces_made"), str(c.get("knit"))[:56], c.get("after_knit"),
            c.get("returned"), c.get("ret_name"), c.get("ret_type")))
        print("        new=%s \u4f53 %s\u2192%s" % (c.get("new"), c.get("pre"), c.get("post")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
