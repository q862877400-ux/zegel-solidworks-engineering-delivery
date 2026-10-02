"""真机冒烟：batch8 的 3 个工具（轮 97）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_batch8_smoke.py
# 定位:   给 `mcp-server/tool_specs_batch8.py` 的 3 条声明取**真机**证据。
# 官方依据: 不适用（调的是本仓库自己的包装函数）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批来自「**只被测试调用**」的池子 ⇒ 有测试不等于跑过真机 ⇒ **必须冒烟**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect

OUT = Path(r"D:\AI\SW\output\batch8-smoke-evidence.json")
ev, checks = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}, []


def chk(name, ok, detail):
    checks.append(bool(ok))
    ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:400]}
    print("   %s %-46s %s" % ("✓" if ok else "**✗**", name, str(detail)[:76]))


sw = None
try:
    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:      # noqa: BLE001
        pass
    model = sw_connect.safe_get_com_member(sw, "ActiveDoc")
    chk("连接 + 活动文档", model is not None,
        str(sw_connect.safe_get_com_member(model, "GetTitle")) if model else "无文档")

    from scripts import sw_costing, sw_review, sw_simulation_study_options

    def timed(fn):
        t0 = time.time()
        try:
            return True, fn(), time.time() - t0
        except Exception as exc:      # noqa: BLE001
            return False, "%s: %s" % (type(exc).__name__, str(exc)[:140]), time.time() - t0

    ok, r, dt = timed(sw_simulation_study_options.list_setter_summary)
    chk("list_setter_summary（无参）", ok and isinstance(r, dict),
        ("%d 键" % len(r)) if ok and isinstance(r, dict) else r)

    if model is not None:
        ok, r, dt = timed(lambda: sw_review.collect_model_summary(model))
        n = len(r.get("features") or []) if ok and isinstance(r, dict) else -1
        chk("★ collect_model_summary（特征树）", ok and isinstance(r, dict) and n >= 0,
            ("%d 个特征 · 键=%s" % (n, sorted(r.keys())[:5])) if ok and isinstance(r, dict) else r)
        ev["feature_count"] = n

        ok, r, dt = timed(lambda: sw_costing.get_costing_manager(model))
        chk("get_costing_manager", ok, ("ok · %s" % type(r).__name__) if ok else r)
    else:
        chk("两个需文档的工具", False, "没有活动文档 ⇒ 本轮判不了")
except Exception as exc:      # noqa: BLE001
    chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
finally:
    try:
        if sw is not None:
            sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
    # ⚠ 本工具**不新建/不修改/不保存**文档 ⇒ 无需关文档。

ev.update(passed=sum(1 for c in checks if c), total=len(checks),
          verdict="pass" if checks and all(checks) else "fail",
          finished=time.strftime("%Y-%m-%d %H:%M:%S"))
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print()
print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
print("  ⚠ 只读性质：不新建/不修改/不保存文档。")
