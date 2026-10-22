r"""@brief 探针：`SldWorks.Simulation` 加载项**为什么取不到** —— 是没加载，还是没许可？

## 为什么（轮 179）
`topology_optimization` 是 `verified`，它的验收命令 `tools/capture_topology_evidence.py`
现在返回：
```
RuntimeError: GetAddInObject('SldWorks.Simulation') 返回 None：
             Simulation 加载项未加载或本机未安装（需 Simulation 许可证）
```
★ 那条限度第 3 条说「用户已在 SolidNetWork License Manager 中调整过许可」⇒ **环境可能变了**。
★ 本探针**分辨两种可能**（不猜）：
```
① **加载项没加载**（程序性的）  ⇒ 试 `ISldWorks.LoadAddIn` / 读 `GetAddInObject` 前后
② **没有许可**（环境性的）      ⇒ 看加载项**能不能被列出**、加载后 `GetAddInObject` 是否变非 None
```

## 判据（可证伪）
```
① `GetAddInObject("SldWorks.Simulation")` 的前后状态（加载**前**应为 None）
② 试 `LoadAddIn(<名字或路径>)` ⇒ 记录返回值与异常
③ 加载后再 `GetAddInObject` ⇒ **变非 None = ① 类（可修）**；仍 None = 更可能是 ② 类
④ 顺带列一下 `ISldWorks.GetUserPreferenceStringValue` 之类**不碰许可**的信息（如果方便）
```

## ⚠ 安全
**只读 + 一次 LoadAddIn 尝试**（不改注册表、不改全局配置）；收尾**轮询点掉**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_simulation_addin_status.py
# 定位:   给 Spec Kit `099` 分辨「拓扑验收变红」是**加载项没加载**还是**许可没了**。
# 官方依据: `ISldWorks.GetAddInObject(String)` / `ISldWorks.LoadAddIn(String)`（出厂反射
#           ）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "simulation-addin-status.json"
)
REFLECT = Path(
    Path(__file__).resolve().parents[1]
    / "_raw"
    / "reflect_sldworks"
    / "iface_sldworks.txt"
)


def show_reflection():
    """★ 从反射里读出 `LoadAddIn` / `GetAddInObject` 的**精确签名**（不猜）。"""
    t = REFLECT.read_text(encoding="utf-8", errors="replace")
    for name in ("LoadAddIn", "GetAddInObject", "GetUserPreferenceStringValue"):
        for line in t.splitlines():
            if re.search(r"\b" + name + r"\s*\(", line):
                print("    反射: %s" % line.strip()[:96])
                break


def main() -> int:
    ev: dict = {}
    print("  ── 官方签名（反射）──")
    if REFLECT.is_file():
        show_reflection()
    print()
    try:
        import sw_connect

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ① 加载前
        def probe():
            try:
                return sw_connect.safe_get_com_member(
                    sw, "GetAddInObject", "SldWorks.Simulation"
                )
            except Exception as exc:  # noqa: BLE001
                return "EXC:%s" % type(exc).__name__

        before = probe()
        ev["before"] = type(before).__name__ if before is not None else None
        print(
            "  ① 加载**前** `GetAddInObject('SldWorks.Simulation')` ⇒ **%s**"
            % ("None" if before is None else type(before).__name__)
        )

        #: ② 试 LoadAddIn（多个候选名 —— ⚠ 都试一遍，看哪个返回 True）
        cands = [
            "SldWorks.Simulation",
            "SolidWorks Simulation",
            "Simulation",
            "COSMOSWorks",
            "SldWorks.SimulationAddin",
        ]
        results = {}
        for cand in cands:
            try:
                r = sw_connect.safe_get_com_member(sw, "LoadAddIn", cand)
                results[cand] = repr(r)
                print("  ② `LoadAddIn(%r)` ⇒ **%r**" % (cand, r))
            except Exception as exc:  # noqa: BLE001
                results[cand] = "EXC:%s" % type(exc).__name__
                print("  ② `LoadAddIn(%r)` ⇒ %s" % (cand, type(exc).__name__))
        ev["load_addin"] = results

        #: ③ 加载后再看
        after = probe()
        ev["after"] = type(after).__name__ if after is not None else None
        print(
            "  ③ 加载**后** ⇒ **%s**"
            % ("None" if after is None else type(after).__name__)
        )
        ev["conclusion"] = (
            "① 类：加载项**能被加载**（可修）"
            if after is not None
            else "② 类：仍取不到 ⇒ 更可能是**许可/安装**问题（环境性）"
        )
        print("  ⇒ 结论：%s" % ev["conclusion"])
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if "sw" in dir() and sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass

    import sw_connect as _sc

    found, dismissed, scanned = _sc.settle_residual_dialogs(settle_seconds=1.0)
    print("  收尾：发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))
    ev["cleanup"] = {"found": found, "scanned": scanned}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
