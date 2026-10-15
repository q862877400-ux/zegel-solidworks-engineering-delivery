"""@brief 复杂孔槽创建封装的离线回归测试。"""

import inspect
from contextlib import contextmanager

import pytest

from pathlib import Path

from scripts import sw_hole_features as holes

REPO_ROOT = Path(__file__).resolve().parents[1]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）。
# 文件:   tests/test_sw_hole_features.py —— 本文件自身。
# 定位:   复杂孔槽创建封装（`scripts/sw_hole_features.py`）的离线回归测试；
#         轮 124 追加的部分覆盖**把孤儿包装接成可用 API** 之后的 6 条契约判据。
# 官方依据: 出厂类型库反射 `iface_*.txt`；
#           `C:\swapi\types\ISldWorks\GetHoleStandardsData.md`；
#           `C:\swapi\types\IHoleStandardsData\GetHoleStandards.md`；
#           真机裁断见已知事实 68（`tools/probe_outparam_object_byref.py`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

class FakeFeature:
    """@brief 模拟 SolidWorks Feature。"""

    Name = ""


class FakeFeatureManager:
    """@brief 记录沉头锥形切除参数。"""

    def __init__(self):
        self.cut_calls = []
        self.chamfer_calls = []

    def FeatureCut4(self, *args):
        self.cut_calls.append(args)
        return FakeFeature()

    def InsertFeatureChamfer(self, *args):
        self.chamfer_calls.append(args)
        return FakeFeature()


class FakeModel:
    """@brief 仅提供复杂孔模块直接访问的 FeatureManager。"""

    def __init__(self):
        self.FeatureManager = FakeFeatureManager()

    def ClearSelection2(self, clear_all):
        return clear_all


@pytest.fixture
def fake_ops(monkeypatch):
    """@brief 用可观测假对象替换草图与普通切除。"""
    calls = {"circles": [], "slots": [], "cuts": [], "selected": []}

    @contextmanager
    def fake_sketch(model, plane_name):
        yield f"Sketch_{plane_name}"

    def fake_circle(model, x, y, radius):
        calls["circles"].append((x, y, radius))
        return object()

    def fake_slot(model, x1, y1, x2, y2, radius):
        calls["slots"].append((x1, y1, x2, y2, radius))
        return [object()]

    def fake_cut(model, sketch_name, depth):
        calls["cuts"].append((sketch_name, depth))
        return FakeFeature()

    monkeypatch.setattr(holes, "sketch", fake_sketch)
    monkeypatch.setattr(holes, "sketch_circle", fake_circle)
    monkeypatch.setattr(holes, "sketch_slot", fake_slot)
    monkeypatch.setattr(holes, "extrude_cut", fake_cut)
    monkeypatch.setattr(holes, "_find_hole_entry_edge", lambda *args: object())
    monkeypatch.setattr(holes, "_select_com_object", lambda edge, append=False, mark=0: True)
    return calls


def test_counterbore_creates_through_and_recess_cuts(fake_ops) -> None:
    evidence = holes.create_counterbore_hole(FakeModel(), (0.02, 0.03), 0.006, 0.012, 0.004)

    assert fake_ops["circles"] == [(0.02, 0.03, 0.003), (0.02, 0.03, 0.006)]
    #: ★★ 2026-10-11 **单位修复**后，`_circle_cut` 把深度**毫米→米**换算一次
    #:   （官方 `FeatureCut4.md:22` 逐字「D1 … **in meters**」）。
    #:   ⇒ 传 4（mm）⇒ 进 `extrude_cut` 的是 **4e-06**（米）。
    #:   依据：`output/probe-unit-decisive/decisive.json`（同文档单变量定案）。
    assert [depth for _sketch, depth in fake_ops["cuts"]] == [0.0, 4e-06]
    assert evidence["feature_kind"] == "counterbore"
    assert evidence["counterbore_diameter_mmm"] == 12.0
    assert evidence["counterbore_depth_mmm"] == 4.0


def test_countersink_computes_depth_from_included_angle(fake_ops) -> None:
    model = FakeModel()
    evidence = holes.create_countersink_hole(model, (0.01, 0.02), 0.005, 0.010, included_angle_deg=90.0)

    assert evidence["feature_kind"] == "countersink"
    assert evidence["countersink_angle_deg"] == 90.0
    assert model.FeatureManager.chamfer_calls[0][0:2] == (4, 1)
    assert model.FeatureManager.chamfer_calls[0][2] == pytest.approx(0.0025)
    assert model.FeatureManager.chamfer_calls[0][3] == pytest.approx(0.7853981633974483)


def test_semicircular_slot_uses_half_width_as_slot_radius(fake_ops) -> None:
    evidence = holes.create_semicircular_slot(FakeModel(), (0.01, 0.02), (0.04, 0.02), 0.010, depth=0.0)

    assert fake_ops["slots"] == [(0.01, 0.02, 0.04, 0.02, 0.005)]
    assert fake_ops["cuts"][0][1] == 0.0
    assert evidence["through"] is True
    assert evidence["width_mm"] == 10.0


def test_hole_pattern_preserves_explicit_positions(fake_ops) -> None:
    evidence = holes.create_hole_pattern(
        FakeModel(),
        [(0.01, 0.02), (0.03, 0.04)],
        holes.create_blind_hole,
        diameter=0.008,
        depth=0.010,
        name="定位盲孔",
    )

    assert [item["center_mm"] for item in evidence] == [[10.0, 20.0], [30.0, 40.0]]
    assert [item["feature_names"][0] for item in evidence] == ["定位盲孔_1", "定位盲孔_2"]


@pytest.mark.parametrize(
    "call",
    [
        lambda model: holes.create_blind_hole(model, (0.0, 0.0), 0.0, 0.01),
        lambda model: holes.create_counterbore_hole(model, (0.0, 0.0), 0.008, 0.006, 0.003),
        lambda model: holes.create_countersink_hole(model, (0.0, 0.0), 0.005, 0.010, 180.0),
        lambda model: holes.create_semicircular_slot(model, (0.0, 0.0), (0.0, 0.0), 0.010),
    ],
)
def test_invalid_hole_parameters_fail_before_com(call, fake_ops) -> None:
    with pytest.raises(ValueError):
        call(FakeModel())

# ── 轮 124：把「孤儿包装」接成能用的 API ──────────────────────────────

def test_module_exposes_a_usable_entry_for_hole_standards():
    """@brief ★ 必须有一个**自己造容器**的高层入口（不再把出参甩给调用方）。"""
    assert hasattr(holes, "list_hole_standards")
    params = list(inspect.signature(holes.list_hole_standards).parameters)
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
    # ⚠ 查**实际构造那一行**，不查整段 ——
    #   文档串里**必须**提到 `VT_BYREF|VT_DISPATCH`（解释为什么不用它），
    #   查整段会被自己的说明文字误伤（**轮 119 踩过同一个坑**）。
    ctor = [l for l in body.splitlines()
            if "VARIANT(" in l and not l.strip().startswith("#")]
    assert ctor, "找不到构造出参容器的那一行"
    line = ctor[-1]
    assert "VT_BYREF" in line and "VT_VARIANT" in line, line
    assert "VT_DISPATCH" not in line, "VT_BYREF|VT_DISPATCH 是已知不可用的形态"
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

    rows = holes.list_hole_standards(_SW(), 0)
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
        holes.list_hole_standards(_SW(), 0)
    assert "长度不一致" in str(ei.value)


def test_list_hole_standards_raises_when_data_is_none():
    """@brief 官方写明 `HoleTypeID = 5`（`swWzdLegacy`）返回 `null` ⇒ 要抛带原因的错。"""

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return None

    with pytest.raises(RuntimeError) as ei:
        holes.list_hole_standards(_SW(), 5)
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
        holes.list_hole_standards(_SW(), 0)

# ── 轮 125：紧固件链路 + "必须热身"那条约束 ──────────────────────────

def test_hole_standards_data_warms_up_by_default():
    """@brief ★★ 默认必须**先热身**（调一次 `GetHoleStandards`）再交给调用方。

    真机查出（轮 125）：拿到 `IHoleStandardsData` 后**直接**调 `GetFastenerTypes`
    ⇒ **返回 `False`**；**先调一次 `GetHoleStandards`** ⇒ **`True`**。
    ⚠ 官方文档**没写**这条约束。谁把热身去掉，这条会红。
    """
    calls = []

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            calls.append("warm")
            return True

        def GetFastenerTypes(self, _s, _a, _b):      # noqa: N802
            calls.append("fastener")
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    holes._hole_standards_data(_SW(), 0)
    assert calls == ["warm"], "默认应当只热身一次；实际 %r" % (calls,)


def test_hole_standards_data_can_skip_warmup():
    """@brief `initialize=False` 时**不热身**（给"只想列标准"的调用方省一次调用）。"""
    calls = []

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            calls.append("warm")
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    holes._hole_standards_data(_SW(), 0, initialize=False)
    assert calls == [], "明确跳过时不该热身"


def test_list_fastener_types_pairs_by_position():
    """@brief 紧固件类型也是**两组出参按位配对**。"""

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            return True

        def GetFastenerTypes(self, _s, a, b):      # noqa: N802
            a.value = (4, 7)
            b.value = ("六角精致螺栓", "六角螺垫螺钉")
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    assert holes.list_fastener_types(_SW(), "ANSI Inch", 0) == [
        {"id": 4, "name": "六角精致螺栓"}, {"id": 7, "name": "六角螺垫螺钉"}]


def test_list_fastener_table_types_second_arg_is_an_int():
    """@brief ★ 官方第 2 参是 `Int32`（**紧固件 ID**），不是尺寸名。

    真机第一版就栽在这：传尺寸名 ⇒ 「类型不匹配」，**位置 2**。
    """
    seen = {}

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            return True

        def GetFastenerTableTypes(self, s, n, out):      # noqa: N802
            seen["args"] = (s, n)
            out.value = (0, 1, 2)
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    assert holes.list_fastener_table_types(_SW(), "ANSI Inch", 4, 0) == [0, 1, 2]
    assert seen["args"] == ("ANSI Inch", 4)
    assert isinstance(seen["args"][1], int), "第 2 参必须是 int"


def test_get_fastener_table_is_documented_as_unreachable():
    """@brief ★★ `get_fastener_table` 目前**到不了** —— 源码必须如实写明。

    真机三次都报「类型不匹配 位置 4」，而同族另外三个用**同一形态**都通。
    ⚠ 没有这条，下一个人会以为它是能用的。
    """
    t = (REPO_ROOT / "scripts" / "sw_hole_features.py").read_text(encoding="utf-8")
    i = t.index("def get_fastener_table")
    body = t[i:i + 1800]
    assert "不可用" in body, "必须写明当前不可用"
    assert "事实 53" in body, "要写明为什么停手"
    assert "位置 4" in body, "要写下量到的失败位置"
