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
# 定位:   `sw_isolate` 的**子进程侧入口**：把仿真域"会弹框"的三件事做成 JSON 入参的薄
#           壳。
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
    create_mesh_safely,
    get_study_by_name,
    mesh_settings_report,
    mesh_size_report,
    run_analysis_report,
)

__all__ = ["mesh_size_by_name", "create_mesh_by_name", "run_analysis_by_name",
           "mesh_settings_by_name", "configure_mesh_settings_by_name",
           "create_mesh_safely_by_name"]

#: ★★ 忙时**先等多久**再看一眼（秒）—— ★ 真机实测：★ 刚把 SolidWorks 拉起来那几秒它自己
#: 在忙，
  #: 忙检会把正常调用**全拒**（假警报）⇒ ★ 给一个**有界**的等待 ✓
  #: ⚠ ★ **别调太大**：★ 每个入口都要等一次 ⇒ ★ 一次链上五个入口就会变成"五分钟"（实测过
  #: ）✓
  #: ⚠ ★ 也不许**无界**（★ 事实 526 的纪律）✓
BUSY_IDLE_WAIT_S = 8.0


def _busy_guard(idle_wait_s: float | None = None) -> dict[str, Any] | None:
    """★★★ **前置闸：SolidWorks 正忙就别发调用** —— ★ 这是本模块**最重要**的一段。

    ★★★★ 为什么（★ 2026-10-04 真机两连撞 · 事实 526/527）：
      · ★ **SW 正忙时下发 COM 调用**，调用会**卡在跨进程 COM 里**（实测子进程 CPU **0.10 s**、
        `Responding` 却不动）⇒ ★ 而**杀它不一定救得回来**（`subprocess.run` 的超时没杀掉它，
        ★ 手动 `taskkill /F /T` 才一秒杀掉；★★ 而**杀掉后调用方也没恢复**）✓
      · ⇒ ★★★ **唯一可靠的根因处置是"别进去"**：★ 忙 ⇒ **一个 COM 调用都不发**，
        立即回 `SOLIDWORKS_BUSY` ✓
    ★ 判据由 `scripts/sw_busy.py` 给（★ 纯 ctypes 读窗口，★ **不碰 COM** ⇒ 它自己不会卡）✓

    :returns: `None` ⇒ 可以继续；★ 否则回**结构化的拒绝**（★ 调用方看得见"为什么没做"）。
    ★★ 2026-10-04 **补一处**：★ 忙检会**先等一小会儿**（`idle_wait_s`，默认 15 s）——
      ★ 真机实测：★ 我们**刚把 SolidWorks 拉起来**的那几秒它自己在忙 ⇒ 忙检把探针的读数
      **全拒了**（★ 那是**假警报**：它马上就不忙了）⇒ ★ 故给一个**有界**的等待 ✓
      ⚠ ★ 仍然**有界**（★ 事实 526 的纪律：不做无界等待）✓
    """
    try:
        from sw_busy import BUSY_BLOCKED_CODE, solidworks_busy, wait_until_idle

        wait_s = BUSY_IDLE_WAIT_S if idle_wait_s is None else float(idle_wait_s)
        idle = wait_until_idle(timeout=wait_s, interval=2.0)
        if idle.get("idle"):
            return None
        b = idle.get("last") or solidworks_busy()
    except Exception:                                          # noqa: BLE001
        #: ★ 判据自身坏了 ⇒ **不阻断**（★ 与仓内既有纪律一致：判据出错不因此拒服务）
        return None
    return {"ok": False, "blocked": BUSY_BLOCKED_CODE, "busy_detail": b,
            "waited_s": idle.get("waited"),
            "error": "SolidWorks 正忙（★ 等了 %ss）⇒ **不发 COM 调用**"
                     "（★ 忙时调用会卡在跨进程 COM 里、且不一定救得回来）：%s"
                     % (idle.get("waited"), "；".join(b.get("reasons") or [])[:300])}


def _study(name: str, *, sw_app=None):
    """在**本进程**里连上 SolidWorks 并按名字取研究。

    ★ 连不上 / 取不到 ⇒ **抛错**（★ 不返回 None —— 让隔离层把错误序列化回调用方）。
    :param sw_app: ★ 已经连上时可直接传（★ 免得同一进程里连两次）。
    """
    if sw_app is None:
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
    busy = _busy_guard()
    if busy is not None:
        return busy
    return mesh_size_report(_study(study_name), int(units))


def create_mesh_by_name(study_name: str, units: int = 0, element_size: float = 0.0,
                        tolerance: float = 0.0) -> dict[str, Any]:
    """按**研究名**建网格（★ 入参可 JSON 化 ⇒ 可隔离执行）。"""
    busy = _busy_guard()
    if busy is not None:
        return busy
    return create_mesh_report(_study(study_name), units=int(units),
                              element_size=float(element_size), tolerance=float(tolerance))


def run_analysis_by_name(study_name: str) -> dict[str, Any]:
    """按**研究名**跑求解并回**回读报告**（★ 入参可 JSON 化 ⇒ 可隔离执行）。"""
    return run_analysis_report(_study(study_name))


def run_analysis_by_name(study_name: str) -> dict[str, Any]:
    """按**研究名**跑求解并回**回读报告**（★ 入参可 JSON 化 ⇒ 可隔离执行）。"""
    busy = _busy_guard()
    if busy is not None:
        return busy
    return run_analysis_report(_study(study_name))


def mesh_settings_by_name(study_name: str) -> dict[str, Any]:
    """按**研究名**读那一组"决定网格规模"的设置（★ 只读 ⇒ 可隔离执行）。

    ★★ 2026-10-04（接手轮）**为什么要它**：★ 我在主进程里直接读/写这些属性时，
      ★ 有一次**把 SolidWorks 留在了一次长计算里**（主进程被杀、而 SW 自己还在烧 CPU）
      ⇒ ★ 教训：★ **凡可能在 SW 侧触发计算的调用，都要能被子进程隔离层杀掉** ✓
    """
    busy = _busy_guard()
    if busy is not None:
        return busy
    return mesh_settings_report(_study(study_name))


def configure_mesh_settings_by_name(study_name: str, **settings) -> dict[str, Any]:
    """按**研究名**设那一组网格旋钮（★ 入参可 JSON 化 ⇒ 可隔离执行）。"""
    busy = _busy_guard()
    if busy is not None:
        return busy
    return configure_mesh_settings(_study(study_name), **settings)


def create_mesh_safely_by_name(study_name: str, units: int = 0, element_size: float = 0.0,
                               tolerance: float = 0.0,
                               memory_budget_gb: float | None = None) -> dict[str, Any]:
    """★★★ **建网格的唯一推荐入口**（★ 隔离可跑；★ 忙检 → 安全档 → 建网格 → 内存闸 → 还原）。

    ★ 它把事实 526 的两条根因处置串在一条链上（★ 曲率自适应 + 无界加密 ⇒ 爆内存；
      ★ SW 忙时下发调用 ⇒ 卡死），★ 且**用完把网格设置还原**（★ 不离开用户的模型）✓
    ★★ 2026-10-04 修：★ **量预算前置闸要的是零件文档**，不是 study ——
      ★ 第一版传错对象 ⇒ ★ 那道闸在错误对象上取包围盒 ⇒ **静默失效**（见 `create_mesh_safely`）。
      ⇒ ★ 故这里从 `ISldWorks.ActiveDoc` 把文档取出来一起传进去 ✓
      ⚠ ★ 取不到文档 ⇒ **不阻断**，但 `size_gate` 里会**如实记"跳过"** ✓
    """
    busy = _busy_guard()
    if busy is not None:
        return busy
    conn = connect_solidworks(wait_seconds=30)
    sw_app = conn[0] if isinstance(conn, tuple) else conn
    study = _study(study_name, sw_app=sw_app)
    model = None
    try:
        from sw_connect import safe_get_com_member

        model = safe_get_com_member(sw_app, "ActiveDoc")
    except Exception:                                          # noqa: BLE001
        model = None
    return create_mesh_safely(study, model=model, units=int(units),
                              element_size=float(element_size), tolerance=float(tolerance),
                              memory_budget_gb=memory_budget_gb)
