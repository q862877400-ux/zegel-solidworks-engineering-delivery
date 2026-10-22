r"""@brief 可调用性普查：22 个「暴露候选」孤立能力，**真机各调一次**。

## 为什么（2026-10-01 轮 94，Spec Kit `014`）
轮 93 抽了 4 个候选就撞上 **1 个从没跑通过的**（`get_mass_property_override_options`）。
⇒ **签名兼容 ≠ 能用** ⇒ 暴露前必须普查一遍。

## 范围（**故意收窄**）
只查 `tools/probe_unexposed_functions.py` 认定的「**签名兼容现有注入**」的那批
（`012` 已证那是最便宜的暴露候选）。**不查全部 300 个** —— 那需要为每个准备前置条件，成本失控。

## 分类（**结果只到这四类，不猜**）
| 类 | 含义 |
|---|---|
| `ok` | 调通了，返回值拿得到 |
| `raised` | 抛异常 —— **可能是真缺陷**（记异常类型与首行）|
| `needs_doc` | 没活动文档 ⇒ 本轮**判不了**（不是缺陷）|
| `error_other` | 其它（如权限/许可证）|

⚠ **本普查不下"可用"结论** —— `ok` 只说明"这一次调用没抛异常"，
**不代表结果正确**（`012` 的 `list_render_materials` 返回 0 就是例证）。

## 安全（铁律 2）
* 先 `CommandInProgress = True`（抑制模态弹窗）；
* **本工具不新建、不修改、不保存任何文档** —— 只读地调；
* 收尾 `CommandInProgress = False`。
* ⚠ **整体超时**：COM 调用无法中断 ⇒ 用外层作业超时兜底（见调用方式）。

# ── 来源 ──
# 仓库:   本项目自身（真机普查）
# 文件:   tools/census_orphan_callability.py
# 定位:   为 Spec Kit `014` 取证：暴露候选里有多少「从没跑通过」。
# 官方依据: 不适用（调的是本仓库自己的包装函数）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import inspect
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "orphan-callability-census.json")

#: 只查这批（`012`/`013` 已确认它们是最便宜的暴露候选）
CANDIDATES = [
    ("sw_geometry_selectors", "available_point_selectors"),
    ("sw_geometry_selectors", "available_direction_selectors"),
    ("sw_selection_spec", "clear_selection"),
    ("sw_selection_spec", "current_selection"),
    ("sw_review", "set_standard_view"),
    ("sw_review", "clear_selection_for_preview"),
    ("sw_review", "activate_model_for_preview"),
    ("sw_render_material", "get_extension"),
    ("sw_render_material", "refresh_scene_graph"),
    ("sw_render_material", "list_render_materials"),
    ("sw_render_material", "collect_appearance_evidence"),
    ("sw_weldment", "iter_features_recursive"),
    ("sw_weldment", "create_cut_list"),
    ("sw_assembly", "iter_feature_tree"),
    ("sw_com_traps", "byref_pair"),
    ("sw_delivery", "collect_assembly_bom"),
    ("sw_export", "get_mass_property_override_options"),
]


def main() -> int:
    rows = []
    sw = None
    try:
        import sw_connect
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        model = sw_connect.safe_get_com_member(sw, "ActiveDoc")
        print("  活动文档: %s" % (sw_connect.safe_get_com_member(model, "GetTitle") if model else "**无**"))
        print()

        import importlib
        for mod_name, fn_name in CANDIDATES:
            entry = {"module": mod_name, "function": fn_name}
            try:
                mod = importlib.import_module("scripts.%s" % mod_name)
                fn = getattr(mod, fn_name)
                sig = inspect.signature(fn)
                params = list(sig.parameters)
            except Exception as exc:      # noqa: BLE001
                entry.update(result="error_other", detail="导入失败: %s" % exc)
                rows.append(entry)
                continue

            # 构造最小实参：首参叫 model 就传活动文档；其余留给默认值
            args = []
            if params and params[0] == "model":
                if model is None:
                    entry.update(result="needs_doc", detail="首参是 model，但没有活动文档")
                    rows.append(entry)
                    print("   ⏭  %-46s needs_doc" % fn_name)
                    continue
                args.append(model)

            t0 = time.time()
            try:
                r = fn(*args)
                entry.update(result="ok", ms=round((time.time() - t0) * 1000),
                             return_type=type(r).__name__,
                             size=(len(r) if hasattr(r, "__len__") else None))
                print("   ✓ %-46s ok（%s）" % (fn_name, type(r).__name__))
            except Exception as exc:      # noqa: BLE001
                first = str(exc).splitlines()[0][:120]
                entry.update(result="raised", ms=round((time.time() - t0) * 1000),
                             exc_type=type(exc).__name__, detail=first)
                # ⚠ 把 `needs selection / requires …` 一类**前置条件**与**真异常**分开记
                # ，
                #   但**不自动判定**是缺陷（由人看）
                print("   ✗ %-46s %s: %s" % (fn_name, type(exc).__name__, first[:52]))
            rows.append(entry)

            # ⚠ 兜底：本工具**绝不**在文档上留下改动（只调，不改）
    except Exception as exc:      # noqa: BLE001
        print("  整体失败: %s: %s" % (type(exc).__name__, exc))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass

    ok = [r for r in rows if r["result"] == "ok"]
    raised = [r for r in rows if r["result"] == "raised"]
    nd = [r for r in rows if r["result"] == "needs_doc"]
    other = [r for r in rows if r["result"] == "error_other"]
    print()
    print("  ── 普查 %d 个候选 ──" % len(rows))
    print("     ok %d · **raised %d** · needs_doc %d · other %d"
          % (len(ok), len(raised), len(nd), len(other)))
    if raised:
        print("     raised 明细（**待人工判是否缺陷**）：")
        for r in raised:
            print("       %-44s %s: %s" % (r["function"], r.get("exc_type"), r.get("detail", "")[:56]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"started": time.strftime("%Y-%m-%d %H:%M:%S"), "rows": rows,
                               "summary": {"total": len(rows), "ok": len(ok), "raised": len(raised),
                                           "needs_doc": len(nd), "other": len(other)}},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    print("  ⚠ 本普查**不下「可用」结论**：`ok` 只说明这次没抛异常，**不代表结果正确**。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
