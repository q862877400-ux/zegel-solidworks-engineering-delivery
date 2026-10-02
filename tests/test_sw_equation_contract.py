"""方程式模块的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_equation_contract.py
# 定位:   守 `scripts/sw_equation.py`（轮 109：从「真缺」档补的第三条能力）。
# 官方签名依据: 出厂反射 `iface_sldworks.txt` + `C:\\swapi\\types\\IEquationMgr\\*.md`
# 许可:   本仓库 MIT。无第三方代码引入。
#
# ★ 本模块**没有真机运行证据**（等级 `stitched`）⇒ **静态判据是它唯一的防线**：
#   参数顺序、`Add2`/`Add` 的取舍、`-1` 的两种语义（末尾 / 失败）、失败必须可见。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from scripts import sw_equation  # noqa: E402


def test_module_uses_add2_not_the_obsolete_add():
    """@brief ★ 官方明写 `Add` 是 `Obsolete. Superseded by Add2` ⇒ 必须用 `Add2`。"""
    t = (REPO_ROOT / "scripts" / "sw_equation.py").read_text(encoding="utf-8")
    assert "Add2" in t
    assert "Obsolete" in t, "来源块应记下「为什么不用 Add」"
    # ⚠ 不许出现**只**调 Add 的写法（`"Add",` 后面紧跟参数）
    assert '"Add",' not in t, "不能用已废弃的 Add"


def test_append_at_end_constant_matches_official_semantics():
    """@brief 官方：`Index = -1` 表示**追加到末尾**。"""
    assert sw_equation.APPEND_AT_END == -1


def test_add_equation_signature_order_follows_official():
    """@brief 官方 `Add2(Int32 Index, String Equation, Bool Solve)` —— 顺序照官方。"""
    params = list(inspect.signature(sw_equation.add_equation).parameters)
    assert params[0] == "model"
    assert params[1] == "equation", "官方第 2 个参数是 Equation"
    assert "index" in params and "solve" in params


class _FakeMgr:
    def __init__(self, ret=0, count=0, equations=None):
        self.calls = []
        self._ret = ret
        self._count = count
        self._eq = equations or []

    def Add2(self, *args):      # noqa: N802
        self.calls.append(("Add2",) + args)
        return self._ret

    def GetCount(self):         # noqa: N802
        return self._count

    def Equation(self, i):      # noqa: N802
        return self._eq[i]

    def Delete(self, i):        # noqa: N802
        self.calls.append(("Delete", i))
        return self._ret

    def EvaluateAll(self):      # noqa: N802
        self.calls.append(("EvaluateAll",))
        return self._ret


class _FakeModel:
    def __init__(self, mgr):
        self._mgr = mgr

    @property
    def GetEquationMgr(self):      # noqa: N802
        return self._mgr


def test_add_equation_passes_official_three_arguments():
    """@brief 三个实参顺序与类型照官方：`(index, equation, solve)`。"""
    mgr = _FakeMgr(ret=2)
    got = sw_equation.add_equation(_FakeModel(mgr), '"B" = 2', index=-1, solve=True)
    assert got == 2
    assert mgr.calls == [("Add2", -1, '"B" = 2', True)]


def test_add_equation_raises_when_official_returns_minus_one():
    """@brief ★ 官方失败返回 `-1` ⇒ **必须抛带原因的错**（不许静默成功）。

    ⚠ 这是本模块最要紧的一条：`-1` 同时是「追加到末尾」的**入参**语义，
    若不区分，失败会被当成"插到了末尾"。
    """
    mgr = _FakeMgr(ret=-1)
    with pytest.raises(RuntimeError) as ei:
        sw_equation.add_equation(_FakeModel(mgr), '"B" = 2')
    msg = str(ei.value)
    assert "双引号" in msg, "要把官方 Remarks 里最常见的失败原因说出来：%s" % msg


def test_add_equation_rejects_blank_string_before_calling_official():
    """@brief 空串提前拦下（不白跑一次 COM）。"""
    mgr = _FakeMgr()
    with pytest.raises(RuntimeError):
        sw_equation.add_equation(_FakeModel(mgr), "   ")
    assert mgr.calls == [], "空串不该真的调官方"


def test_list_equations_uses_getcount_then_indexed_property():
    """@brief `GetCount()` + `Equation[i]`（官方两个成员配合）。"""
    mgr = _FakeMgr(count=3, equations=['"A" = 1', '"B" = 2', '"C" = "A"+1'])
    assert sw_equation.list_equations(_FakeModel(mgr)) == ['"A" = 1', '"B" = 2', '"C" = "A"+1']


def test_delete_and_evaluate_report_failures():
    """@brief 删/求解失败也要抛（`-1` / `None` 都不许静默）。"""
    with pytest.raises(RuntimeError):
        sw_equation.delete_equation(_FakeModel(_FakeMgr(ret=-1)), 5)
    assert sw_equation.evaluate_equations(_FakeModel(_FakeMgr(ret=0))) == 0
    with pytest.raises(RuntimeError):
        sw_equation.evaluate_equations(_FakeModel(_FakeMgr(ret=None)))


def test_missing_manager_raises_diagnosable_error():
    """@brief 拿不到管理器时抛**带原因**的 `RuntimeError`。"""
    with pytest.raises(RuntimeError) as ei:
        sw_equation.list_equations(_FakeModel(None))
    assert "GetEquationMgr" in str(ei.value)


def test_module_declares_verified_with_real_machine_evidence():
    """@brief ★ 等级是 `verified`，且来源块里**写明真机证据从哪来**。

    ⚑ 2026-10-01（轮 116）：由 `stitched` 升为 `verified` ——
    依据是 `tools/verify_equation_smoke.py` 真机 **5/5**（含 `add`→`list` **往返一致**）。
    ⚠ **等级不许往回降**：谁把它改回 `stitched`，这条测试会红。
    """
    t = (REPO_ROOT / "scripts" / "sw_equation.py").read_text(encoding="utf-8")
    assert "验证等级：`verified`" in t, "等级声明必须是 verified"
    assert "verify_equation_smoke" in t, "来源块必须指认真机证据脚本"
    assert "往返一致" in t, "要写明关键证据（往返一致 ⇒ 不是空操作）"
    assert "验证等级：`stitched`" not in t, "不许把等级降回去"
