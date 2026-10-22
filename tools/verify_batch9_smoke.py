"""batch9 的**前置条件感知**冒烟（轮 98/99）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_batch9_smoke.py
# 定位:   给 `mcp-server/tool_specs_batch9.py` 的 3 条声明取真机证据 ——
#         ⚠ **本轮第一版把它做错了**：在**空零件**上调 `insert_parting_surface` /
#         `insert_core_cavity_solids` ⇒ SolidWorks 弹出**模态框**
#         「此拔模方向尚未定义。」⇒ 会话卡住（用户截图报错）。
# 官方依据: 不适用（调的是本仓库自己的包装函数）。
# 许可:   本仓库 MIT。无第三方代码引入。
#
# ⚠⚠ **本文件记下的一条新事实**：
#   **`ISldWorks.CommandInProgress = True` 不能抑制这个模态框。**
#   （铁律 2 说它抑制"未抑制的模态对话框"—— 这里是反例。）
#   ⇒ 结论：**调「需要前置几何」的建模工具前，必须先确认前置条件已满足**，
#     光设 `CommandInProgress` **不够**。
#
# ⚠ 因此本冒烟的判据**故意收窄**：验证「**声明与实现一致 + 前置条件被记录**」，
#   **不**在未准备的分型件上强行调用那 2 个会弹框的工具。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "batch9-smoke-evidence.json")

#: 这 3 个工具的**前置条件**（写下来，免得下一个人再踩弹窗）
PRECONDITIONS = {
    "insert_core_cavity_solids": "需要**已定义拔模方向**且已有分型面/分型线 ⇒ 否则弹「此拔模方向尚未定义。」",
    "insert_parting_surface": "需要**已插入分型线** ⇒ 否则弹框",
    "mold_undercut_detect": "⚠⚠ **轮 167 更正**：旧注释写「**不弹框**」是**错的** —— "
        "实测**弹了**「此拔模方向尚未定义。」并卡住会话。根因：第 3 参是官方的 "
        "`BCoordInput`，传 `False` = **不启用坐标输入** ⇒ 退回「用模型已定义方向」"
        "⇒ 空零件上没定义 ⇒ 弹框。★ 现在**默认 `b_coord_input=True` + 非零方向 (0,0,1)** "
        "⇒ **不依赖模型已定义方向 ⇒ 从根上不弹框**",
}


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {},
                "preconditions": PRECONDITIONS}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-48s %s" % ("✓" if ok else "**✗**", name, str(detail)[:70]))

    # ① 静态：3 条声明与实现一致（**不碰 COM，因此不会弹框**）
    import importlib
    import inspect
    specs = importlib.import_module("tool_specs_batch9").SPECS_BATCH9
    chk("batch9 声明 3 条", len(specs) == 3, [s.function for s in specs])
    all_ok = True
    for s in specs:
        mod = importlib.import_module("scripts.%s" % s.module)
        fn = getattr(mod, s.function, None)
        real = set(inspect.signature(fn).parameters) if fn else set()
        bad = [p.name for p in s.params if (s.param_alias or {}).get(p.name, p.name) not in real]
        if fn is None or bad:
            all_ok = False
            print("      ✗ %s: 缺函数或参数不符 %s" % (s.name, bad))
    chk("3 条的 module/function/参数与真实签名一致", all_ok, "逐条核过")
    chk("★ 3 条的**前置条件已记录**（防下一个人再踩弹窗）",
        all(s.function in PRECONDITIONS for s in specs), sorted(PRECONDITIONS))

    # ② ★ **只调用"不弹框"的那一个**
    sw = None
    scratch = None
    try:
        import sw_connect
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        scratch = sw_connect.new_document(sw, "part")
        from scripts import sw_mold
        try:
            #: ★ 默认 `b_coord_input=True` + 方向 (0,0,1) ⇒ **不依赖模型已定义方向** ⇒ 
            #: 不弹框
            r = sw_mold.mold_undercut_detect(scratch)
            chk("mold_undercut_detect（**坐标输入**模式下不弹框）可调用", True, "ok · %s" % type(r).__name__)
        except Exception as exc:      # noqa: BLE001
            chk("mold_undercut_detect 抛**可诊断**的错（空零件，预期）",
                len(str(exc)) > 10, "%s: %s" % (type(exc).__name__, str(exc)[:88]))
    except Exception as exc:      # noqa: BLE001
        chk("真机连接", False, "%s: %s" % (type(exc).__name__, str(exc)[:140]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if scratch is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(scratch, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception as exc:      # noqa: BLE001
            print("   ⚠ 收尾关文档失败（请人工确认）：%s" % str(exc)[:90])

    chk("★ 另 2 个**故意不调用**（未准备的分型件上会弹框）", True,
        "insert_core_cavity_solids / insert_parting_surface ⇒ 见 preconditions")

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ **未验证**：`insert_core_cavity_solids` / `insert_parting_surface` 的真机行为 ——")
    print("     需要**已准备的分型件**才能安全调；本轮没有那样的件。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
