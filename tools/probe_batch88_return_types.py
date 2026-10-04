"""★ 真机验证批 88 里那 4 个"返回可能是 COM 对象"的工具 —— ★ 判据是**能不能过 JSON 边界**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   `mcp-server/tool_specs_batch88.py`（被验的 4 条声明）·
#         `scripts/sw_assembly.py`（get_component_feature / get_component_feature_entity）·
#         `scripts/sw_sketch.py`（get_relation_manager / get_model_to_sketch_transform）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-005 精神；★ **本探针补的是一处明写的缺口**：
#         批 88 的提交信息里写着「这 4 个的**返回可能是 COM 对象**、★ 我的门禁**只看入参**、
#         静态查不到 ⇒ **未做真机验证**」⇒ 本探针就是去补那一刀 ✓
# 官方依据: 各实现的来源块（本探针只按 **ToolSpec 的契约**调，不手调内部实现 —— AGENTS.md 的纪律）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ★ 跑法：`python tools/sw_guard.py --timeout 420 -- python tools/probe_batch88_return_types.py`
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts import sw_connect                                    # noqa: E402
from scripts import sw_part                                       # noqa: E402
import register_capabilities as rc                                # noqa: E402

PART = ROOT / "output" / "_probe_tools_e2e_part_210427.SLDPRT"
ASM = ROOT / "output" / "fr008-assembly-copy.SLDASM"
OUT = ROOT / "output" / "batch88-return-types-evidence.json"


def _verdict(v) -> dict:
    """★★ 判据：返回值**能不能 `json.dumps`**（★ MCP 的边界就是 JSON）。"""
    d = {"type": type(v).__name__}
    try:
        s = json.dumps(v)
        d["json_ok"] = True
        d["json_len"] = len(s)
        d["json_preview"] = s[:180]
    except Exception as exc:                                      # noqa: BLE001
        d["json_ok"] = False
        d["json_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    return d


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "_": "批 88 那 4 个工具的**返回类型**真机读数（判据 = 能不能过 JSON 边界）",
                "tool_count": len(rc.all_specs()), "steps": {}}
    sw = model = None
    opened = []
    try:
        sw, _m, meta = sw_connect.connect_solidworks(wait_seconds=30, return_metadata=True)
        print("★ SW:", meta.get("prog_id"))

        # ── ① 草图那两个：需要**活动草图** ──────────────────────────────
        if PART.is_file():
            model = sw_connect.open_document(sw, PART, silent=True)
            opened.append(str(sw_connect.get_com_member(model, "GetTitle") or ""))
            with sw_part.sketch(model, "前视基准面") as sk_name:
                sw_part.sketch_corner_rectangle(model, -0.01, -0.005, 0.01, 0.005)
                print("★ 开了草图:", sk_name)
                sk = rc.RESOLVERS["sketch"](None)
                for fn_name, module in (("get_relation_manager", "sw_sketch"),
                                        ("get_model_to_sketch_transform", "sw_sketch")):
                    import importlib
                    fn = getattr(importlib.import_module("scripts.%s" % module), fn_name)
                    try:
                        v = fn(sk)
                        ev["steps"]["sketch." + fn_name] = {"ok": True, **_verdict(v)}
                    except Exception as exc:                          # noqa: BLE001
                        ev["steps"]["sketch." + fn_name] = {
                            "ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
                    print("  [草图] %-32s %s" % (fn_name, json.dumps(
                        ev["steps"]["sketch." + fn_name], ensure_ascii=False)[:200]))
            sw_connect.get_com_member(sw, "CloseDoc", str(
                sw_connect.get_com_member(model, "GetTitle") or ""))
            opened.pop()
            model = None

        # ── ② 装配那两个：需要**选中的组件** ────────────────────────────
        if ASM.is_file():
            model = sw_connect.open_document(sw, ASM, silent=True)
            title = str(sw_connect.get_com_member(model, "GetTitle") or "")
            opened.append(title)
            print("★ 开了装配:", title)
            #: ★ 选第一个顶层组件（★ 走官方选择管理器，不裸坐标）
            from scripts.sw_selection import get_selected_component
            comps = []
            try:
                comps = list(sw_connect.get_com_member(model, "GetComponents", True) or [])
            except Exception:                                         # noqa: BLE001
                pass
            sel_mgr = sw_connect.get_com_member(model, "SelectionManager")
            if comps:
                #: ★★ 先**清选区**再选（★ 独立探针里"清着选"时 `selected_count=1`，而这里没落上）
                #: ★ 并**回读计数** —— ★ 判据是回读，不是 `Select` 的返回值（事实 8）✓
                try:
                    sw_connect.get_com_member(model, "ClearSelection2", True)
                except Exception:                                     # noqa: BLE001
                    pass
                try:
                    #: ★ 选实体一律走官方 `ISelectionMgr.AddSelectionListObject`（★ 不裸坐标 —— 规则 3）
                    sw_connect.get_com_member(sel_mgr, "AddSelectionListObject", comps[0],
                                              sw_connect.create_empty_dispatch_variant())
                except Exception as exc:                              # noqa: BLE001
                    print("  ⚠ 选中组件失败:", str(exc)[:140])
                try:
                    ev["steps"]["_selected_count"] = int(sw_connect.get_com_member(
                        sel_mgr, "GetSelectedObjectCount2", -1) or 0)
                except Exception:                                     # noqa: BLE001
                    ev["steps"]["_selected_count"] = -1
                print("  ★ 回读选区计数:", ev["steps"]["_selected_count"])
                #: ★★ `ISelectionMgr` 的 **Index 是 1 基**（实测：count=1 时 index 1 取得到、0 取不到）
                comp = get_selected_component(sel_mgr, 1)
                ev["steps"]["_component_selected"] = comp is not None
                if comp is not None:
                    for fn_name in ("get_component_feature", "get_component_feature_entity"):
                        import importlib
                        fn = getattr(importlib.import_module("scripts.sw_assembly"), fn_name)
                        for aliases in (["凸台-拉伸1", "Boss-Extrude1", "Sketch1", "草图1"],):
                            try:
                                v = fn(comp, aliases, True)
                                ev["steps"]["assembly." + fn_name] = {
                                    "ok": True, "aliases": aliases, **_verdict(v)}
                            except Exception as exc:                      # noqa: BLE001
                                ev["steps"]["assembly." + fn_name] = {
                                    "ok": False, "aliases": aliases,
                                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
                        print("  [装配] %-32s %s" % (fn_name, json.dumps(
                            ev["steps"]["assembly." + fn_name], ensure_ascii=False)[:220]))
            else:
                ev["steps"]["_assembly_note"] = "★ 装配里读不到组件（GetComponents 空）"
    except Exception as exc:                                          # noqa: BLE001
        ev["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:400])
        print("★ 异常:", ev["★_异常"])
    finally:
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
        print("★ wrote", OUT)
        if sw is not None and model is not None:
            try:
                sw_connect.get_com_member(sw, "CloseDoc", str(
                    sw_connect.get_com_member(model, "GetTitle") or ""))
                print("★ 已关件（★ 不保存）")
            except Exception:                                         # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
