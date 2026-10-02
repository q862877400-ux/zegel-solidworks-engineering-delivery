"""草图编辑模块的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_sketch_edit_contract.py
# 定位:   守 `scripts/sw_sketch_edit.py`（轮 105：从「真缺」档补的第二批）。
# 官方签名依据: 出厂反射 + `C:\\swapi\\types\\ISketchManager\\CreateChamfer.md`
#               + `C:\\swapi\\types\\IModelDoc2\\SketchMirror.md`
# 许可:   本仓库 MIT。无第三方代码引入。
#
# ★ **本文件最重要的一条是「枚举冲突」那条**：
#   `swSketchChamfer_DistanceDistance` 在 `C:\\swapi` 的 md 里写 **-1**、
#   在出厂反射里写 **1**。铁律 4 说**冲突以出厂类型库为准** ⇒ 实现取 **1**。
#   本测试把 1 **独立抄一份**，任何人改成 -1 都会红。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from scripts import sw_sketch_edit  # noqa: E402


#: ★ **出厂反射**的值 —— 铁律 4：两源冲突时以它为准。
#: ⚠ 与 `C:\swapi\enums\swSketchChamferType_e.md` 的 **-1** 冲突（那条是 md 的）。
REFLECTION_CHAMFER_TYPE = {
    "distance_angle": 0,
    "distance_distance": 1,
    "distance_equal": 2,
}


def test_chamfer_enum_follows_the_type_library_not_the_markdown():
    """@brief ★ 枚举冲突时**取出厂反射**（铁律 4）—— 本模块的核心判据。"""
    assert sw_sketch_edit.SKETCH_CHAMFER_TYPE == REFLECTION_CHAMFER_TYPE
    assert sw_sketch_edit.SKETCH_CHAMFER_TYPE["distance_distance"] == 1, \
        "md 写 -1、反射写 1 ⇒ 必须取 1（铁律 4）"


def test_mirror_marks_match_the_official_doc():
    """@brief 镜像的**选中标记**：线段 1 / 中心线 2（官方写明）。"""
    assert sw_sketch_edit.SKETCH_MIRROR_MARK == {"segment": 1, "centerline": 2}


def test_chamfer_signature_has_three_official_arguments_in_order():
    """@brief 官方 `CreateChamfer(Int32, Double, Double)` —— 3 参，顺序照官方。"""
    params = list(inspect.signature(sw_sketch_edit.create_sketch_chamfer).parameters)
    assert params[0] == "model"
    assert params[1:] == ["chamfer_type", "distance_mm", "angle_or_distance"]


def test_mirror_takes_no_official_arguments():
    """@brief 官方 `SketchMirror()` **0 参** —— 本模块只多一个 `model`。"""
    params = list(inspect.signature(sw_sketch_edit.sketch_mirror).parameters)
    assert params == ["model"], "官方 0 参 ⇒ 除了 model 不该有别的"


class _FakeSeg:
    pass


class _FakeSketchManager:
    def __init__(self, seg=None, sketch=object()):
        self.calls = []
        self._seg = seg
        self._sketch = sketch

    def CreateChamfer(self, *args):      # noqa: N802
        self.calls.append(args)
        return self._seg

    @property
    def ActiveSketch(self):
        return self._sketch


class _FakeModel:
    def __init__(self, skm):
        self._skm = skm
        self.mirror_calls = 0

    @property
    def SketchManager(self):
        return self._skm

    def SketchMirror(self):      # noqa: N802
        self.mirror_calls += 1


def test_chamfer_passes_mm_converted_distance():
    """@brief `distance_mm` 必须在**边界**换算成米（并入规则 2）。"""
    seg = _FakeSeg()
    skm = _FakeSketchManager(seg=seg)
    m = _FakeModel(skm)
    out = sw_sketch_edit.create_sketch_chamfer(m, distance_mm=2.5)
    assert out is seg
    (args,) = skm.calls
    assert args[0] == 0, "默认 distance_angle = 0"
    assert args[1] == pytest.approx(0.0025), "2.5 mm 应换算成 0.0025 米"


def test_chamfer_raises_when_nothing_selected():
    """@brief ★ 没选中两条实体时抛**带原因**的 `RuntimeError`（不许静默成功）。"""
    m = _FakeModel(_FakeSketchManager(seg=None))
    with pytest.raises(RuntimeError) as ei:
        sw_sketch_edit.create_sketch_chamfer(m, distance_mm=1.0)
    msg = str(ei.value)
    assert "两条草图实体" in msg, msg


def test_mirror_raises_when_not_in_sketch_edit_mode():
    """@brief 不在草图编辑态时抛**带原因**的错（并点明标记）。"""
    m = _FakeModel(_FakeSketchManager(sketch=None))
    with pytest.raises(RuntimeError) as ei:
        sw_sketch_edit.sketch_mirror(m)
    msg = str(ei.value)
    assert "草图编辑态" in msg, msg
    assert "mark=1" in msg and "mark=2" in msg, "必须点明官方标记"


def test_mirror_calls_the_official_zero_arg_member():
    """@brief 进到草图态时应调官方的 0 参 `SketchMirror()`。"""
    m = _FakeModel(_FakeSketchManager())
    assert sw_sketch_edit.sketch_mirror(m) is True
    assert m.mirror_calls == 1



# ── convert_entities（轮 115：从「真缺」档补）────────────────────────

def test_convert_entities_uses_the_current_entry_not_the_obsolete_one():
    """@brief ★ 走 `ISketchManager.SketchUseEdge3`，**不走**已废弃的 `SketchUseEdge2`。

    官方 md 明写 `IModelDoc2.SketchUseEdge2` 是
    `Obsolete. Superseded by ISketchManager::SketchUseEdge.`
    """
    t = (REPO_ROOT / "scripts" / "sw_sketch_edit.py").read_text(encoding="utf-8")
    assert "SketchUseEdge3" in t
    assert "SketchUseEdge2" not in t.split("# ── 来源")[0], "实现里不许用已废弃的入口"
    assert "Obsolete" in t, "来源块应记下「为什么不用 SketchUseEdge2」"


def test_convert_entities_signature_follows_official():
    """@brief 官方 `SketchUseEdge3(Boolean Chain, Boolean InnerLoops)` —— 两参。"""
    params = list(inspect.signature(sw_sketch_edit.convert_entities).parameters)
    assert params[0] == "model"
    assert "chain" in params and "inner_loops" in params


class _FakeSketchManagerWithEdge:
    def __init__(self, ret=True, sketch=object()):
        self.calls = []
        self._ret = ret
        self._sketch = sketch

    def SketchUseEdge3(self, *args):      # noqa: N802
        self.calls.append(args)
        return self._ret

    @property
    def ActiveSketch(self):
        return self._sketch


def test_convert_entities_passes_both_official_arguments_in_order():
    """@brief 两个实参按官方顺序：`(Chain, InnerLoops)`。"""
    skm = _FakeSketchManagerWithEdge(ret=True)
    m = _FakeModel(skm)
    assert sw_sketch_edit.convert_entities(m, chain=False, inner_loops=True) is True
    assert skm.calls == [(False, True)]


def test_convert_entities_defaults_match_the_official_meaning():
    """@brief 默认 `chain=True`（整条链）/ `inner_loops=False`（不转内环）。"""
    skm = _FakeSketchManagerWithEdge(ret=True)
    sw_sketch_edit.convert_entities(_FakeModel(skm))
    assert skm.calls == [(True, False)]


def test_convert_entities_raises_when_official_returns_false():
    """@brief ★ 官方失败返回 `False` ⇒ **必须抛带原因的错**（不许静默成功）。

    ⚠ 这是本函数最要紧的一条：`False` 是"假值"，**很容易被 `if not got: pass` 吞掉**。
    """
    skm = _FakeSketchManagerWithEdge(ret=False)
    with pytest.raises(RuntimeError) as ei:
        sw_sketch_edit.convert_entities(_FakeModel(skm))
    msg = str(ei.value)
    assert "选中" in msg, msg


def test_convert_entities_raises_when_not_in_sketch_manager():
    """@brief 拿不到 `SketchManager` 时抛**带原因**的错。"""
    with pytest.raises(RuntimeError):
        sw_sketch_edit.convert_entities(_FakeModel(None))

def test_module_declares_stitched_and_records_the_conflict():
    """@brief ★ 来源块必须写明 `stitched` + **记下枚举冲突**（铁律 4 的活例）。"""
    t = (REPO_ROOT / "scripts" / "sw_sketch_edit.py").read_text(encoding="utf-8")
    assert "stitched" in t
    assert "无本机运行证据" in t or "没有本机运行证据" in t
    assert "冲突以出厂类型库为准" in t


def test_module_uses_the_non_obsolete_entry_point():
    """@brief ★ 必须走**非废弃**入口 —— 官方明写 `SketchChamfer` 是 Obsolete。"""
    t = (REPO_ROOT / "scripts" / "sw_sketch_edit.py").read_text(encoding="utf-8")
    assert "CreateChamfer" in t
    assert "Obsolete" in t, "来源块应记下「为什么不用 SketchChamfer」"
