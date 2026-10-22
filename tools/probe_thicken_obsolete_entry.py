"""★ 真机：试**废弃入口** `IModelDoc2.FeatureBossThicken`（3 参）—— 上轮留下的假设。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_thicken_obsolete_entry.py
# 定位:   ★ 2026-10-03（轮 504）★ 验证上一轮**明确留下的假设**：
#
#   ★★ 背景（轮 502-503）：`IFeatureManager.FeatureBossThicken`（7 参）——
#      ★ **前置完美**（`solid = 0 · surface = 1`）、★ 而 **7 组参数组合全部返回 `None`**、
#      树不动、★ 连错误都不报 ⇒ ★ 「不是参数没找对」有据；★ 按**事实 53** 停手。
#      ★ 而那形态与**事实 40**（`IModeler.Create*Surface` 返回 `None` 而几何不变）同族。
#
#   ★★★ **本轮试的假设**（★ 上轮写在函数 docstring 里的）：★
# 「试 `IModelDoc2.FeatureBossThicken` —— ★ 它标 `Obsolete`，而**废弃入口有时在 pywin32
# 上
#      反而更顺** —— ★ 本仓在别处见过这种反转」⚠
#
#   官方签名（`C:\swapi\types\IModelDoc2\FeatureBossThicken.md`，`kind: method`）：
# `void FeatureBossThicken( System.double Thickness, System.int Direction, System.int Fa
# ceIndex )`
#     —— ★ **3 参**（★ 而 `IFeatureManager` 那个是 7 参）
#     ★★ 而 `Obsolete. Superseded by [[IFeatureManager::FeatureBossThicken]]`
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
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

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_features as sf  # noqa: E402


def _build_surface(sw):
    doc = C.new_document(sw, "part")
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.02,
        -0.02,
        0.0,
        0.02,
        0.02,
        0.0,
    )
    P.end_sketch(doc)
    for cand in ("\u8349\u56fe1", "Sketch1"):
        try:
            if sf.create_extruded_surface_report(doc, 20.0, sketch_name=cand).get("ok"):
                break
        except Exception:  # noqa: BLE001
            continue
    return doc


def _one(sw, tag, fn):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = _build_surface(sw)
        row["pre"] = {
            "solid": sf._solid_body_count(doc),
            "surface": sf._surface_body_count(doc),
        }
        before = list(P.feature_names(doc) or [])
        try:
            ret = fn(doc)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            row["code"] = getattr(exc, "args", (None,))[0]
        after = list(P.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["post"] = {
            "solid": sf._solid_body_count(doc),
            "surface": sf._surface_body_count(doc),
        }
        row["ok"] = bool(row["new"])
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
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
        "_": "\u8bd5**\u5e9f\u5f03\u5165\u53e3** IModelDoc2.FeatureBossThicken\uff083 \u53c2\uff09",
        "hypothesis": "\u4e0a\u4e00\u8f6e\u7559\u4e0b\u7684\uff1a\u5e9f\u5f03\u5165\u53e3\u6709\u65f6\u5728 pywin32 \u4e0a\u53cd\u800c\u66f4\u987a",
        "cases": [],
    }
    #: \u2605 \u4e09\u7ec4\uff1a\u2103 \u57fa\u51c6 \u00b7 \u2161 direction=1 \u00b7 \u2
    #: 162 Thickness \u6362\u4e00\u4e2a
    ev["cases"].append(
        _one(
            sw,
            "\u5e9f\u5f03\u5165\u53e3\uff08\u57fa\u51c6\uff09",
            lambda d: C.get_com_member(d, "FeatureBossThicken", 3.0 * 0.001, 0, 0),
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5e9f\u5f03\u5165\u53e3 direction=1",
            lambda d: C.get_com_member(d, "FeatureBossThicken", 3.0 * 0.001, 1, 0),
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5e9f\u5f03\u5165\u53e3 \u539a 5mm",
            lambda d: C.get_com_member(d, "FeatureBossThicken", 5.0 * 0.001, 0, 0),
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "thicken-obsolete-entry-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u6210\u4e86 **%d / %d**" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print(
            "  %-24s ok=%-6s pre=%s \u56de=%-9s new=%s %s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("pre"),
                c.get("returned"),
                c.get("new"),
                (c.get("err") or "")[:80],
            )
        )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
