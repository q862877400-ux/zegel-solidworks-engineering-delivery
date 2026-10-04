"""**仿真域的子进程侧工人**：只吃**可 JSON 化**的入参，在子进程里自己重连并干活。

## ★★★ 为什么需要它（与 `sw_isolate` 配套）
```
★ `sw_isolate.run_isolated` 要把参数**跨进程传**（★ 走 stdin/stdout 的 JSON）
⇒ ★★ 而 `sw_simulation.run_analysis_report(study)` 吃的是 **COM 对象** ⇒ **JSON 化不了**。
⇒ ★★★ 所以本模块提供**只吃字符串/数字**的入口：
     子进程 → `connect_solidworks()` 自己连 → `get_study_by_name(sw, name)` → 干活
   ★ 入参全是 `str` / `int` / `float` ⇒ 跨进程无损。
```

## ★★ 为什么这些入口值得单独存在（★ 不是为隔离临时糊的）
```
★ 它们把"**按名字定位研究**"这件事固定下来 —— 而名字是**唯一**跨进程能传的标识
  （★ 与 `specs/141` 的结论一致：`study_name` 是仿真域的稳定句柄）。
★ 于是"会弹模态框的三件事"（建网格 / 跑求解 / 取研究读数）都能被隔离执行 ⇒
  ★ **一次静默的前置不满足 = 一次会话挂起** 这条链条被**结构上切断**（见 known-facts 177）。
```

## ⚠ 本模块的每个函数**都可能在子进程里永久挂住**（★ 那正是它的用途）
```
★ 所以它们**不该被直接调用** —— 应该经 `sw_isolate.run_isolated(...)` 走：
    run_isolated("scripts.sw_simulation_worker", "run_analysis_by_name",
                 args=["Study 1"], timeout=180)
  ⇒ 超时 ⇒ ★ 子进程被杀 ⇒ **会话完好**（★ 实测见 `tests/test_isolate.py`）。
★ 直接调它们 = 放弃了那层保护（★ 只在**你自己**能承受挂起时那么做）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation_worker.py
# 定位:   `sw_isolate` 的**子进程侧入口**：把仿真域"会弹框"的三件事做成 JSON 入参的薄壳。
# 官方依据: 被包住的调用见 `scripts/sw_simulation.py` 的来源块
#          （`ICWStudy.CreateMesh` / `RunAnalysis` / `ICWMesh.ElementCount` / `ICWResults.GetPlotCount`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 直接调用会放弃进程隔离保护 —— 见上。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from typing import Any

from sw_connect import connect_solidworks
from sw_simulation import (
    configure_mesh_settings,
    create_mesh_report,
    get_study_by_name,
    mesh_settings_report,
    mesh_size_report,
    run_analysis_report,
)

__all__ = ["mesh_size_by_name", "create_mesh_by_name", "run_analysis_by_name",
           "mesh_settings_by_name", "configure_mesh_settings_by_name"]


def _study(name: str):
    """在**本进程**里连上 SolidWorks 并按名字取研究。

    ★ 连不上 / 取不到 ⇒ **抛错**（★ 不返回 None —— 让隔离层把错误序列化回调用方）。
    """
    conn = connect_solidworks(wait_seconds=30)
    sw_app = conn[0] if isinstance(conn, tuple) else conn
    if sw_app is None:
        raise RuntimeError("连不上 SolidWorks（connect_solidworks 回了 None）")
    study = get_study_by_name(sw_app, name)
    if study is None:
        raise RuntimeError("找不到研究 %r —— 先建一个（solidworks_simulation_create_study）" % name)
    return study


def mesh_size_by_name(study_name: str, units: int = -1) -> dict[str, Any]:
    """按**研究名**取建议网格尺寸（★ 入参可 JSON 化 ⇒ 可隔离执行）。"""
    return mesh_size_report(_study(study_name), int(units))


def create_mesh_by_name(study_name: str, units: int = 0, element_size: float = 0.0,
                        tolerance: float = 0.0) -> dict[str, Any]:
    """按**研究名**建网格（★ 入参可 JSON 化 ⇒ 可隔离执行）。"""
    return create_mesh_report(_study(study_name), units=int(units),
                              element_size=float(element_size), tolerance=float(tolerance))


def run_analysis_by_name(study_name: str) -> dict[str, Any]:
    """按**研究名**跑求解并回**回读报告**（★ 入参可 JSON 化 ⇒ 可隔离执行）。"""
    return run_analysis_report(_study(study_name))


def mesh_settings_by_name(study_name: str) -> dict[str, Any]:
    """按**研究名**读那一组"决定网格规模"的设置（★ 只读 ⇒ 可隔离执行）。

    ★★ 2026-10-04（接手轮）**为什么要它**：★ 我在主进程里直接读/写这些属性时，
      ★ 有一次**把 SolidWorks 留在了一次长计算里**（主进程被杀、而 SW 自己还在烧 CPU）
      ⇒ ★ 教训：★ **凡可能在 SW 侧触发计算的调用，都要能被子进程隔离层杀掉** ✓
    """
    return mesh_settings_report(_study(study_name))


def configure_mesh_settings_by_name(study_name: str, **settings) -> dict[str, Any]:
    """按**研究名**设那一组网格旋钮（★ 入参可 JSON 化 ⇒ 可隔离执行）。"""
    return configure_mesh_settings(_study(study_name), **settings)
