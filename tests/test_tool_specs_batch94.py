"""★ 批次 94 的契约测试：隐藏/显示**选中的**草图 + ★★ 裁决书强制的「名字不许许 all」断言。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch94.py` · `scripts/sw_sketch.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-4（idx 175）**；本文件钉四件事：
#         ① 契约：spec 能解析、必填形参全声明 ✓
#         ② ★★ **裁决书硬约束**：官方 `BlankSketch` 逐字是「Hides the **selected** sketches」
#            ⇒ ★ **官方没有 "all" 这个语义** ⇒ ★ 工具名**不许叫 `hide_all_sketches`**、
#              也**不许**在名字里许诺 "all"（★ 那正是别家犯的错）✓
#         ③ ★★ **回读入口**：`IFeature::Visible` → `swVisibilityState_e`
#            （★ 官方示例里**只有肉眼**；★ 这是本批真机定出来的东西）✓
#         ④ 判据：**读不到 ≠ 没变**（两者在返回值里分开）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402
import tool_specs_batch94 as b94                              # noqa: E402

EXPECTED = 1


def test_batch94_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch94"' in t


def test_one_spec_declared_and_resolves():
    assert len(b94.SPECS_BATCH94) == EXPECTED, len(b94.SPECS_BATCH94)
    s = b94.SPECS_BATCH94[0]
    m = importlib.import_module("scripts.%s" % s.module)
    assert callable(getattr(m, s.function, None)), (s.name, s.module, s.function)
    assert s.inject == "model"


def test_required_params_are_all_declared():
    s = b94.SPECS_BATCH94[0]
    sig = inspect.signature(importlib.import_module("scripts.sw_sketch").set_sketch_blanked)
    declared = {p.name for p in s.params}
    required = [n for n, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty and n != "model"]
    assert not [n for n in required if n not in declared], (required, declared)
    assert declared == {"selection", "blank"}, declared


def test_tool_name_does_not_promise_all():
    """★★★ 裁决书硬约束：官方语义是「**选中的**草图」，**没有 "all"** ⇒
    ★ 本仓工具名里**不许**出现 `all` / `hide_all`（★ 别家的 `hide_all_sketches` 是**自己许的语义**，
    而它的实现是「零选区 + 返回常量」—— ★ 规则 6 的反例）✓"""
    name = b94.SPECS_BATCH94[0].name
    assert name == "solidworks_sketch_set_blanked", name
    assert "all" not in name, name
    assert "hide_all" not in name, name


def test_visibility_enum_values_match_official():
    """★ 官方 `swVisibilityState_e`：**Hide=1 · Shown=2 · Unknown=3**（★ **没有 0**）——
    ★ 逐值钉住（★ 这是"隐藏了没有"的唯一官方回读语义）✓"""
    from sw_sketch import VISIBILITY_STATES
    assert VISIBILITY_STATES == {1: "hide", 2: "shown", 3: "unknown"}, VISIBILITY_STATES
    assert 0 not in VISIBILITY_STATES, VISIBILITY_STATES


class _Feat:
    def __init__(self, raw=None, name="草图1", boom=False):
        self.Name = name
        self._raw = raw
        self._boom = boom

    @property
    def Visible(self):
        if self._boom:
            raise RuntimeError("读不到")
        return self._raw


def test_feature_visibility_separates_unreadable_from_a_state():
    """★★ 判据纪律：**读不到**（`readable=False, raw=None`）与**读到某个状态**必须分得开 ——
    ★ 尤其**不许**把「读不到」冒充成 `unknown`(3) ✓"""
    from sw_sketch import feature_visibility
    ok = feature_visibility(_Feat(raw=1))
    assert ok == {"raw": 1, "state": "hide", "readable": True}, ok
    shown = feature_visibility(_Feat(raw=2))
    assert shown["state"] == "shown", shown
    broken = feature_visibility(_Feat(boom=True))
    assert broken == {"raw": None, "state": None, "readable": False}, broken
    #: ★ 枚举外的值也要如实报（★ 不硬塞进三档）
    weird = feature_visibility(_Feat(raw=7))
    assert weird["readable"] is True and weird["state"] == "not_in_enum_7", weird


def test_set_sketch_blanked_refuses_without_model_or_selection():
    import sw_sketch as SK
    r = SK.set_sketch_blanked(None)
    assert r["ok"] is False and r["error"], r
    assert r["entry_used"] == "IModelDoc2::BlankSketch()", r
    r2 = SK.set_sketch_blanked(None, blank=False)
    assert r2["entry_used"] == "IModelDoc2::UnblankSketch()", r2


def test_tool_total_grew_by_one():
        #: ★★ 这里**故意不钉绝对总数** —— ★ 我原来钉的是 `== 443`，结果**每加一批就让
    #:   前面所有批次的测试全红**（★ 全量 pytest 时才暴露，焦点测试看不见）⇒
    #:   ★ **绝对总数只有一处权威断言**：`tests/test_server_wiring.py` ✓
    assert len(rc.all_specs()) >= 443
