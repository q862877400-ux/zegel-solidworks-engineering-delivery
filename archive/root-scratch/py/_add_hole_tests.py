import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_hole_features.py")
t = P.read_text(encoding="utf-8")

ADD = '''

# ── 轮 124：把「孤儿包装」接成能用的 API ──────────────────────────────

def test_module_exposes_a_usable_entry_for_hole_standards():
    """@brief ★ 必须有一个**自己造容器**的高层入口（不再把出参甩给调用方）。"""
    assert hasattr(sw_hole_features, "list_hole_standards")
    params = list(inspect.signature(sw_hole_features.list_hole_standards).parameters)
    assert params[:2] == ["sw", "hole_type_id"], params
    assert "out" not in " ".join(params).lower(), "高层入口不该要求调用方传容器"


def test_out_container_uses_the_verified_byref_form():
    """@brief ★★ 出参容器必须是 `VARIANT(VT_BYREF|VT_VARIANT, None)`。

    真机裁断（已知事实 68）：裸 `None` 与 `VT_BYREF|VT_DISPATCH` **都报「类型不匹配」**，
    只有 `VT_BYREF|VT_VARIANT` 能跑通。
    ⚠ 谁把它改回别的形态，这条会红。
    """
    t = (REPO_ROOT / "scripts" / "sw_hole_features.py").read_text(encoding="utf-8")
    i = t.index("def _out_container")
    body = t[i:t.index("def _out_value", i)]
    assert "VT_BYREF" in body and "VT_VARIANT" in body
    assert "VT_DISPATCH" not in body, "VT_BYREF|VT_DISPATCH 是已知不可用的形态"
    assert "win32com.client" in body, "VARIANT 在 win32com.client 里，**不是** pythoncom.VARIANT"


def test_list_hole_standards_pairs_the_two_out_params_by_position():
    """@brief 两组出参要**按位配对**。"""

    class _Data:
        def GetHoleStandards(self, a, b):      # noqa: N802
            a.value = (0, 1)
            b.value = ("ANSI Inch", "ANSI Metric")
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    rows = sw_hole_features.list_hole_standards(_SW(), 0)
    assert rows == [{"id": 0, "name": "ANSI Inch"}, {"id": 1, "name": "ANSI Metric"}]


def test_list_hole_standards_raises_on_length_mismatch():
    """@brief ★ 长度不一致 ⇒ **抛**（不静默截断、不猜配对）。"""

    class _Data:
        def GetHoleStandards(self, a, b):      # noqa: N802
            a.value = (0, 1, 2)
            b.value = ("x",)
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    with pytest.raises(RuntimeError) as ei:
        sw_hole_features.list_hole_standards(_SW(), 0)
    assert "长度不一致" in str(ei.value)


def test_list_hole_standards_raises_when_data_is_none():
    """@brief 官方写明 `HoleTypeID = 5`（`swWzdLegacy`）返回 `null` ⇒ 要抛带原因的错。"""

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return None

    with pytest.raises(RuntimeError) as ei:
        sw_hole_features.list_hole_standards(_SW(), 5)
    assert "swWzdLegacy" in str(ei.value), str(ei.value)


def test_list_hole_standards_raises_when_official_returns_false():
    """@brief 官方 `GetHoleStandards` 返回 `False` ⇒ **抛**（不静默成功）。"""

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            return False

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    with pytest.raises(RuntimeError):
        sw_hole_features.list_hole_standards(_SW(), 0)
'''

if "test_module_exposes_a_usable_entry" not in t:
    t = t.rstrip() + ADD
    if "import inspect" not in t:
        # 插到第一个 import 之前
        lines = t.splitlines(keepends=True)
        for k, l in enumerate(lines):
            if l.startswith("import ") or l.startswith("from "):
                lines.insert(k, "import inspect\n")
                break
        t = "".join(lines)
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 6 条契约测试")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
