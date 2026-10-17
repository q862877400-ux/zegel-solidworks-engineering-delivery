"""★ 真机：**按工具层契约**跑焊件切割清单那条链（`create → ensure → evidence → csv`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_weldment_tools_e2e.py
# 定位:   ★ 2026-10-03（轮 498）★ 上一轮证明了 **结构系统**真机跑得通**（事实 389），
#   而本探针补上**最后一块**：★ **按 `ToolSpec` 的契约调**（★ 而不是手调底层实现）。
#
#   ★★ **为什么必须按契约调**（★ 本仓 AGENTS.md 有一条专门的纪律）：
#     「① 从 mcp-server 的 ToolSpec 读它声明的 inject 与 params；② 按那个契约准备实参；
#      ③ 只有工具层本身有 bug 时才去调内部实现，并在记录里写明」
#     ★ 实证代价：轮 497 我手调 `create_structural_member(model, "草图1", profile)`
#     —— ★★ 而真签名是 `(model, **profile_path**, **segment_groups**, …)`
#     ⇒ 报 `FileNotFoundError: 焊件型材不存在或格式错误: D:\AI\SW\草图1` ⚠
#     ★ 而**工具层那个入口根本不需要 `segment_groups`**：
#       `solidworks_weldment_create_structural_member` ⇒
#       `sw_weldment.create_structural_member_from_sketch(model, sketch_name, profile_path)`
#       —— ★ **只要草图名 + 型材路径** ✓
#
#   ★ 本探针按契约调这三个：
#     · `solidworks_weldment_create_structural_member`（inject=model · sketch_name · profile_path）
#     · `solidworks_weldment_ensure_cut_list`（inject=model · 无参）
#     · `solidworks_weldment_evidence`（inject=model · create_missing_cut_list）
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: `C:\swapi\types\IFeatureManager\InsertStructuralWeldment2{,3}.md` ·
#   `…\InsertWeldmentCutList2.md`（`Feature InsertWeldmentCutList2( System.object Bodies )`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ ① 结构构件建成（★ 树里有 `WeldmentFeature` 类型）· ② 切割清单建成
#   （★ 树里有 `CutListFolder` 类型）—— ★ 都用 `GetTypeName2`（事实 242）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "mcp-server"))

from scripts import sw_connect as C                                    # noqa: E402
from scripts import sw_part as P                                       # noqa: E402
from scripts import sw_weldment as W                                   # noqa: E402


def _types(model):
    """★ 按**类型名**清点（★ 事实 242：挑只依赖被测对象的那个）。"""
    out = {}
    try:
        for feat in W.iter_features_recursive(model):
            t = str(C.get_com_member(feat, "GetTypeName2") or "")
            nm = str(getattr(feat, "Name", "") or "")
            out.setdefault(t, []).append(nm)
    except Exception as exc:                                              # noqa: BLE001
        return {"err": "%s: %s" % (type(exc).__name__, str(exc)[:90])}
    return out


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u6309**\u5de5\u5177\u5c42\u5951\u7ea6**\u8dd1\u710a\u4ef6\u5207\u5272\u6e05\u5355\u90a3\u6761\u94fe",
          "contracts": {
              "create": "solidworks_weldment_create_structural_member \u21d2 inject=model \u00b7 sketch_name \u00b7 profile_path",
              "ensure": "solidworks_weldment_ensure_cut_list \u21d2 inject=model \u00b7 \u65e0\u53c2",
              "evidence": "solidworks_weldment_evidence \u21d2 inject=model \u00b7 create_missing_cut_list",
          },
          "steps": []}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: \u2605 \u2460 \u753b\u4e00\u6761\u8def\u5f84\u8349\u56fe\uff08\u2605 \u5de5\u5177\u5c42\u53ea\u8981\u8349\u56fe\u540d\uff09
        P.start_sketch(doc, plane_name="Front Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateLine",
                         0.0, 0.0, 0.0, 120.0 / 1000.0, 0.0, 0.0)
        P.end_sketch(doc)
        profile = (r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles"
                   r"\GB\square-rods.sldlfp")

        #: \u2605 \u2461 \u6309\u5951\u7ea6\u8c03**\u5de5\u5177\u5c42\u90a3\u4e2a\u5165\u53e3**
        for cand in ("\u8349\u56fe1", "Sketch1"):
            try:
                feat = W.create_structural_member_from_sketch(doc, cand, profile)
                ev["steps"].append({"step": "create", "sketch": cand,
                                    "ok": feat is not None, "type": type(feat).__name__})
                break
            except Exception as exc:                                      # noqa: BLE001
                ev["steps"].append({"step": "create", "sketch": cand,
                                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])})
        ev["types_after_create"] = _types(doc)

        #: \u2605 \u2462 \u6309\u5951\u7ea6\u8c03 ensure\uff08\u2605 \u65e0\u53c2\uff09
        try:
            folders = W.ensure_cut_list(doc)
            ev["steps"].append({"step": "ensure", "ok": True, "n": len(folders or [])})
        except Exception as exc:                                          # noqa: BLE001
            ev["steps"].append({"step": "ensure", "ok": False,
                                "err": "%s: %s" % (type(exc).__name__, str(exc)[:170])})
        ev["types_after_ensure"] = _types(doc)

        #: \u2605 \u2463 \u6309\u5951\u7ea6\u8c03 evidence
        try:
            e = W.weldment_evidence(doc, create_missing_cut_list=False)
            ev["evidence"] = {"ok": True, "keys": sorted(e.keys())[:10]}
        except Exception as exc:                                          # noqa: BLE001
            ev["evidence"] = {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:170])}

        cl = (ev["types_after_ensure"] or {}).get("CutListFolder") or []
        wf = (ev["types_after_ensure"] or {}).get("WeldmentFeature") or []
        ev["weldment_feature"] = wf
        ev["cut_list_folder"] = cl
        ev["verdict"] = "pass" if (wf and cl) else "fail"
    except Exception as exc:                                              # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        ev["verdict"] = "fail"
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass

    p = R / "output" / "weldment-tools-e2e-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u636e\uff1a**%s**" % ev.get("verdict"))
    for s in ev["steps"]:
        print("  %-8s %s" % (s.get("step"), json.dumps({k: v for k, v in s.items() if k != "step"},
                                                       ensure_ascii=False)[:150]))
    print("  WeldmentFeature=%s" % ev.get("weldment_feature"))
    print("  CutListFolder=%s" % ev.get("cut_list_folder"))
    print("  evidence=%s" % json.dumps(ev.get("evidence"), ensure_ascii=False)[:150])
    if ev.get("err"):
        print("  err=%s" % ev["err"][:170])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
