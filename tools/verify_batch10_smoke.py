r"""@brief 真机冒烟：**走「工具声明」这条路**调 batch10 的 4 个工具。

## 为什么这条比"直接调函数"更值钱
`tools/verify_bbox_smoke.py` / `verify_hole_standards_smoke.py` 证的是**函数**能用；
本冒烟证的是**声明**能用 —— 即
```
ToolSpec（手抄的参数名 + 注入名） → register_capabilities.RESOLVERS 解析宿主对象 → 真调
```
★ 这条路上**任何一个环节写错**（参数名手抄错、注入名搞错、`read_only` 标错），
`inspect` 那类静态测试**都发现不了** —— 只有真机跑一次才知道。

## 安全
4 个工具**都是查询**（`read_only=True`）⇒ 只读，风险低。
⚠ `bbox` 需要一个**有实体的活动文档** ⇒ 本冒烟**自己建一个临时零件**并在收尾关掉。
`CommandInProgress` + **收尾查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_batch10_smoke.py
# 定位:   给 `mcp-server/tool_specs_batch10.py` 的 4 条声明取**真机**证据
#         （走 `tool_registry` + `RESOLVERS`，**不绕过声明层**）。
# 官方签名依据: 不适用（本冒烟只做调度；被调函数的官方依据在其源码来源块里）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "batch10-smoke-evidence.json"
)


def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。"""
    try:
        from scripts.sw_connect import residual_dialogs
    except ImportError:
        from sw_connect import dismiss_residual_dialogs, residual_dialogs
    #: ★ 2026-10-01（轮 169）：**查到了就点掉**（兜底）——
    #: 只查不点的脚本在真发现弹窗时**什么也没处置**，弹窗还在 ⇒ 下一轮挂在这儿。
    _dialogs, _scanned = residual_dialogs()
    if _dialogs:
        dismiss_residual_dialogs()
    return _dialogs, _scanned


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-44s %s" % ("✓" if ok else "**✗**", name, str(detail)[:72]))

    sw = None
    scratch = None
    try:
        import register_capabilities as rc
        import sw_connect
        from tool_registry import effective_inject

        from scripts import sw_part

        specs = {s.name: s for s in rc.all_specs()}
        mine = [
            specs[n]
            for n in (
                "solidworks_part_bounding_box",
                "solidworks_hole_standards",
                "solidworks_fastener_types",
                "solidworks_fastener_table_types",
            )
        ]
        chk(
            "batch10 的 4 条都在 all_specs() 里",
            len(mine) == 4,
            "all_specs() 共 %d 条" % len(specs),
        )

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        # ── 造前置：一个有实体的临时零件（给 bbox 用）────────────────
        scratch = sw_connect.new_document(sw, "part")
        chk("新建临时零件（给 bbox 造实体）", scratch is not None, "ok")
        if scratch is not None:
            sw_part.start_sketch(scratch)
            sw_part.sketch_corner_rectangle(scratch, 0.0, 0.0, 20.0, 10.0)
            sw_part.end_sketch(scratch)
            sw_part.extrude_boss(scratch, "草图1", 5.0)

        # ── ★ 走「声明 → 解析器 → 调用」这条路 ───────────────────────
        #: 每条的实参（按声明里的参数名给）
        args = {
            "solidworks_part_bounding_box": {},  # 全默认
            "solidworks_hole_standards": {},  # 全默认（0 = 沉头孔）
            "solidworks_fastener_types": {"standard_name": "ANSI Inch"},
            "solidworks_fastener_table_types": {
                "standard_name": "ANSI Inch",
                "fastener_id": 4,
            },
        }
        for spec in mine:
            inj = effective_inject(spec)
            resolver = rc.RESOLVERS.get(inj)
            if resolver is None:
                chk(spec.name, False, "注入名 %r 没有解析器" % inj)
                continue
            # ⚠ 解析器收一个 `_params`（调用方实参）—— 空 dict 即可，
            #   因为本批 4 条的**宿主对象不需要从实参里推**
            host = resolver({})  # ★ 走**真实**解析器
            mod = importlib.import_module("scripts.%s" % spec.module)
            fn = getattr(mod, spec.function)
            kwargs = dict(args[spec.name])
            #: 只传**声明里有的**参数（其余的用默认）—— 这正是"参数名有没有抄错"的检验
            for k in list(kwargs):
                if k not in {p.name for p in spec.params}:
                    chk(spec.name, False, "实参 %r 不在声明里" % k)
                    continue
            t0 = time.time()
            out = fn(host, **kwargs)
            dt = time.time() - t0
            if spec.name == "solidworks_part_bounding_box":
                ok = isinstance(out, dict) and out.get("size")
                detail = "size=%s · %.2fs" % (out.get("size") if ok else out, dt)
            else:
                ok = isinstance(out, list) and len(out) > 0
                detail = "%d 条 · 首项=%s · %.2fs" % (
                    len(out),
                    out[:1] if ok else out,
                    dt,
                )
            chk("★ %s（inject=%s）" % (spec.name, inj), ok, detail)
            ev.setdefault("results", {})[spec.name] = detail
    except Exception as exc:  # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if scratch is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(scratch, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception as exc:  # noqa: BLE001
            print("   ⚠ 收尾关文档失败（请人工确认）：%s" % str(exc)[:90])

    modals, _win_scanned = modal_dialogs()
    chk(
        "★ 收尾无残留模态框（已知事实 64 的检查）",
        (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s"
        % (
            _win_scanned,
            "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals),
        ),
    )

    ev.update(
        passed=sum(1 for c in checks if c),
        total=len(checks),
        verdict="pass" if checks and all(checks) else "fail",
        finished=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print(
        "  ⚠ 只证「声明 → 解析器 → 调用」这条链跑得通；**不证 MCP 协议层**（那要起 server）。"
    )
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
