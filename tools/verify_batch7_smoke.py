"""真机冒烟：batch7 的 3 个工具（轮 96）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_batch7_smoke.py
# 定位:   给 `mcp-server/tool_specs_batch7.py` 的 3 条声明取**真机**证据。
# 官方依据: 不适用（调的是本仓库自己的包装函数）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批的 3 个在 `014` 普查里都判过 `ok`，但**普查不下"可用"结论**
#   ⇒ 这里再单独跑一次（隔离调用，避免普查的状态相关假阳性）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

import json
import sys
import time
from pathlib import Path

#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, r"" + _ROOT_S + r"")
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "batch7-smoke-evidence.json"
)
ev, checks = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}, []


def chk(name, ok, detail):
    checks.append(bool(ok))
    ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
    print("   %s %-46s %s" % ("✓" if ok else "**✗**", name, str(detail)[:76]))


sw = None
try:
    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    model = sw_connect.safe_get_com_member(sw, "ActiveDoc")
    chk(
        "连接 + 活动文档",
        model is not None,
        str(sw_connect.safe_get_com_member(model, "GetTitle")) if model else "无文档",
    )

    from scripts import sw_render_material, sw_review

    def timed(fn):
        t0 = time.time()
        try:
            return True, fn(), time.time() - t0
        except Exception as exc:  # noqa: BLE001
            return (
                False,
                "%s: %s" % (type(exc).__name__, str(exc)[:130]),
                time.time() - t0,
            )

    if model is not None:
        for label, fn in (
            (
                "activate_model_for_preview",
                lambda: sw_review.activate_model_for_preview(model),
            ),
            (
                "clear_selection_for_preview",
                lambda: sw_review.clear_selection_for_preview(model),
            ),
            (
                "refresh_scene_graph",
                lambda: sw_render_material.refresh_scene_graph(model),
            ),
        ):
            ok, r, dt = timed(fn)
            chk(label, ok, ("ok · %s · %.2fs" % (type(r).__name__, dt)) if ok else r)
    else:
        chk("三个工具", False, "没有活动文档 ⇒ 本轮判不了")
except Exception as exc:  # noqa: BLE001
    chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
finally:
    try:
        if sw is not None:
            sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass
    # ⚠ 本工具**不新建、不修改、不保存**任何文档 ⇒ 无需关文档。

ev.update(
    passed=sum(1 for c in checks if c),
    total=len(checks),
    verdict="pass" if checks and all(checks) else "fail",
    finished=time.strftime("%Y-%m-%d %H:%M:%S"),
)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print()
print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
print("  ⚠ 只读性质：本工具不新建/不修改/不保存文档。")
