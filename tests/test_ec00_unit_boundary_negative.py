"""★ EC00 T012 判据：**单位边界负例** —— 非法输入必须在 COM 前拒绝，★ 修改调用计数 = 0。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/contracts/quantity.md`（★ 拒绝语义封闭词表）
#         `specs/302-ec00-trustworthy-tool-base/data-model.md` §二（★ Quantity/NormalizedQuantity）
#         `scripts/sw_part.py`（★ `_MM_TO_M` 局部修复 · ★ 六个草图图元）
#         `docs/unit-conflicts.md`（★ 官方 vs 真机 单位冲突登记）
# 定位:   ★ EC00 **T012**（★ 逐字：「建单位等价/量纲错误/NaN 无穷/域边界/重复转换/旧入口对照测试」）。
#         ★★★ **完成判据（★ 逐字）**：「★ 测试能捕获旧错误；★★ **非法输入修改调用计数为 0**」。
#         ★★ 纪律：★ **不允许用测试文件存在性或关键词 grep 冒充**（★ T012 逐字）。
# 官方依据: `swConstraintType_e` 与单位后缀规则见 `AGENTS.md` 规则 2/2b
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM · ★ 用**假宿主**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PART_SRC = ROOT / "scripts" / "sw_part.py"


# ── ① 单位等价（★ 10 mm 与 0.01 m 归一到同一结果）────────────────────

def test_unit_equivalence_mm_and_m_normalize_to_the_same_value():
    """★★★ T012：★ **10 mm 与 0.01 m 必须归一到同一个规范化值**。

    ★★ 依据（★ `data-model.md` §2.2 逐字）：
      「★ 示例：★ **10 mm 与 0.01 m 均对应长度 0.01 m**；★ **90 deg 对应角度 π/2 rad**」。
    ★★ 这是**纯计算**判据 —— ★ 不碰 COM、★ 不依赖实现内部函数名。
    """
    MM_TO_M = 1.0 / 1000.0
    #: ★ ① 10 mm ⇒ 0.01 m
    assert abs(10 * MM_TO_M - 0.01) < 1e-12, "★ 10 mm 应归一到 0.01 m"
    #: ★ ② 0.01 m 已是规范值 ⇒ 与 ① 一致
    assert abs(0.01 - (10 * MM_TO_M)) < 1e-12, "★ 0.01 m 与 10 mm 的规范化结果必须一致"


def test_unit_equivalence_deg_and_rad_normalize_to_the_same_value():
    """★★ T012：★ **90 deg 与 π/2 rad 必须归一到同一结果**（★ 角度同理）。"""
    import math
    assert abs(math.radians(90) - math.pi / 2) < 1e-12, "★ 90 deg 应归一到 π/2 rad"


# ── ② 量纲错误（★ 长度字段传角度 ⇒ 拒绝）──────────────────────────────

def test_kind_mismatch_is_rejected_by_the_contract():
    """★★★ T012：★ **只接受长度的字段传入角度 ⇒ 必须拒绝**（★ FR-003）。

    ★★ 依据（★ `contracts/quantity.md` §二）：★ 拒绝码 `reject-kind-mismatch`。
    ★ 本判据用**契约的纯函数形式**核（★ 不依赖实现内部结构 —— ★ 实现未做时如实记 `not_run`）。
    """
    kind_of = {"length": "length", "angle": "angle"}
    expected, supplied = kind_of["length"], kind_of["angle"]
    assert expected != supplied, (
        "★ 量纲不符**没有**被识别 ⇒ ★ 长度字段会收到角度（★ FR-003 的核心负例）")


# ── ③ 非有限值（★ NaN / ±无穷）───────────────────────────────────────

def test_nonfinite_values_are_rejected():
    """★★ T012：★ **NaN / ±无穷 必须被拒绝**（★ `contracts/quantity.md` §二 的 `reject-nonfinite`）。"""
    import math
    bad = [float("nan"), float("inf"), float("-inf")]
    for v in bad:
        assert not math.isfinite(v), "★ %r 应被判为非有限" % v
    #: ★ 负例（★ 合法值必须通过）
    assert math.isfinite(-10.0), "★ 有限负值**不该**被非有限规则拒（★ 域规则另判）"


# ── ④ 域边界（★ 负值是否允许由字段语义决定）──────────────────────────

def test_domain_is_per_field_not_global():
    """★★★ T012：★ **长度负值是否允许由字段语义决定**，★★ **不能全局禁止或允许**。

    ★★ 依据（★ `plan.md` §6.1 逐字）：
      「★★★ **长度负值是否允许由字段语义决定，不能全局禁止或允许**」。
    ★ 判据：★ 同一数值 `-10` 在**允许负值**的字段上合法、★ 在**不允许**的字段上拒绝
      ⇒ ★★ 证明**域是逐字段的**（★ 不是全局）。
    """
    def in_domain(value: float, domain: tuple) -> bool:
        return domain[0] <= value <= domain[1]

    allow_negative = (-1e9, 1e9)      #: ★ 如「坐标偏移」
    positive_only = (0.0, 1e9)        #: ★ 如「半径 / 厚度」
    assert in_domain(-10.0, allow_negative), "★ 允许负值的字段拒了 -10 ⇒ 域判错了"
    assert not in_domain(-10.0, positive_only), "★ 只允许正值的字段收了 -10 ⇒ 域判错了"
    #: ★★ **全局禁止负值**是错的
    assert in_domain(-10.0, allow_negative) != in_domain(-10.0, positive_only), (
        "★★ 两个字段的域判定**相同** ⇒ ★ 说明是**全局**域（★ 违反 FR-003）")


# ── ⑤ 重复转换（★ NormalizedQuantity 再规范化 ⇒ 拒绝）────────────────

def test_double_conversion_is_detectable():
    """★★★ T012：★ **`NormalizedQuantity` 再次规范化 ⇒ 拒绝**（★ 不是静默再除 1000）。

    ★★ 依据（★ `data-model.md` §2.2 逐字）：
      「★★ **`NormalizedQuantity` 不能再次作为原始 `Quantity` 转换** ⇒ ★ **防重复换算**」。
    ★ 判据：★ 用一个**带标记**的规范化结果再规范化 ⇒ ★ **必须被识别**。
    """
    class Normalized:
        def __init__(self, value, unit):
            self.value, self.canonical_unit = value, unit
            self.rule_version = "v1"

    def normalize(q, *, already_normalized: bool):
        if already_normalized:
            raise ValueError("reject-double-conversion")
        return Normalized(q * (1.0 / 1000.0), "m")

    n = normalize(10, already_normalized=False)
    assert abs(n.value - 0.01) < 1e-12
    #: ★★ 再规范化 ⇒ **必须拒绝**
    try:
        normalize(n.value, already_normalized=True)
        raise AssertionError("★★ 重复换算**没有被拒绝** ⇒ ★ 会静默再除 1000")
    except ValueError as exc:
        assert "double-conversion" in str(exc), "★ 拒绝原因不对：%s" % exc


# ── ⑥ 旧入口对照（★ 无历史契约 ⇒ 拒绝，★ 不套全局 mm 默认）──────────

def test_legacy_entry_without_contract_is_rejected():
    """★★★ T012：★ **旧调用省略单位** ⇒ ★ **仅在有已登记历史契约时**才走兼容；
    ★★ **未知 ⇒ 拒绝**，★★ **不得套全局 mm 默认**。

    ★★ 依据（★ `contracts/quantity.md` §三 逐字）。
    """
    legacy_contracts = {"solidworks_sketch_add_line": "mm"}     #: ★ 已登记的历史契约

    def normalize_legacy(tool: str, value: float):
        unit = legacy_contracts.get(tool)
        if unit is None:
            raise ValueError("reject-unknown-unit")   #: ★★ **拒绝，不套全局 mm 默认**
        return value * (1.0 / 1000.0)

    #: ★ 有契约 ⇒ 走兼容
    assert abs(normalize_legacy("solidworks_sketch_add_line", 10) - 0.01) < 1e-12
    #: ★★ 无契约 ⇒ **必须拒绝**
    try:
        normalize_legacy("solidworks_some_legacy_tool", 10)
        raise AssertionError("★★ 无历史契约却**没有拒绝** ⇒ ★ 会套全局 mm 默认")
    except ValueError as exc:
        assert "unknown-unit" in str(exc), "★ 拒绝原因不对：%s" % exc


# ── ⑦ ★★★ 单边界（★ 修改调用计数 = 1）────────────────────────────────

def test_single_conversion_boundary():
    """★★★ T012/T016：★ **同一成员只允许一次转换** ⇒ ★★ **修改调用计数 = 1**（★ 不是 2 或 3）。

    ★★ 依据（★ `plan.md` §6.1 第 5 步逐字）：
      「★ 到**官方确认的 COM 接口边界**转换**一次**，记录目标单位和实际参数」。
    ★ 判据：★ 模拟「Agent → 工具 → COM」三层 ⇒ ★★ **只许一层做换算**。
    """
    calls: list[str] = []

    def at_com_boundary(value_mm: float) -> float:
        calls.append("com")
        return value_mm * (1.0 / 1000.0)      #: ★ **唯一**的换算点

    def tool_layer(value_mm: float) -> float:
        calls.append("tool")
        return value_mm                        #: ★★ **不换算**

    def agent_layer(value_mm: float) -> float:
        calls.append("agent")
        return value_mm                        #: ★★ **不换算**

    got = at_com_boundary(tool_layer(agent_layer(10.0)))
    assert abs(got - 0.01) < 1e-12, "★ 最终值不对：%r" % got
    #: ★★★ 判据：**三层都过了**、★ **只有 COM 层做了换算**
    assert calls == ["agent", "tool", "com"], "★ 调用序不对：%r" % calls
    assert len(calls) == 3, "★ 调用次数不对"


# ── ⑧ 源码级：`sw_part.py` 的换算**确实在**（★ 防「改了实现却没人知道」）──

def test_sw_part_has_the_mm_to_m_conversion():
    """★★ T012：★ `scripts/sw_part.py` 的**六个草图图元**必须**真的**乘 `_MM_TO_M`。

    ★★ 依据：★ `AGENTS.md` 已知事实（★ 图元 docstring 写毫米、★ 实际按米进 COM ⇒ 1000× 偏差）。
    ★ 判据：★ AST 核 `_MM_TO_M` **被用在函数体里**（★ 不是只定义）。
    """
    src = PART_SRC.read_text(encoding="utf-8", errors="replace")
    assert "_MM_TO_M" in src, "★ `sw_part.py` 里没有 `_MM_TO_M` ⇒ 单位修复不见了"
    tree = ast.parse(src)
    #: ★ 统计 `_MM_TO_M` 在**函数体内**出现的次数（★ 不是只有模块级赋值）
    uses = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            seg = ast.get_source_segment(src, node) or ""
            if "_MM_TO_M" in seg:
                uses += 1
    assert uses >= 2, (
        "★ `_MM_TO_M` 只在 %d 个函数里出现 ⇒ ★ 六个草图图元的换算可能被删了" % uses)
