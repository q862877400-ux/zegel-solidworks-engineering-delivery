import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 测试：加角度那一半的负例
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_rule2_length_suffix_is_enforced.py")
t = P.read_text(encoding="utf-8")
ADD = '''

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
'''
if "test_rule2_angle_suffix_is_now_enforced" not in t:
    t = t.rstrip() + ADD
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 5 条角度那一半的测试")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

# ② 修探针的子串 bug
Q = Path(r"C:\swprojects\sw-skill-fork\tools\probe_dead_guards.py")
tq = Q.read_text(encoding="utf-8")
print("  （探针本身没有 rad 词表 —— 子串 bug 在**本轮临时探针**里，不写进仓库）")
