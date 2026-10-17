"""★ 对照实验：跑**本仓成功过的曲面特征**（填充曲面）—— 判别"曲面特征能不能建"。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_surface_control.py
# 定位:   ★ 2026-10-03（轮 510）★ 一次**干净的对照实验**。
#
#   ★★ **要判别的问题**（★ 从事实 391 / 393 收窄到这里）：
#     · **流程一样、选区一样、前置一样** —— `CreateDefinition` → （试 `AccessSelections`，失败不管）
#       → **直接 `CreateFeature`**，★ 而本条路**没有设任何属性**
#       （★ 它是 `scripts/sw_sweep.create_sweep_report` 逐字的样子 —— 本轮核实过）
#     · ★ 而**同样的流程**：★ 在 `swFmSweep`（**17 · 实体扫描**）上**成过**；
#       ★★ 而在 `swFmRefSurface`（**62 · 曲面扫描**）· 加厚 · 直纹曲面上**不成** ⚠
#     ⇒ ★★ **故"流程/参数/选择"都被排除，唯一差的是"那个特征类型本身"** ✓
#
#   ★★★ **故本探针问一个更基础的问题**：
#     ★ **在这个新零件里，一个"本仓成功过"的曲面特征，现在还建得成吗？**
#     · ★ 若**它也不成** ⇒ ★ 说明**本机/本会话的曲面特征整体失效**（★ 那是一类环境问题）
#     · ★ 若**它成** ⇒ ★ 说明**曲面特征能建**，★ 而失败的那几条**另有原因**（★ 逐条再查）
#   ⇒ ★ **这是一个二分判别，两边都给出下一步** ✓
#
#   ★ 选**填充曲面**作对照，因为本仓 `sw_surface_features.insert_fill_surface_report` 的
#     注释记着它**真机 PASS 过**（★ 而"本仓成功过"是本实验的前提 —— ★ 不能拿没验过的当对照）。
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

from scripts import sw_connect as C                                    # noqa: E402
from scripts import sw_part as P                                       # noqa: E402
from scripts import sw_surface_features as SF                          # noqa: E402


def _one(sw, tag, fn):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        r = fn(doc)
        row["result"] = {k: v for k, v in (r or {}).items() if k != "\u2605"}
        row["ok"] = bool((r or {}).get("ok"))
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


def _case_fill(doc):
    """★ 对照：**填充曲面**（★ 本仓记着它 PASS 过）——
    ★ 前置：先建一张曲面 + 选出它那一圈边（★ 官方 Remarks：边界边用 **mark=1**）。"""
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
    return SF.insert_fill_surface_report(doc, 2)


def _case_extend(doc):
    """★ 第二个对照：**延伸曲面**（★ 本仓也记着 PASS 过）——
    ★ 前置：先建一张曲面。"""
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
    return SF.insert_extend_surface_report(doc, 5.0)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u5bf9\u7167\uff1a\u672c\u4ed3**\u6210\u529f\u8fc7**\u7684\u66f2\u9762\u7279\u5f81\u8fd8\u5efa\u5f97\u6210\u5417",
          "why": "\u6d41\u7a0b/\u9009\u533a/\u524d\u7f6e\u90fd\u4e00\u6837\uff0c\u552f\u4e00\u5dee\u7684\u662f\u201c\u7279\u5f81\u7c7b\u578b\u672c\u8eab\u201d "
                 "\u21d2 \u5148\u95ee\uff1a\u4e00\u4e2a\u672c\u4ed3\u6210\u529f\u8fc7\u7684\u66f2\u9762\u7279\u5f81\u73b0\u5728\u8fd8\u6210\u5417\uff1f",
          "cases": []}
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u586b\u5145\u66f2\u9762", _case_fill))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u5ef6\u4f38\u66f2\u9762", _case_extend))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "control_alive" if ev["passed"] else "control_also_dead"
    p = R / "output" / "surface-control-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-24s ok=%-6s %s" % (c.get("tag"), c.get("ok"),
                                      json.dumps(c.get("result") or c.get("err"), ensure_ascii=False)[:150]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
