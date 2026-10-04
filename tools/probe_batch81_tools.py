"""★ 批 81 工具的**真机抽查**（★ 按 `ToolSpec` 的契约调，不手调内部实现 —— AGENTS.md 的纪律）。

★ 覆盖 5 个只读工具（低风险、无副作用）：
  ① `solidworks_preflight_check_com_dependencies`（★ 纯 Python，不需要 SolidWorks）
  ② `solidworks_feature_list_names`      ← `sw_feature_readback.feature_names(model, limit)`
  ③ `solidworks_feature_present`         ← `…feature_present(model, feature_name)`
  ④ `solidworks_feature_whats_wrong`     ← `…whats_wrong(model)`
  ⑤ `solidworks_review_collect_geometry_measurements` ← `sw_review.collect_geometry_measurements(model)`
⚠ 一律走 `python tools/sw_guard.py --timeout N -- python tools/probe_batch81_tools.py`；
★ 打开的是 `output/` 里的**探针零件**（不是用户原件），且 `finally` 里**关件不保存**。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   `mcp-server/tool_specs_batch81.py`（被验工具的**声明**）·
#         `scripts/sw_feature_readback.py` · `scripts/sw_review.py` · `scripts/sw_preflight.py`（实现）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-005 精神：★ **工具挂上了 ≠ 它真的能用** ⇒ 抽 5 个真机跑 ✓
# 官方依据: 各实现的来源块（本探针只做调用与读数，不新增 API 用法）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
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

import register_capabilities as rc                                # noqa: E402
from scripts import sw_connect                                    # noqa: E402

PART = ROOT / "output" / "_probe_tools_e2e_part_210427.SLDPRT"
OUT = ROOT / "output" / "batch81-tools-evidence.json"


def _spec(name: str):
    return next((s for s in rc.all_specs() if getattr(s, "name", "") == name), None)


def _call(name: str, *, inject_value=None, **kwargs):
    """★ 按 ToolSpec 的契约调：`inject` 决定注入哪个对象，其余按 `param_alias` 映射 ✓"""
    s = _spec(name)
    if s is None:
        return {"ok": False, "error": "工具不在 all_specs() 里"}
    import importlib
    m = importlib.import_module("scripts.%s" % s.module)
    fn = getattr(m, s.function)
    alias = getattr(s, "param_alias", None) or {}
    call_kwargs = {}
    for k, v in kwargs.items():
        call_kwargs[alias.get(k, k)] = v
    if s.inject:
        call_kwargs[s.inject] = inject_value
    try:
        r = fn(**call_kwargs)
        return {"ok": True, "result": r if isinstance(r, (dict, list, str, int, float, bool, type(None)))
                else str(r)[:200]}
    except Exception as exc:                                      # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "_": "批 81 工具的真机抽查（★ 按 ToolSpec 契约调）", "steps": {}}
    sw = model = None
    try:
        #: ① 纯 Python 那个：不用 SolidWorks
        ev["steps"]["preflight_check_com_dependencies"] = _call(
            "solidworks_preflight_check_com_dependencies")
        print("  [1] preflight:", json.dumps(ev["steps"]["preflight_check_com_dependencies"],
                                            ensure_ascii=False)[:180])

        sw, model, meta = sw_connect.connect_solidworks(wait_seconds=30, return_metadata=True)
        print("  [2] SW:", meta.get("prog_id"))
        if not PART.is_file():
            ev["★_异常"] = "探针零件不存在: %s" % PART
            print("★ 零件不存在 ⇒ 只做纯 Python 那一步")
        else:
            model = sw_connect.open_document(sw, PART, silent=True)
            title = ""
            try:
                title = str(sw_connect.get_com_member(model, "GetTitle") or "")
            except Exception:                                       # noqa: BLE001
                pass
            print("  [2b] 打开:", title)
            for key, tool, kw in (
                ("feature_list_names", "solidworks_feature_list_names", {"limit": 400}),
                ("feature_present__Front_Plane", "solidworks_feature_present",
                 {"feature_name": "前视基准面"}),
                ("feature_present__NoSuchFeature", "solidworks_feature_present",
                 {"feature_name": "绝对不存在的特征名_XYZ"}),
                ("whats_wrong", "solidworks_feature_whats_wrong", {}),
                ("collect_geometry_measurements", "solidworks_review_collect_geometry_measurements", {}),
            ):
                r = _call(tool, inject_value=model, **kw)
                ev["steps"][key] = {"tool": tool, **r}
                brief = json.dumps(r, ensure_ascii=False)[:220]
                print("  [3] %-34s %s" % (key, brief))
    except Exception as exc:                                         # noqa: BLE001
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
            except Exception:                                        # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
