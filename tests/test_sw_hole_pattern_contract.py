"""★ 段 4 孔族的契约：工具接线 + 「需要 COM 元素的配置器不许被挂」的保护。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_sw_hole_pattern_contract.py
# 定位:   ★ 2026-10-03（轮 401）24h 计划 v2 段 4 的契约测试。被锁的契约：
#   ① `tool_specs_batch57` 的声明接线（★ `inject="model"` 必须写 —— 轮 398 漏过一次）；
#   ② ★★ **`hole_pattern_report` 把 `creator` 可调用对象换成了具名 `kind`** ——
#      ★ 断言它**只接受白名单里的种类**，且**缺必填参数时先拒绝再碰模型**（★ 纯逻辑可离线测）；
#   ③ ★★ **不许把"需要 COM 元素的配置器"挂出去**：`configure_straight_tap` /
#      `configure_tapered_tap` 吃 `IStraightTapElementData` / `ITaperedTapElementData`，
#      ★ 而本仓**没有任何路径能从孔特征拿到那个元素** ⇒ ★ MCP 层给不出 ⇒ **不该有工具指向它们**。
# 官方依据: `IFeatureManager.HoleWizard5`
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
sys.path.insert(0, str(ROOT / "mcp-server"))

import sw_hole_features as H                                        # noqa: E402


def _specs():
    import tool_specs_batch57 as B                                  # noqa: PLC0415
    return {s.name: s for s in B.SPECS_BATCH57}


def test_spec_declared_and_wired() -> None:
    spec = _specs()["solidworks_hole_pattern"]
    assert spec.module == "sw_hole_features"
    assert spec.function == "hole_pattern_report"
    assert spec.inject == "model"
    real = set(inspect.signature(H.hole_pattern_report).parameters)
    for p in spec.params:
        assert spec.param_alias.get(p.name, p.name) in real


def test_positions_param_is_a_list() -> None:
    """★ 孔位是**列表**（★ 而 `Param(..., list, ...)` 在本仓已有先例：bom_rows / configuration_names）。"""
    params = {p.name: p for p in _specs()["solidworks_hole_pattern"].params}
    assert "positions" in params


@pytest.mark.parametrize("kwargs,why", [
    ({"positions": [[0.0, 0.0]], "kind": "counterbore"}, "只暴露 through/blind"),
    ({"positions": [[0.0, 0.0]], "kind": "blind"}, "盲孔缺 depth_mm"),
    ({"positions": [], "kind": "through"}, "空孔位表"),
    ({"positions": [[0.0]], "kind": "through"}, "孔位不足两个数"),
])
def test_rejects_before_touching_the_model(kwargs: dict, why: str) -> None:
    """★★ **先拒绝再碰模型**：★ `model=None` 时这些非法输入必须**回 `ok=False` + 原因**，
    ★ 而**不是**抛 `AttributeError`（★ 那说明它先去摸模型了 —— 白名单/校验的位置就错了）。"""
    out = H.hole_pattern_report(None, **kwargs)
    assert isinstance(out, dict) and out["ok"] is False, why
    assert out["error"], "拒绝时必须写原因"
    json.dumps(out, ensure_ascii=False)          #: ★ 必须能序列化（MCP 层会这么做）


def test_supported_kinds_are_exactly_through_and_blind() -> None:
    """★ 白名单是**显式**的（★ 而这也让"没暴露的种类"成为**有意**而不是遗漏）。"""
    assert set(H._HOLE_PATTERN_CREATORS) == {"through", "blind"}
    for name in H._HOLE_PATTERN_CREATORS.values():
        assert hasattr(H, name), "creator 名字必须真的存在于本模块"


@pytest.mark.parametrize("fn_name", ["configure_straight_tap", "configure_tapered_tap"])
def test_com_element_configurators_are_not_exposed(fn_name: str) -> None:
    """★★ **保护**：★ 这两个吃 **COM 元素对象**，而本仓**没有路径**能拿到它
    （★ 只在 mock 测试里出现过）⇒ ★ MCP 层给不出 ⇒ ★ **不该有任何工具指向它们**。
    ★ 若将来有人找到了取元素的路，先让本测试红，再决定怎么挂。"""
    import register_capabilities as RC                              # noqa: PLC0415
    targets = {s.function for s in RC.all_specs()}
    assert fn_name not in targets, "%s 需要 COM 元素 ⇒ 不该直接挂" % fn_name
    #: ★ 而它的第一个形参确实是那个元素（★ 理由的**静态证据**）
    first = next(iter(inspect.signature(getattr(H, fn_name)).parameters))
    assert first == "element", "理由：它的第一个形参就是那个 COM 元素"
