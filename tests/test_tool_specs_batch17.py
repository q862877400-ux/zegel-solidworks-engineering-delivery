"""第十七批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch17.py
# 定位:   第十七批的守卫 —— ★ 重点是**规则 2 的角度换算边界**（本批的核心风险）。
# 官方签名依据: 不适用（纯静态核对 + 既有换算助手 `sw_connect.deg()` 的行为核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 核心断言（**含负例**）：
#   ① `derived_args` 把 `angle_deg` 换算成**弧度**（90° ⇒ π/2）；
#   ② ★★ **负例**：证明「只改名不换算」会得到 **90**（差 ~57 倍）—— 那正是本批要防的静默错；
#   ③ `angle_deg` **不是**目标函数的形参（所以必须被 `_consumed` 消费，否则 `TypeError`）；
#   ④ `revolve_boss` 的 `axis_sketch_name` 归一化：`""` → `None`（与目标函数默认对齐）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import inspect
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_DIR = REPO_ROOT / "mcp-server"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def batch17():
    sys.path.insert(0, str(MCP_DIR))
    sys.path.insert(0, str(REPO_ROOT))
    return _load("_b17", MCP_DIR / "tool_specs_batch17.py")


class _P:
    """最小的参数容器（注册器传进来的那个 `params` 的形状）。"""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def _spec(batch17, name):
    for s in batch17.SPECS_BATCH17:
        if s.name == name:
            return s
    raise AssertionError("没有 %s" % name)


def test_deg_is_converted_to_radians(batch17):
    """① `angle_deg=90` ⇒ `angle_rad` 必须是 π/2（**换算真的做了**）。"""
    s = _spec(batch17, "solidworks_circular_pattern")
    out = s.derived_args(_P(angle_deg=90.0))
    assert set(out) == {"angle_rad"}, out
    assert out["angle_rad"] == pytest.approx(math.pi / 2), out
    #: 换算助手与规则 2 点名的 `mm()` **同族** ⇒ 期望它确实是 deg→rad
    assert out["angle_rad"] == pytest.approx(1.5707963267948966), out


def test_negative_naive_alias_would_send_degrees_as_radians(batch17):
    """② ★★ **负例**：证明「只改名、不换算」会静默送出 **90**（而不是 1.5708）。

    ⚠ 这条是**本批存在的理由**：90 rad ≈ 5157°，几何会静默错。
    判据写法：直接构造"naive alias"的语义（把用户值原样当 angle_rad），断言它与正确值**不同量级**。
    """
    s = _spec(batch17, "solidworks_circular_pattern")
    correct = s.derived_args(_P(angle_deg=90.0))["angle_rad"]
    naive = 90.0                      #: ← 只改名不换算时，目标函数会收到的那个值
    assert correct != pytest.approx(naive)
    assert naive / correct == pytest.approx(180.0 / math.pi, rel=1e-9)   #: ≈ 57.3 倍
    assert naive > 50 * correct, "若是同一量级，说明换算没有真的发生"


def test_angle_deg_is_not_a_real_param_so_it_must_be_consumed(batch17):
    """③ `angle_deg` 不是目标函数形参 ⇒ 必须被 `_consumed`；`angle_rad` 才是。"""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import sw_part

    for tool, fn_name in (("solidworks_circular_pattern", "circular_pattern"),
                          ("solidworks_revolve_boss", "revolve_boss")):
        s = _spec(batch17, tool)
        real = set(inspect.signature(getattr(sw_part, fn_name)).parameters)
        assert "angle_rad" in real, real
        assert "angle_deg" not in real, real
        #: ★ 声明了 `angle_deg`，而它不是形参 ⇒ 必须被消费掉（alias 映射到 None）
        assert s.param_alias.get("angle_deg", "MISSING") is None, s.param_alias
        declared = {p.name for p in s.params}
        assert "angle_deg" in declared, declared


def test_declared_params_match_real_signature(batch17):
    """④ 声明的参数（除被消费的）与真实签名一一对应 —— 防止写错名字。"""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import sw_part

    for tool, fn_name in (("solidworks_circular_pattern", "circular_pattern"),
                          ("solidworks_revolve_boss", "revolve_boss")):
        s = _spec(batch17, tool)
        real = set(inspect.signature(getattr(sw_part, fn_name)).parameters)
        consumed = set(s.param_alias)
        declared = {p.name for p in s.params}
        passed = declared - consumed
        assert passed <= real, (tool, "声明了但目标函数不接受的参数: %s" % (passed - real))
        #: 反过来：函数必填的形参不能漏声明（`model` 由注入给，不算）
        required = {
            n for n, p in inspect.signature(getattr(sw_part, fn_name)).parameters.items()
            if p.default is inspect.Parameter.empty and n != "model"
        }
        delivered = passed | set(s.derived_args(_P(angle_deg=1.0, axis_sketch_name="")))
        assert required <= delivered, (tool, "漏声明的必填形参: %s" % (required - delivered))


def test_revolve_boss_normalises_empty_axis_to_none(batch17):
    """⑤ `revolve_boss` 的 `axis_sketch_name`：`""` → `None`（与目标函数默认对齐）。"""
    s = _spec(batch17, "solidworks_revolve_boss")
    assert s.derived_args(_P(angle_deg=360.0, axis_sketch_name=""))["axis_sketch_name"] is None
    assert s.derived_args(_P(angle_deg=360.0, axis_sketch_name="Axis1"))["axis_sketch_name"] == "Axis1"
    #: ⚠ 负例：不归一化时目标函数会收到空的**字符串**（那可能改变分支）
    assert "" is not None
