"""
sw_part 草图选择回归测试。

重点覆盖 SolidWorks 2024 中文版反馈过的问题：
选择集为空且 SelectByID2("SKETCH") 失败时，特征函数应使用创建草图时
缓存的对象引用，而不是依赖残留选择集。
"""
from pathlib import Path
import inspect
import sys
import types
import unittest

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）。
# 文件:   tests/test_sw_part_sketch_selection.py —— 本文件自身。
# 定位:   `scripts/sw_part.py` 的离线回归测试；轮 127 追加**边界框**那 3 条判据
#         （`GetBodyBox` 的原始值就是毫米、官方 approximate 声明要照抄、失败要抛）。
# 官方依据: `C:\swapi\types\IBody2\GetBodyBox.md`；
#           真机单位裁断见 `tools/verify_bbox_smoke.py` 与已知事实 71。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

def fake_get_com_member(obj, attr_name, *args):
    """测试用 COM 成员读取器。"""
    member = getattr(obj, attr_name)
    return member(*args) if args or callable(member) else member


class FakeVariant:
    """测试用 VARIANT 占位类型。"""

    def __init__(self, *_args):
        pass


#: ⚠ 2026-10-01（轮 145）：桩要**跟着真模块走** —— 轮 145 给 `sw_connect`
#:   加了 `call_com_member`（"故意要调"的显式名），桩里也得有，否则 `sw_part` 导入即失败。
#: ★★★ 2026-10-06（规格 209 收口轮）：**同一处又栽了一次** —— `scripts/sw_feature_readback.py`
#:   后来加了 `safe_get_com_member`（★ 阶段3/5 那条线，见 `git log -S`），★ 而**桩里没有** ⇒
#:   `import sw_part` 在**收集期**就炸 ⇒ ★★ 它一炸就把**后面所有测试的模块身份也带坏**
#:   （实测：`tests/test_tool_specs_batch92.py` **单独跑 25 passed**、跟在它后面跑就红）✓
#:   ⇒ ★ 本条本来就是"桩要跟着真模块走"，★ **这次把它补全** ✓
#: ★★★★★ 2026-10-07（接手轮）**第三次同一处** —— ★ 这次缺的是 `sw_connect` 新加的 **`deg`**
#:   （★ 规格 213「`sw_sheet_metal.py` 的 `deg` 取法」那一条）⇒ ★ `scripts/sw_body_ops.py` /
#:   `sw_helix.py` / `sw_sheet_metal*.py` 都 `from sw_connect import deg` ⇒ **收集期即炸**，
#:   ★★ 实测同一副症状：`test_tool_specs_batch92.py` 单独跑 **25 passed**、跟在它后面跑 **23 failed**；
#:   ★ 全量跑时被带坏的还有 `test_rule3_*`（3 条）· `test_spec212_rule2b_gate`（1 条）·
#:   本文件的 `BBoxTests`（2 条）⇒ ★ **一处桩缺名，8 条测试红** ✓
#:   ★★★ **⇒ 这次不再"手补第三个名字"**，改成 **让假模块的其余名字一律转发给真模块** ——
#:   ★★ 这正是同仓 `tests/test_sw_selection_contract.py` 在**轮 470** 用过的**成熟解法**
#:   （PEP 562 的模块级 `__getattr__`）⇒ ★★ **以后真 `sw_connect` 再加名字，本装置不必再改** ✓
#:   ⚠ 为什么原来是 `types.SimpleNamespace` 就会坏：它**没有**模块级 `__getattr__`、
#:     也**没有 `__name__`** ⇒ `from sw_connect import deg` 报
#:     `cannot import name 'deg' from '<unknown module name>'`
#:     —— ★★ "unknown module name" 正是**缺 `__name__`** 的后果 ⇒ **错误信息指不到真因**
#:     （与轮 470 那条 `unknown location` 同型）✓
#:   ⚠ 真模块**按文件路径**载入（不用 `import sw_connect`）—— ★ 因为本文件**自己**就要往
#:     `sys.modules["sw_connect"]` 里装假模块，用名字导入会**拿到别人装的那个** ⇒ 转发会自己咬自己 ✓
_real_sw_connect = None
try:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("_real_sw_connect_for_part_tests",
                                         str(ROOT / "scripts" / "sw_connect.py"))
    _real_sw_connect = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_real_sw_connect)                                # type: ignore[union-attr]
except Exception:                                                             # noqa: BLE001
    _real_sw_connect = None

_fake_connect = types.ModuleType("sw_connect")
_fake_connect.get_com_member = fake_get_com_member
_fake_connect.call_com_member = fake_get_com_member
_fake_connect.safe_get_com_member = fake_get_com_member
if _real_sw_connect is not None:
    #: ★ PEP 562 兜底：假模块上**没手装**的名字，一律从真模块拿 ✓
    _fake_connect.__getattr__ = lambda _n: getattr(_real_sw_connect, _n)
#: ★★ 进本模块**之前**这两个键是谁 —— ★ fixture teardown 要把它们**原样还回去** ✓
_saved_sw_connect = sys.modules.get("sw_connect")
_saved_sw_preflight = sys.modules.get("sw_preflight")

#: ★★ 模块级名字：**由下面的 fixture 在用例开始前填入** ——
#:    ⚠ 收集期这里**故意是 `None`**（★ 不在这里 `import sw_part`）—— 见 fixture 那段注释 ✓
sw_part = None


#: ═══════════════════════════════════════════════════════════════════════════
#: ★★★ 2026-10-07（接手轮 · 规格 214 T-214-12）**装假模块 + `import sw_part` 一起搬进 fixture** ——
#:   ★ 原来这两步在**模块级**（收集期就执行），★ 而**从不还原** ⇒ ★★ 污染面比"后面所有测试"**更大**：
#:     · ★ **收集期就装上了** —— 而 pytest **收集阶段会把所有测试模块 import 完**，
#:       早于**任何一条用例执行** ⇒ ★★ 于是**在本文件之前跑**的用例也拿到假模块 ✗✗
#:     · ★ 实测（`-k` 只跑一条时的忠实复现）：
#:       `test_com_member_helpers::test_call_com_member_exists_and_is_documented` 报
#:       「`assert '就是去调它' in '测试用 COM 成员读取器'`」 —— ★ 那句 docstring 正是本文件的
#:       `fake_get_com_member` ⇒ ★ 它拿到的是**本文件的假模块** ✓
#:     · ★★ 为什么会"时绿时红"：★ 本文件的用例若**先跑**，fixture 的 teardown 会把真模块还回去
#:       ⇒ 后面的用例就绿；★ 而 `test_com_member_helpers`（**c**）在字母序上**早于**本文件（**s**）
#:       ⇒ 它跑的时候假模块**还挂着** ✗ ⇒ ★ 全量必红、而"本文件 + 它"两个文件跑却绿 ✓
#:         （★ 这就是本轮二分**查不出单文件**的原因 —— ★ 它不是"谁污染了谁"，而是
#:          **收集期装的东西落在了先跑的用例头上**）
#:   ⇒ ★★★ **正解**：★ **装假模块与 `import sw_part` 都在 fixture 里做**（module 作用域 autouse）
#:     ⇒ ★ 收集期**不碰** `sys.modules` ⇒ ★ teardown 再原样还回去 ⇒ **两个方向都不漏** ✓
#:   ⚠ **为什么不能"import 完就撤"**：★ `scripts/sw_part.py` 的 `_select_com_object`（L334）与
#:     `create_axis_report`（L2174）是**函数内** `from sw_connect import …` ⇒ ★ 那两条路要到
#:     **用例执行期**才导入 ⇒ ★ 撤早了它们会拿到**真的** `sw_connect`（★ 于是真去连 COM）✗
#:   ⚠ 同类定则（本规格已修三处）：★ **凡改**共享模块/`sys.modules` 的全局态**，一律走
#:     `monkeypatch` 或**成对的 fixture 装/撤**，★ 不许在模块级裸做** ✓
#: ═══════════════════════════════════════════════════════════════════════════
@pytest.fixture(scope="module", autouse=True)
def _fake_modules_then_import_sw_part():
    """★ 用例开始前装假模块并 `import sw_part`；★ 本模块跑完**原样还回去** ✓"""
    global sw_part
    sys.modules["sw_connect"] = _fake_connect
    sys.modules["sw_preflight"] = types.SimpleNamespace(
        import_com_dependencies=lambda: (
            types.SimpleNamespace(VT_DISPATCH=9),
            types.SimpleNamespace(),
            FakeVariant,
        )
    )
    try:
        import sw_part as _sw_part_module
        sw_part = _sw_part_module
        yield
    finally:
        for _name, _saved in (("sw_connect", _saved_sw_connect),
                              ("sw_preflight", _saved_sw_preflight)):
            if _saved is None:
                sys.modules.pop(_name, None)      # ★ 本来就没有 ⇒ 撤掉本模块塞的
            else:
                sys.modules[_name] = _saved       # ★ 本来是谁就还谁（★ 可能是真模块）✓


#: ═══════════════════════════════════════════════════════════════════════════
#: ★ 2026-10-07（接手轮 · 规格 214 T-214-12）：★ 早先我在这里单独加过一个"只还回去"的 fixture ——
#:   ★★ **已删**，★ 因为它**治不了根**：装假模块那一步仍在**模块级**（收集期就执行），
#:   而**先于本文件跑**的用例照样拿到假模块（★ `test_com_member_helpers` 就是这么中招的）✗
#:   ⇒ ★★★ **现在装与撤在同一个 fixture 里**（见上面 `_fake_modules_then_import_sw_part`）——
#:     ★ 收集期**不碰** `sys.modules` ⇒ ★ **两个方向都不漏** ✓
#: ═══════════════════════════════════════════════════════════════════════════


class FakeFeature:
    """模拟 SolidWorks Feature 对象。"""

    def __init__(self, name):
        self.Name = name
        self.selected = False

    def Select2(self, append, mark):
        """模拟对象级选择成功。"""
        self.selected = True
        return True


class FakeSketch:
    """模拟 SolidWorks Sketch 对象。"""

    def __init__(self, name):
        self.Name = name
        self.feature = FakeFeature(name)

    def GetFeature(self):
        """返回草图对应特征。"""
        return self.feature


class FakeSketchManager:
    """模拟 SketchManager。"""

    def __init__(self, sketch):
        self.ActiveSketch = None
        self.sketch = sketch

    def InsertSketch(self, _update_edit_rebuild):
        """进入或退出草图。"""
        self.ActiveSketch = self.sketch if self.ActiveSketch is None else None


class FakeSelectionManager:
    """模拟空选择集。"""

    def GetSelectedObjectCount2(self, _mark):
        """始终返回空选择集。"""
        return 0


class FakeExtension:
    """模拟 SelectByID2 对 SKETCH 失败、对 PLANE 成功。"""

    def __init__(self):
        self.calls = []

    def SelectByID2(self, name, entity_type, *_args):
        """记录选择调用，并故意让 SKETCH 名称选择失败。"""
        self.calls.append((name, entity_type))
        return entity_type == "PLANE"


class FakeFeatureManager:
    """模拟拉伸特征管理器。"""

    def __init__(self, model):
        self.model = model

    def FeatureExtrusion3(self, *_args):
        """只有对象级选择发生后才创建特征。"""
        if self.model.sketch.feature.selected:
            return FakeFeature("Boss-Extrude1")
        return None


class FakeModel:
    """模拟最小 IModelDoc2。"""

    def __init__(self):
        self.sketch = FakeSketch("草图1")
        self.Extension = FakeExtension()
        self.SketchManager = FakeSketchManager(self.sketch)
        self.SelectionManager = FakeSelectionManager()
        self.FeatureManager = FakeFeatureManager(self)
        self.clear_calls = 0

    def ClearSelection2(self, _clear_all):
        """记录清空选择集。"""
        self.clear_calls += 1

    def FeatureByName(self, _name):
        """模拟中文 SW 中按名称找不到草图。"""
        return None


class SketchSelectionTests(unittest.TestCase):
    """验证草图选择不依赖残留选择集或 SelectByID2("SKETCH")。"""

    def test_extrude_uses_cached_sketch_object_when_select_by_id_fails(self):
        """选择集为空且 SKETCH 名称选择失败时仍应拉伸成功。"""
        model = FakeModel()

        with sw_part.sketch(model, "Front Plane") as sketch_name:
            self.assertEqual(sketch_name, "草图1")

        feature = sw_part.extrude_boss(model, sketch_name, 0.01)

        self.assertIsNotNone(feature)
        self.assertTrue(model.sketch.feature.selected)
        self.assertNotIn(("草图1", "SKETCH"), model.Extension.calls)


if __name__ == "__main__":
    unittest.main()

# ── 轮 127：边界框（`bbox`）──────────────────────────────────────────
# ⚠ 本文件用 `unittest` 且**打桩了 `sw_connect`**（只有 `get_com_member`，没有 `mm`），
#   所以这里也用 `unittest`，并**不依赖**任何未打桩的成员。

class BBoxTests(unittest.TestCase):
    """@brief ★★ `GetBodyBox` 的原始值**就是毫米** —— 不许再乘除 1000。

    真机实测（轮 127）：**80 × 60 × 50 mm** 的盒子，`GetBodyBox` 返回
    `[0.0, 0.0, -50.0, 80.0, 60.0, 0.0]` ⇒ 原始值就是 80/60/50。
    ⚠ 第一版误用了 `sw_connect.mm()`（**输入方向**：毫米→米）⇒ 被数值冒烟当场抓住。
    ⚠ 谁把换算加回来，这条会红。
    """

    class _Body:
        def GetBodyBox(self):      # noqa: N802
            return [0.0, 0.0, -50.0, 80.0, 60.0, 0.0]      # ⚠ 单位是**毫米**

    class _Model:
        def GetBodies2(self, _i, _h):      # noqa: N802
            return [BBoxTests._Body()]

    def test_returns_raw_millimetres(self):
        box = sw_part.get_bounding_box(self._Model())
        self.assertEqual(box["size"], [80.0, 60.0, 50.0])
        self.assertEqual(box["min"], [0.0, 0.0, -50.0])
        self.assertEqual(box["max"], [80.0, 60.0, 0.0])

    def test_documents_the_official_approximate_warning(self):
        """@brief ★★ 官方明说该值**近似**、**不应用于比较或计算** ⇒ 源码要照抄。

        ⚠ 不能因为"实测偏差为 0"就把这句删掉 —— **两者说的是不同的事**。
        """
        src = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
        i = src.index("def get_bounding_box")
        # ⚠ 往前多取一段 —— 官方的 "approximate" 原文在**来源块**里（在 def **之前**）
        body = src[max(0, i - 2200):i + 2600]
        self.assertIn("approximate", body)
        self.assertIn("毫米", body)
        self.assertIn("实测", body)

    def test_raises_when_no_body_or_wrong_length(self):
        class _Empty:
            def GetBodies2(self, _i, _h):      # noqa: N802
                return []

        class _ShortBody:
            def GetBodyBox(self):      # noqa: N802
                return [1.0, 2.0]

        class _Short:
            def GetBodies2(self, _i, _h):      # noqa: N802
                return [_ShortBody()]

        with self.assertRaises(RuntimeError):
            sw_part.get_bounding_box(_Empty())
        with self.assertRaises(RuntimeError) as cm:
            sw_part.get_bounding_box(_Short())
        self.assertIn("6", str(cm.exception))

# ── 轮 132：椭圆 + **单位是毫米**（docstring 曾写错）────────────────

class EllipseAndUnitTests(unittest.TestCase):
    """@brief ★ `sketch_ellipse` 走**现行入口**；★ 长度单位是**毫米**。"""

    def test_ellipse_uses_the_current_entry(self):
        """@brief ★★ 走 `ISketchManager.CreateEllipse`，**不走**两条已废弃的旧路。

        官方废弃链（两级）：
          `IModelDoc2.CreateEllipse` ⇒ Superseded by `IModelDoc2::CreateEllipse2`
          `IModelDoc2.CreateEllipse2` ⇒ Superseded by `ISketchManager::CreateEllipse`
        """
        src = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
        i = src.index("def sketch_ellipse")
        impl = src[i:i + 1600]
        assert "CreateEllipse" in impl
        #: ⚠ 查**调用形态**（带引号的成员名），不查裸名字 ——
        #:   说明文字里**必须**提到那两条废弃路径（否则读者不知道有坑）
        assert '"CreateEllipse2"' not in impl, "不许调已废弃的 CreateEllipse2"
        assert "两级废弃链" in src, "来源块要写明那两级废弃"

    def test_ellipse_signature_is_nine_doubles(self):
        """@brief 官方 9 个 double：中心 + 长轴上一点 + 短轴上一点。"""
        params = list(inspect.signature(sw_part.sketch_ellipse).parameters)
        assert params[:7] == ["model", "cx", "cy", "major_x", "major_y",
                              "minor_x", "minor_y"], params

    def test_ellipse_raises_when_nothing_created(self):
        """@brief 官方返回 `None` ⇒ **抛**（不静默成功）。"""

        class _SketchMgr:
            def CreateEllipse(self, *a):      # noqa: N802
                return None

        class _M:
            @property
            def SketchManager(self):      # noqa: N802
                return _SketchMgr()

        with self.assertRaises(RuntimeError):
            sw_part.sketch_ellipse(_M(), 0.0, 0.0, 40.0, 0.0, 0.0, 20.0)

    def test_module_documents_millimetres_not_metres(self):
        """@brief ★★ 模块级必须写明**长度单位是毫米**（此前多处写"米"，与实际不符）。

        实测：半径 25 的圆 ⇒ 边界框跨度 **50**（毫米）；拉伸 10 ⇒ 跨度 **10**（毫米）。
        ⚠ 谁把这条说明删掉、或让 docstring 再出现裸的"（单位: 米）"，这条会红。
        """
        src = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
        assert "长度单位" in src and "毫米" in src, "模块头要写明单位"
        assert "（单位: 米）" not in src, "不许再有裸的「（单位: 米）」"
        assert "实测" in src, "要写明这是实测校正的"
