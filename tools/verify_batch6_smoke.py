"""真机冒烟：batch6 的 3 个工具（轮 93）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_batch6_smoke.py
# 定位:   给 `mcp-server/tool_specs_batch6.py` 的 3 条声明取**真机**证据
#         （`012` 的教训：**签名兼容 ≠ 能用**，必须真跑）。
# 官方依据: 不适用（调的是本仓库自己的包装函数）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本文件诞生于一次**缺陷发现**：第 4 个候选 `get_mass_property_override_options`
#   真机跑不通（见 `docs/orphan-functions-not-runnable.md`）⇒ 已不纳入本批。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, r"" + _ROOT_S + r"")
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
OUT = Path(r"D:\AI\SW\output\batch6-smoke-evidence.json")
ev, checks = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}, []


def chk(name, ok, detail):
    checks.append(bool(ok))
    ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
    print("   %s %-46s %s" % ("✓" if ok else "**✗**", name, str(detail)[:78]))


sw = None
try:
    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    model = sw_connect.safe_get_com_member(sw, "ActiveDoc")
    chk("连接 + 活动文档", model is not None,
        str(sw_connect.safe_get_com_member(model, "GetTitle")) if model else "无文档")

    from scripts import sw_delivery, sw_export, sw_geometry_selectors

    def timed(fn):
        t0 = time.time()
        try:
            return True, fn(), time.time() - t0
        except Exception as exc:      # noqa: BLE001
            return False, "%s: %s" % (type(exc).__name__, str(exc)[:130]), time.time() - t0

    ok, r, dt = timed(sw_geometry_selectors.available_point_selectors)
    chk("available_point_selectors（无参）", ok and isinstance(r, list) and len(r) > 0,
        "%d 个：%s" % (len(r), r[:3]) if ok and isinstance(r, list) else r)

    ok, r, dt = timed(sw_geometry_selectors.available_direction_selectors)
    chk("available_direction_selectors（无参）", ok and isinstance(r, list) and len(r) > 0,
        "%d 个：%s" % (len(r), r[:3]) if ok and isinstance(r, list) else r)

    if model is not None:
        ok, r, dt = timed(lambda: sw_delivery.collect_assembly_bom(model))
        # 活动文档是零件 ⇒ 期望它**结构化地失败或给空**，而不是崩掉整个冒烟
        chk("collect_assembly_bom（零件上）", ok or "装配" in str(r),
            "%s" % (("行数=%d" % len(r)) if ok and hasattr(r, "__len__") else r))

except Exception as exc:      # noqa: BLE001
    chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
finally:
    try:
        if sw is not None:
            sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass

ev.update(passed=sum(1 for c in checks if c), total=len(checks),
          verdict="pass" if checks and all(checks) else "fail",
          finished=time.strftime("%Y-%m-%d %H:%M:%S"))
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print()
print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
