"""`scripts/sw_isolate.py` 的单元测试（★ 不需要 SolidWorks，纯进程隔离机制）。

## 为什么这个测试重要
```
★ `sw_isolate` 的存在理由是「**COM 是 STA，超时救不了线程**」（AGENTS.md 铁律 2）——
  所以"会弹模态框的调用"必须放到**能被杀掉的地方**。
⇒ ★★ 而这条保障的**核心不变量**是：**超时 ⇒ 子进程被杀 ⇒ 调用方拿到 `timed_out=True`**
   —— ★ 这个不变量**不需要真机就能测**（★ 用一个人为阻塞的夹具函数即可）。
★ 真机三条（子进程能连同一实例 / 卡住不阻塞主进程 / 可被杀）由
  `tools/experiment_subprocess_com.py` 验证（★ 那需要 SolidWorks，不进 pytest）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_isolate.py
# 定位:   守住 `sw_isolate` 的核心不变量（超时即杀、结果可回、错误不吞）。
# 官方依据: 不适用（标准库 `subprocess`）；设计依据见 known-facts 176 与 AGENTS.md 铁律 2
# 许可:   本仓库 MIT。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sw_isolate import ISOLATED_MARKER, run_isolated  # noqa: E402


def test_normal_call_returns_json_able_result():
    """★ 正常路径：结果**跨进程回得来**，且带隔离标记。"""
    r = run_isolated("scripts.sw_connect", "mm", args=[25.4], timeout=60)
    assert r["ok"] is True, r.get("error")
    assert r[ISOLATED_MARKER] is True
    assert r["timed_out"] is False
    assert r["result"] == pytest.approx(0.0254)


def test_timeout_kills_child_and_reports_timed_out():
    """★★★ 核心不变量：**超时 ⇒ `timed_out=True`**（子进程已被杀）。

    ★ 这是与"在同一进程里加超时"的**本质区别** —— 后者救不了挂住的线程（铁律 2）。
    """
    r = run_isolated("tools._stall_fixture", "forever", timeout=3)
    assert r["timed_out"] is True
    assert r["ok"] is False
    assert "超时" in (r.get("error") or "")
    #: ★ 用时应该**接近**超时值（不是 3600s）⇒ 证明它**真的被杀掉了**
    assert r["seconds"] <= 20, "★ 超时没有生效（用时 %s）" % r["seconds"]


def test_child_exception_is_serialized_not_swallowed():
    """★ 子进程里的异常**要回到调用方**（★ 不吞掉 —— 吞掉就变成静默失败了）。"""
    r = run_isolated("scripts.sw_connect", "definitely_not_a_function", timeout=30)
    assert r["ok"] is False
    assert r["timed_out"] is False
    assert r.get("error"), "★ 异常被吞掉了"


def test_missing_module_reports_clearly():
    """★ 模块不存在时要**说清楚**（而不是回一个空结果）。"""
    r = run_isolated("scripts.no_such_module_xyz", "f", timeout=30)
    assert r["ok"] is False
    assert "no_such_module_xyz" in (r.get("error") or "") or "ModuleNotFound" in (
        r.get("error") or "")
