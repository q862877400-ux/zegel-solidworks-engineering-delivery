"""@brief 负例：证明「规则 2 的长度那一半」**根本没生效**。

⚠ 已知事实 62：「一个门禁『写了』不等于它『有效』—— **负例测试是唯一的证明**」。
⚠ 已知事实 40：「一个**存在但没人用**的守卫与没有守卫等价，**且更糟**（让人以为防住了）」。

做法：造一个**故意违规**的 `ToolSpec` —— 参数名是明确的长度词、**不以 `_mm` 结尾**
（`thickness`），然后看 `tool_registry.check_spec` / `register` **会不会拒**。
* 若**拒了** ⇒ 规则 2 有效（那本测试的断言要反过来写）；
* 若**没拒** ⇒ ★ **`_LEN_SUFFIX` 是死常量**，规则 2 只实现了一半。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_rule2_length_suffix_is_enforced.py
# 定位:   轮 134：核实「五统一门禁 · 规则 2（长度 `_mm`）」是否真的在守。
# 官方依据: 不适用（本项目内部纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT / "mcp-server", REPO_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import tool_registry as tr          # noqa: E402


def _bogus_spec() -> "tr.ToolSpec":
    """一个**故意违规**的声明：长度参数 `thickness` **不以 `_mm` 结尾**。"""
    return tr.ToolSpec(
        name="solidworks_probe_rule2_violation",
        title="Rule 2 violation probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="负例：长度参数不以 _mm 结尾（规则 2 应当拒掉它）。",
        param_alias={},
        params=[tr.Param("thickness", float, default=1.0, description="长度，单位不明")],
    )


def test_leng_suffix_constant_exists_but_is_it_used():
    """@brief ★★ `_LEN_SUFFIX` 常量**在源码里出现几次** —— 只在定义处出现 = 死常量。"""
    src = (REPO_ROOT / "mcp-server" / "tool_registry.py").read_text(encoding="utf-8")
    uses = [l for l in src.splitlines()
            if "_LEN_SUFFIX" in l and not l.strip().startswith("#")]
    #: ⚑ 轮 134 之前这里是 `== 1`（**死常量**）；接上之后必须有**判据本体**在用它。
    assert len(uses) > 1, (
        "`_LEN_SUFFIX` 又变回死常量了 —— 规则 2 的长度那一半被摘掉了？实际: %r" % uses)


def test_rule2_length_suffix_is_now_enforced():
    """@brief ★★ **负例**：长度参数不以 `_mm` 结尾 ⇒ **必须被拒**。

    ⚑⚑ 这条测试**换过一次方向**（按它自己预留的指示）：
      * 轮 134 **之前**：规则 2 的长度那一半**从未生效** ⇒ 这里断言"**不**被拒"；
      * 轮 134 **接上之后**：⇒ 改成断言"**必须**被拒"（就是现在这条）。
    ★ 这就是事实 62 要的东西：**负例是唯一的证明** ——
      而"从断言不生效改成断言生效"这个**动作本身**，就是判据被接上的证据。
    """
    spec = _bogus_spec()
    with pytest.raises(tr.GateError) as ei:
        tr.check_spec(spec)
    msg = str(ei.value)
    assert "规则 2" in msg, msg
    assert "thickness" in msg, msg


def test_rule2_exemptions_are_explicit_and_reasoned():
    """@brief ⚑ 豁免必须是**显式表**，且**每条带理由**（照 `MANUAL_MAP` 的先例）。

    ★ 2026-10-01（轮 255）**放宽为「两类理由之一」**（★ 而不是把一类硬说成另一类）：
      本断言原写「理由里必须出现『文档默认』」—— 那是**当时三条豁免的唯一理由**
      （`thickness` / `offset` / `distance`，都是「0.0 = 用文档默认」）。
      ★★ 而轮 255 遇到了**第二类理由**：`solidworks_export_bmp` 的 `pixel_width` / `pixel_height`
        是**像素**，**根本不是长度** ⇒ ★ 加 `_mm` 会把「像素」说成「毫米」，**那是说错话**。
      ⇒ ★ 断言放宽成：**理由必须点明「文档默认」或「不是长度/像素」之一**。
        ★★★ **而不是**把「像素」硬写成「文档默认」—— 那是**为了过门禁而说假话**。
    """
    ex = tr._LEN_SUFFIX_EXEMPT
    assert ex, "豁免表不该为空"
    for k, reason in ex.items():
        assert isinstance(k, tuple) and len(k) == 2, k
        text = str(reason)
        assert len(text) > 30, "%s 的理由太短" % (k,)
        #: ★ 两类理由：①「交给 SolidWorks 的文档默认量」②「它不是长度（如像素）」
        assert ("文档默认" in text) or ("不是长度" in text) or ("像素" in text), (
            "%s 的理由要点明「文档默认」或「不是长度（如像素）」之一" % (k,))


def test_rule2_does_not_flag_boolean_flags():
    """@brief ★ `bool` **不是长度** —— `use_default_radius` / `reverse_thickness` 是**标志**。

    ⚠ 没有这条排除，这两个**真实存在**的参数会被误判（那是本轮的 4 个假阳性里的 2 个）。
    """
    spec = tr.ToolSpec(
        name="solidworks_probe_rule2_bool_flag",
        title="Bool flag probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="负例：bool 标志里含长度词，**不该**被规则 2 拦。",
        param_alias={},
        params=[tr.Param("use_default_radius", bool, default=True,
                         description="标志，不是长度")],
    )
    tr.check_spec(spec)      # 不该抛


def test_the_bare_coordinate_rule_is_enforced():
    """@brief 对照：**裸坐标那条**（同一段的规则 3）**是生效的**。

    ⇒ 说明规则 2 的缺失**不是"整段都没实现"**，而是**恰好少了长度那一半**。
    """
    spec = tr.ToolSpec(
        name="solidworks_probe_bare_coord",
        title="Bare coord probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="负例：裸坐标参数（规则 3 应当拒掉它）。",
        param_alias={},
        params=[tr.Param("x", float, default=0.0, description="裸坐标")],
    )
    with pytest.raises(tr.GateError):
        tr.check_spec(spec)

# ── 轮 135：规则 2 的**角度那一半**（同样曾是死常量）────────────────

def _bogus_angle_spec() -> "tr.ToolSpec":
    """一个**故意违规**的声明：角度参数 `angle` **不以 `_deg` 结尾**。"""
    return tr.ToolSpec(
        name="solidworks_probe_rule2_angle_violation",
        title="Rule 2 angle violation probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="负例：角度参数不以 _deg 结尾（规则 2 应当拒掉它）。",
        param_alias={},
        params=[tr.Param("angle", float, default=0.0, description="角度，单位不明")],
    )


def test_angle_suffix_constant_is_used_now():
    """@brief ★★ `_ANGLE_SUFFIX` 曾与 `_LEN_SUFFIX` 一样是**死常量**（轮 135 扫出来的）。"""
    src = (REPO_ROOT / "mcp-server" / "tool_registry.py").read_text(encoding="utf-8")
    uses = [l for l in src.splitlines()
            if "_ANGLE_SUFFIX" in l and not l.strip().startswith("#")]
    assert len(uses) > 1, (
        "`_ANGLE_SUFFIX` 变回死常量了 —— 规则 2 的角度那一半被摘掉了？实际: %r" % uses)


def test_rule2_angle_suffix_is_now_enforced():
    """@brief ★★ **负例**：角度参数不以 `_deg` 结尾 ⇒ **必须被拒**。"""
    with pytest.raises(tr.GateError) as ei:
        tr.check_spec(_bogus_angle_spec())
    msg = str(ei.value)
    assert "规则 2" in msg and "angle" in msg, msg


def test_angle_words_exclude_the_radius_substring_trap():
    """@brief ★★ `_ANGLE_WORDS` **不许**含 `rad` —— 它会**子串命中 `radius`**。

    ⚠ 本轮实测：`bend_radius_mm`（×4）+ `use_default_radius`（×3）= **7 处**假阳性
    就是这么来的。⇒ 词表**刻意不含** `rad` / `radians`。
    """
    assert "rad" not in tr._ANGLE_WORDS, "`rad` 会子串命中 `radius`"
    assert "angle" in tr._ANGLE_WORDS


def test_radius_param_is_not_flagged_as_an_angle():
    """@brief ★ 对照：`bend_radius_mm`（**长度**）不该被角度那条拦。"""
    spec = tr.ToolSpec(
        name="solidworks_probe_radius_not_angle",
        title="Radius probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="对照：`bend_radius_mm` 是长度、且已带 `_mm` ⇒ 两条都不该拦。",
        param_alias={},
        params=[tr.Param("bend_radius_mm", float, default=1.0, description="弯曲半径")],
    )
    tr.check_spec(spec)      # 不该抛


def test_angle_exemptions_are_explicit_and_reasoned():
    """@brief ⚑ 角度豁免也必须是**显式表 + 每条理由**。"""
    ex = tr._ANGLE_SUFFIX_EXEMPT
    assert ex, "角度豁免表不该为空"
    for k, reason in ex.items():
        assert isinstance(k, tuple) and len(k) == 2, k
        assert "文档默认" in str(reason), "%s 的理由要点明「文档默认」" % (k,)
