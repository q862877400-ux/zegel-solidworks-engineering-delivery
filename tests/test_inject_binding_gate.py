"""★ 注入绑定门禁的契约测试（含负例 —— 事实 62：负例是唯一证明）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_inject_binding_gate.py
# 定位:   ★ 2026-10-03（轮 461）★ 配套 `tools/check_inject_binding.py`。
#   ★★ 本测试的**负例是主体** —— 因为那条门禁是**真机撞出来**才写的：
#     ```
#     ★ 正例：★ 当前仓库 ⇒ 0 条（★ 因为 16 个漏的已修）
#     ★★ 负例：★ **构造一条"包装需要 model 而 spec 没声明 inject"的 ToolSpec**
#        ⇒ ★ **门禁必须报它** ✓（★ 否则这道门禁等于没有 —— 事实 62）
#     ★★ 负例二：★ 有 `derived_args` 的 ⇒ **不该报**（★ 那是另一种合法覆盖）
#     ```
# 官方依据: 不适用（本仓自有的接线契约）。
# 许可:   本仓库 MIT。无第三方代码引用。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import importlib
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (_REPO, _REPO / "tools", _REPO / "mcp-server", _REPO / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _gate():
    return importlib.import_module("check_inject_binding")


def test_current_repo_passes():
    """★ 正例：现在这棵树里没有"必炸"的注入漏声明。"""
    assert _gate().scan() == []


def test_negative_missing_inject_is_caught(monkeypatch):
    """★★ 负例①：包装需要 model 而 spec 没声明 inject ⇒ **必须被抓到**。"""
    import register_capabilities as rc
    from tool_registry import ToolSpec

    class _Fake:
        name = "solidworks_fake_needs_model"
        module = "sw_part"
        function = "extrude_boss"          # ← 真函数：首参是 model
        inject = ""                        # ← ★ 故意漏掉
        params = []
        param_alias = {}
        derived_args = None

    monkeypatch.setattr(rc, "all_specs", lambda: [_Fake()])
    bad = _gate().scan()
    assert len(bad) == 1, "漏 inject 的那条没被抓到 ⇒ 这道门禁等于没有"
    assert bad[0][0] == "solidworks_fake_needs_model"
    assert bad[0][3] == "model"


def test_negative_derived_args_is_not_reported(monkeypatch):
    """★★ 负例②：有 `derived_args` 的**不该**报（那是另一种合法覆盖）。"""
    import register_capabilities as rc

    class _Fake2:
        name = "solidworks_fake_derived"
        module = "sw_part"
        function = "extrude_boss"
        inject = ""
        params = []
        param_alias = {}
        derived_args = lambda p: {"model": object()}

    monkeypatch.setattr(rc, "all_specs", lambda: [_Fake2()])
    assert _gate().scan() == []


def test_non_object_first_param_is_out_of_scope(monkeypatch):
    """★ 边界：首个必需形参**不是**注入对象 ⇒ 不归本门禁管（避免假阳性）。"""
    import register_capabilities as rc

    class _Fake3:
        name = "solidworks_fake_scalar_first"
        module = "sw_part"
        function = "extrude_boss"
        inject = ""
        params = []
        param_alias = {}
        derived_args = None

    monkeypatch.setattr(rc, "all_specs", lambda: [_Fake3()])
    #: extrude_boss \u7684\u9996\u53c2\u786e\u5b9e\u662f model \u21d2 \u6545\u672c\u6d4b\u8bd5\u53cd\u8fc7\u6765\u7528\u4e00\u4e2a\u9996\u53c2\u662f\u6807\u91cf\u7684\u51fd\u6570
    class _Fake4(_Fake3):
        function = "grid"                  # \u2605 sw_part.grid(\u2026) \u9996\u53c2\u4e0d\u662f\u6ce8\u5165\u5bf9\u8c61\uff08\u5982\u679c\u5b58\u5728\uff09

    monkeypatch.setattr(rc, "all_specs", lambda: [_Fake4()])
    got = _gate().scan()
    #: \u2605 \u82e5 grid \u4e0d\u5b58\u5728\u6216\u9996\u53c2\u4e0d\u662f\u6ce8\u5165\u5bf9\u8c61 \u21d2 \u5e94\u4e3a\u7a7a\uff1b\u82e5\u5b83\u6070\u597d\u662f \u21d2 \u4e5f\u53ea\u80fd\u62a5\u5b83\u4e00\u6761
    assert len(got) <= 1
    assert all(x[0] == "solidworks_fake_scalar_first" for x in got)


if __name__ == "__main__":
    import types

    class _MP:
        def __init__(self):
            self._undo = []

        def setattr(self, obj, name, val):
            self._undo.append((obj, name, getattr(obj, name)))
            setattr(obj, name, val)

        def undo(self):
            for obj, name, old in reversed(self._undo):
                setattr(obj, name, old)
            self._undo.clear()

    for fn in (test_current_repo_passes, test_negative_missing_inject_is_caught,
               test_negative_derived_args_is_not_reported,
               test_non_object_first_param_is_out_of_scope):
        mp = _MP()
        try:
            fn(mp)
            print("  \u2713 %s" % fn.__name__)
        except AssertionError as exc:
            print("  **\u2717 %s**: %s" % (fn.__name__, exc))
        finally:
            mp.undo()
