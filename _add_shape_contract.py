import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_sketch_contract.py")
t = P.read_text(encoding="utf-8")
ADD = '''

# ── 轮 141：`get_*` 系列**都是「数值数组」**（通例，不是孤例）──────────
#
# ⚑ 实测（2026-10-01 轮 141，真机 SW 2026 SP4.1，`tools/probe_sketch_getter_shapes.py`）：
#   | 取法 | 画 1 个 | 画 2 个 | 每个占几个 float |
#   |---|---|---|---|
#   | get_lines    | 12 | 24 | **12** |
#   | get_arcs     | 16 | 32 | **16** |
#   | get_ellipses | 22 | 44 | **22** |
#   ⇒ ★ 三个**都是数值数组**（元素 `float`）⇒ 与轮 140 发现的 `get_lines` **同类**。
#   ⚠ `get_splines` 量到 **0** —— 而根因是**样条根本画不出来**（另见下节）。

_GETTER_SHAPES = {"get_lines": 12, "get_arcs": 16, "get_ellipses": 22}


def test_type_getters_document_the_numeric_array_shape():
    """@brief ★★ 三个按类型取法的 docstring 都要写明「数值数组」与「每个占几个 float」。"""
    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    for fn, per in _GETTER_SHAPES.items():
        i = src.index("def %s(" % fn)
        doc = src[i:i + 2000]
        assert "数值数组" in doc, "%s 要写明返回的是数值数组" % fn
        assert str(per) in doc, "%s 要写明每个占 %d 个 float" % (fn, per)
        assert "get_sketch_segments" in doc, "%s 要给出「要几个实体」的替代" % fn


def test_sketch_spline_fails_loudly_instead_of_returning_none():
    """@brief ★★ `sketch_spline` 在 `CreateSpline2` 返回 `None` 时**必须抛**。

    ⚑ 实测（轮 141）：`CreateSpline2` 返回 **`None`** ⇒ `get_sketch_segments` = **0**；
    ★ **重绘后仍是 0** ⇒ 排除了官方 Remarks 那句"必须重绘才看得见"的解释；
    后继 `CreateSpline3` 末参是 **BYREF `Object&`** ⇒ 事实 47/68 的架构限制。
    ⇒ 处置照 `sw_surface._invoke` 的先例（事实 40）：**让失败可见**。
    """
    import importlib.util
    import types
    spec = importlib.util.spec_from_file_location(
        "sw_part_probe", REPO_ROOT / "scripts" / "sw_part.py")
    mod = importlib.util.module_from_spec(spec)
    stub = types.ModuleType("sw_connect")
    stub.get_com_member = lambda obj, name: getattr(obj, name)
    sys.modules.setdefault("sw_connect", stub)
    spec.loader.exec_module(mod)

    class _Mgr:
        @staticmethod
        def CreateSpline2(_arr, _flag):      # noqa: N802
            return None

    class _Model:
        SketchManager = _Mgr()

    try:
        mod.sketch_spline(_Model(), [(0.0, 0.0), (10.0, 10.0)])
    except RuntimeError as exc:
        assert "没建出来" in str(exc) or "None" in str(exc), str(exc)
    else:
        raise AssertionError("sketch_spline 返回 None 时**没有抛** —— 静默空操作")


def test_sketch_spline_docstring_states_the_measured_failure():
    """@brief ★★ docstring 必须写明**实测建不出来**与**为什么**（免得下一个人再试）。"""
    src = (REPO_ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
    i = src.index("def sketch_spline(")
    doc = src[i:i + 2200]
    assert "轮 141" in doc, "要标注实测轮次"
    assert "重绘" in doc, "要写明「重绘后仍为 0」（排除掉那条解释）"
    assert "CreateSpline3" in doc, "要点出后继与它的 BYREF 末参"
'''
if "test_type_getters_document_the_numeric_array_shape" not in t:
    P.write_text(t.rstrip() + ADD, encoding="utf-8")
    print("  ok 契约测试已加 3 条")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
