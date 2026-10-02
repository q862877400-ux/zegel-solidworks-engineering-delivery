"""★ 选择底座 6 个工具的契约测试：返回形状 + 「绝不许漏出 COM 对象」+ 非法输入不崩。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_sw_selection_base_contract.py
# 定位:   ★ 2026-10-03（轮 397）24h 计划 v2 段 1 的契约测试。被锁的契约：
#   ① 四个直挂入口返回的**类型**（int / dict）—— `get_selection_count` · `select_entity_by_index` ·
#      `resolve_selection` · `selection_point`；
#   ② ★★ **两个 report 包装（`select_by_selector_report` / `resolve_entity_report`）
#      绝不许把 COM 对象漏出来** —— 用 `json.dumps` 当判据（★ 那正是 MCP 层会做的事）；
#   ③ ★ 非法输入 / `model=None` ⇒ **回 `ok=False` + 有原因**，**不崩**（★ 本模块不碰 COM ⇒ 可离线测）。
# 官方依据: `ISelectionMgr.GetSelectedObjectCount2` · `IEntity.Select4` ·
#   `ISelectionMgr.GetSelectionPoint2(Index, Mark)`（★ 2 参；★ 而 `GetSelectionPoint(AtIndex)` **1 参**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sw_selection_spec as S                                        # noqa: E402

REPORT_WRAPPERS = ("select_by_selector_report", "resolve_entity_report")


@pytest.mark.parametrize("fn_name", REPORT_WRAPPERS)
def test_report_wrapper_return_is_json_serializable(fn_name: str) -> None:
    """★★ **契约核心**：report 包装的返回值必须能 `json.dumps` ——
    ★ 那正是 MCP 层会做的事；★ 而 COM 对象过不去（★ 这就是那两个包装存在的理由）。"""
    fn = getattr(S, fn_name)
    for selector in ("index:0", "index:not_an_int", ""):
        out = fn(None, selector, "EDGE")          # model=None ⇒ 走异常分支
        assert isinstance(out, dict), "%s 必须回 dict" % fn_name
        json.dumps(out, ensure_ascii=False)       # ★ 不许抛


@pytest.mark.parametrize("fn_name", REPORT_WRAPPERS)
def test_report_wrapper_never_raises_on_none_model(fn_name: str) -> None:
    """★ `model=None` ⇒ **回 `ok=False` + 写明原因**，★ **不崩**（★ 与"选不中就报错"分工不同：
    报错是给直接调内部实现的调用方；包装是给 MCP 层，要能回一个可读的结果）。"""
    out = getattr(S, fn_name)(None, "index:0", "EDGE")
    assert out["ok"] is False
    assert out["error"], "失败必须写原因"


def test_select_by_selector_report_shape() -> None:
    """★ `select_by_selector_report` 的键必须齐（★ 契约固定，调用方按名字取）。"""
    out = S.select_by_selector_report(None, "index:0", "EDGE")
    assert set(out) >= {"ok", "selector", "kind", "count", "error"}
    assert out["kind"] == "EDGE", "kind 应被规整成大写"


def test_resolve_entity_report_shape() -> None:
    """★ `resolve_entity_report` 的键必须齐，且 `resolved` 与 `ok` **不是同一个东西**。"""
    out = S.resolve_entity_report(None, "index:0", "EDGE")
    assert set(out) >= {"ok", "selector", "kind", "count", "resolved", "error"}
    assert out["resolved"] is False


def test_selection_point_returns_mm_named_fields() -> None:
    """★ 规则 2：★ `selection_point` 回的字段名必须带 `_mm`（★ 因为它是**长度**）。
    ⚠ 本测试**不碰 COM**：只检查签名与文档里的键名约定。"""
    src = inspect.getsource(S.selection_point)
    assert "point_mm" in src, "长度字段必须带 _mm（规则 2）"
    assert '"ok"' in src and '"error"' in src


def test_get_selection_point_arity_is_per_name() -> None:
    """★★ 2026-10-03 真机抓到的 bug 的**静态锁**：★ 两个入口的 arity **不同** ——
    `GetSelectionPoint2(Index, Mark)` 是 **2 参**，而 `GetSelectionPoint(AtIndex)` 是 **1 参**。
    ★ 先前给两个都传 `(1, -1)` ⇒ 走到 1 参那个必然报 `(-2147352562, '无效的参数数目。')`。
    ⇒ ★ 本测试读源码，断言**两个入口各自带着自己的实参元组**。"""
    src = inspect.getsource(S.selection_point)
    assert '("GetSelectionPoint2", (1, -1))' in src, "2 参入口必须传 (Index, Mark)"
    assert '("GetSelectionPoint", (1,))' in src, "1 参入口只能传 (AtIndex)"
    assert 'GetSelectionPoint(1, -1)' not in src, "不许再出现给 1 参入口传两个实参"
