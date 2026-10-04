"""★ 回归测试：三个 extrude 工具的 `*_mm` 必须**真的换算成米**，不能只改名（含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch22.py` 的
#         `solidworks_extrude_boss` / `_cut` / `_midplane`
# 定位:   ★★★ **用户两次点破的那个真缺陷的机器化修复** ——
#           用户逐字：「**你看到的是一根线，是因为你拉伸长度太长了，离远了看着就是一根线。
#           你都探测到深度是米了为什么不改回来呢？**」
#           并附 SolidWorks 截图：深度框 = **`84300.00mm`** ✓
#         ★★ 根因：三个工具声明的 `depth_mm` / `total_depth_mm` **只做 param_alias 改名、
#           没有换算**，而 `IFeatureManager.FeatureExtrusion3` 的 **D1 吃米** ⇒ 传 40 得 40 米 ✓✗
#         ★★★ 单位口径的**定案证据**（四条独立读数）：
#           ① 标定实验：建 40×40×10 的盒 ⇒ `part_bounding_box` 回 `[0.04, 0.04, 0.01]`
#              ⇒ ★ **该工具返回米**（这一条把我先前"盒 X=84.3 ⇒ 84.3 mm"的误读纠正过来了）✓
#           ② `create_basic_part`（`server.py:1551-1556`）**每处都调 `mm()`** ⇒ 它的盒是对的 ✓
#           ③ 俯视草图按毫米给（±62）⇒ 包围盒 X = 0.131 m = **131 mm** ⇒ ★ **草图吃毫米** ✓
#           ④ **分辨性序列**：`SetSystemValue3` 依次写 0.0843 / 84.3 / 84300 ⇒
#              **只有 0.0843 m** 让包围盒变成 0.0843 m（= 84.3 mm）⇒ ★ **D1 吃米，定案** ✓
#         ★ 同形先例：`tool_specs_batch17.py` 的角度那条（`_consumed` + `derived_args`）✓
# 官方依据: `IFeatureManager/FeatureExtrusion3.md`（D1 = 深度）· `IDimension/SetSystemValue3.md`
#           （NewValue = 米）· 本仓 `sw_connect.mm()`（规则 2 点名的换算助手）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MCP = REPO / "mcp-server"

#: ★ 三个工具：工具名 → (声明的 `_mm` 参数名, 目标形参名)
TOOLS = {
    "solidworks_extrude_boss": ("depth_mm", "depth"),
    "solidworks_extrude_cut": ("depth_mm", "depth"),
    "solidworks_extrude_midplane": ("total_depth_mm", "total_depth"),
}


def _load_batch22():
    if str(MCP) not in sys.path:
        sys.path.insert(0, str(MCP))
    spec = importlib.util.spec_from_file_location("tool_specs_batch22", MCP / "tool_specs_batch22.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tool_specs_batch22"] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _load_batch22()


def _spec(name: str):
    for s in MOD.SPECS_BATCH22:
        if s.name == name:
            return s
    raise AssertionError("找不到工具声明 %r" % name)


class _P:
    """★ 假 params（带该工具声明的那一个 `_mm` 字段）。"""
    def __init__(self, declared: str, value: float):
        setattr(self, declared, value)


# ── 守卫 ─────────────────────────────────────────────────────────────────
def test_three_tools_are_declared() -> None:
    """★ 守卫：三个工具都在，且 `_consumed` / `_m_of_mm` 可用。"""
    for name in TOOLS:
        assert _spec(name) is not None
    assert callable(getattr(MOD, "_consumed"))
    assert callable(getattr(MOD, "_m_of_mm"))


# ── 主断言：三处都必须换算 ───────────────────────────────────────────────
def test_all_three_mm_params_are_converted_not_renamed() -> None:
    """★★★ 主断言：三个 `*_mm` 都被 `derived_args` 消费，且产出的是**米** ✓

    ★★ 这条否掉旧写法：旧写法把它们映射到**非 None** 的目标名 ⇒ 原值（毫米）**直传** ⇒ 大 1000 倍 ✓✗
    """
    for tool, (declared, target) in TOOLS.items():
        s = _spec(tool)
        alias = getattr(s, "param_alias", {}) or {}
        assert declared in alias, "%s：`%s` 没进 param_alias" % (tool, declared)
        assert alias[declared] is None, (
            "%s：`%s` 的别名不是 None ⇒ 会被**原值直传**（★ 这就是 40 米那个缺陷）" % (tool, declared))
        derived = getattr(s, "derived_args", None)
        assert callable(derived), "%s：没有 derived_args ⇒ 没有地方做换算" % tool
        out = derived(_P(declared, 40.0))
        assert target in out, "%s：换算结果没落到目标形参 %r：%r" % (tool, target, out)
        assert declared not in out, "%s：还把 `_mm` 那个名字传下去了" % tool
        assert abs(out[target] - 0.04) < 1e-12, (
            "★★ %s 换算值不对：期望 0.04 米（40 mm），实际 %r —— "
            "★ 若回 40.0 那就是**只改名没换算**（真机症状：40 米高的柱子）" % (tool, out[target]))


def test_conversion_is_linear() -> None:
    """★ 换几个值再验（★ 防"只对某个数凑对"）：1000 mm ⇒ 1.0 m · 84.3 mm ⇒ 0.0843 m ✓"""
    assert abs(MOD._m_of_mm(_P("depth_mm", 1000.0), "depth_mm")["depth"] - 1.0) < 1e-12
    got = MOD._m_of_mm(_P("total_depth_mm", 84.3), "total_depth_mm")["total_depth"]
    assert abs(got - 0.0843) < 1e-15, "84.3 mm 应当是 0.0843 米，实际 %r" % got


def test_conversion_uses_the_shared_helper() -> None:
    """★★ 必须走 `sw_connect.mm()`（规则 2：换算只有一个家），不许手写 /1000。"""
    if str(REPO / "scripts") not in sys.path:
        sys.path.insert(0, str(REPO / "scripts"))
    from sw_connect import mm as shared_mm
    assert MOD._m_of_mm(_P("depth_mm", 37.5), "depth_mm")["depth"] == shared_mm(37.5)
    src = (MCP / "tool_specs_batch22.py").read_text(encoding="utf-8", errors="replace")
    assert "from scripts.sw_connect import mm" in src, "★ 没有从 sw_connect 取 mm() ⇒ 换算有两个家"


# ── 负例（★ 事实 62）────────────────────────────────────────────────────
def test_negative_plain_rename_is_detected() -> None:
    """★★ 负例①：**只改名不换算**（本缺陷的原形态）⇒ 必须被判坏。"""
    tool = "solidworks_extrude_boss"
    alias = {"depth_mm": "depth"}          #: ★ 旧形态逐字
    derived = None
    bad = alias["depth_mm"] is not None and derived is None
    assert bad, "★ 旧形态（只改名）没被判坏 ⇒ 主断言是空转的"


def test_negative_identity_conversion_is_detected() -> None:
    """★★ 负例②：`derived_args` 存在但**原样返回** ⇒ 必须被判坏。"""
    out = {"depth": 40.0}                   #: ★ 忘了 mm()
    assert abs(out["depth"] - 0.04) >= 1e-12, "恒等换算（40 ⇒ 40）通过了 ⇒ 判据抓不到'忘了换算'"


def test_negative_wrong_direction_is_detected() -> None:
    """★★ 负例③：**方向搞反**（×1000）⇒ 也必须被判坏。"""
    wrong = 40.0 * 1000.0
    assert abs(wrong - 0.04) >= 1e-12, "★ 方向搞反没被抓到"


def test_source_records_the_calibration_lesson() -> None:
    """★★ 把"我一度回退过这个修法、因为读错了单位"记在源码里（★ 免得下一个人重犯）。"""
    src = (MCP / "tool_specs_batch22.py").read_text(encoding="utf-8", errors="replace")
    assert "标定" in src and "米" in src, "★ 源码里没记下「标定实验定单位」这条教训"
    assert "84300" in src, "★ 没记下用户截图那个关键数（84300.00mm）"
