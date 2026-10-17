"""★ 真机：**重跑** `ILinearPatternFeatureData.AccessSelections`（★ 目标点名第一族的决定性实验）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_linear_pattern_access_recheck.py
# 定位:   ★ 2026-10-03（轮 547）★ 解一个**直接冲突**。
#
#   ★★★ **冲突是什么**（★ 两边都有真机证据）：
#     · `docs/toolbar-gaps-backend-limits.md` **§二**（轮 484 记，逐字）：
#       ```
#       (model, None)        ⇒ 类型不匹配，位置 2
#       (model, 空Dispatch)  ⇒ **0x80010105**（服务器出现意外情况）  ← 指针族的签名错误码
#       (None, None)         ⇒ 类型不匹配，位置 1
#       ```
#       ⇒ ★ 据此判 **线性阵列族到不了**（★ 而那就是**目标点名第一族**的理由）。
#     · 而**事实 425/426**（轮 545/546，同样真机）：★ `(doc, 空Dispatch)` ⇒ **过 = True**（**6/6**）✓
#
#   ★★ **两个可能**：① ★ **接口不同**（`ILinearPatternFeatureData` vs `ISurfaceCutFeatureData` 那族）；
#     ② ★ 当年那次**有别的毛病**（★ 例如 `data` 不是真拿到、或 model 传错）。
#     ⇒ ★ **本探针就是那个决定性实验**：★ **把 §二 那三种传法在同一个脚本里重跑一遍**。
#
#   ★ 三段（★ 与 §二 逐字对齐，★ 便于直接对照）：
#     ⓐ `(model, None)` · ⓑ `(model, 空Dispatch)` · ⓒ `(None, None)`
#   ★ 并**同时记**：★ `CreateDefinition(6)` 拿到什么 · ★ `data` 的类型名 · ★ 完整错误串。
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **本探针不求建成** —— ★ 它要的是**那个冲突的答案**。

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
from scripts.sw_connect import create_empty_dispatch_variant as _av    # noqa: E402
from scripts import sw_part as P                                      # noqa: E402


SW_FM_LPATTERN = 6


def _mk_solid_with_hole(doc):
    """★ 实体 + 一个可阵列的**小凸台**（★ 阵列要有特征可选）。"""
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    ok = False
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            ok = True
            break
        except Exception:                                                 # noqa: BLE001
            continue
    #: \u2605 \u7b2c\u4e8c\u4e2a\u7279\u5f81\uff08\u2605 \u4f9b\u9635\u5217\uff09
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCircleByRadius",
                     -0.02, 0.0, 0.0, 3.0 / 1000.0)
    P.end_sketch(doc)
    names2 = [n for n in (P.feature_names(doc) or [])
              if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names2[-1] if names2 else "\u8349\u56fe2", "\u8349\u56fe2"):
        try:
            P.extrude_boss(doc, cand, 0.005)
            break
        except Exception:                                                 # noqa: BLE001
            continue
    return ok


def _one(sw, tag, mode):
    row = {"tag": tag, "mode": mode}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["solid"] = _mk_solid_with_hole(doc)
        fm = C.get_com_member(doc, "FeatureManager")
        data = None
        try:
            data = C.get_com_member(fm, "CreateDefinition", SW_FM_LPATTERN)
            row["createdef"] = type(data).__name__ if data is not None else "None"
            if data is not None:
                try:
                    row["data_typename"] = str(data._oleobj_.GetTypeInfo().GetDocumentation(-1)[0])
                except Exception:                                         # noqa: BLE001
                    pass
        except Exception as exc:                                          # noqa: BLE001
            row["createdef_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
        if data is None:
            row["access"] = "no_data"
            return row
        #: \u2605 \u4e09\u79cd\u4f20\u6cd5\uff08\u2605 \u4e0e \u00a7\u4e8c \u9010\u5b57\u5bf9\u9f50\uff09
        try:
            if mode == "model_none":
                r = C.get_com_member(data, "AccessSelections", doc, None)
            elif mode == "model_emptydisp":
                r = C.get_com_member(data, "AccessSelections", doc, _av())
            else:
                r = C.get_com_member(data, "AccessSelections", None, None)
            row["access"] = "ok"
            row["access_returns"] = str(r)
        except Exception as exc:                                          # noqa: BLE001
            row["access"] = "err"
            s = str(exc)
            row["access_err"] = "%s: %s" % (type(exc).__name__, s[:200])
            for tok in ("0x80010105", "0x80028CA0", "80010105", "80028CA0"):
                if tok in s:
                    row["error_code"] = tok
                    break
        try:
            C.get_com_member(data, "ReleaseSelectionAccess")
            row["release"] = "ok"
        except Exception as exc:                                          # noqa: BLE001
            row["release_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:80])
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
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
          "_": "\u91cd\u8dd1 `ILinearPatternFeatureData.AccessSelections`\uff08\u2605 \u89e3\u00a7\u4e8c vs \u4e8b\u5b9e 425/426 \u7684\u51b2\u7a81\uff09",
          "conflict": "toolbar-gaps-backend-limits.md \u00a7\u4e8c\uff08\u8f6e 484\uff09\u8bb0\u300c(model, \u7a7aDispatch) "
                      "\u21d2 0x80010105\u300d\uff1b\u800c\u4e8b\u5b9e 425/426\uff08\u8f6e 545/546\uff09\u6d4b\u51fa\u300c\u8fc7=True\u300d\uff086/6\uff09",
          "cases": []}
    for tag, mode in (("\u2460 (model, None)\uff08\u2605 \u00a7\u4e8c \u7b2c\u4e00\u884c\uff09", "model_none"),
                      ("\u2461 (model, \u7a7aDispatch)\uff08\u2605 \u00a7\u4e8c \u7b2c\u4e8c\u884c\uff09", "model_emptydisp"),
                      ("\u2462 (None, None)\uff08\u2605 \u00a7\u4e8c \u7b2c\u4e09\u884c\uff09", "none_none")):
        ev["cases"].append(_one(sw, tag, mode))
    ev["ok_count"] = sum(1 for c in ev["cases"] if c.get("access") == "ok")
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("linear_pattern_access_works" if ev["ok_count"]
                     else "linear_pattern_access_fails_again")
    p = R / "output" / "linear-pattern-access-recheck-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u8fc7 %d / %d\uff09" % (ev["verdict"], ev["ok_count"], ev["total"]))
    for c in ev["cases"]:
        print("  %-40s CreateDefinition=%s data=%s" % (
            c.get("tag"), c.get("createdef"), str(c.get("data_typename"))[:30]))
        print("        access=%-6s \u56de=%s \u9519\u7801=%s" % (
            c.get("access"), c.get("access_returns"), c.get("error_code")))
        for k in ("createdef_err", "access_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:150]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
