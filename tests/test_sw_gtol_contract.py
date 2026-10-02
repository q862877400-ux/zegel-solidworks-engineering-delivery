"""GTol 模块的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

#: ⚠⚠⚠ **2026-10-01（轮 166）本文件把 `tol_type=22` 改成了 `22`，理由**：
#: 官方 `IGtolFrame.AddIndicator` 的 Remarks 明写 `TolType` **只能是 5 个**
#: （`swGcsANG`20 / `swGcsPARALLEL`22 / `swGcsPERP`21 / `swGcsCIRCRUNOUT`25 / `swGcsSYMMETRY`13）。
#: `position`(23) **不在清单里** ⇒ 真机**必然返回 False**，而**本文件有几个测试原来在断言它会成功**
#: ⇒ ★ 是**测试用了非法值**（假对象看不见这条官方限制）。
#: ★ 已给 `add_gtol_indicator` 加**清单校验**（错值当场 `ValueError`），测试随之改用**清单内**的值。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_gtol_contract.py
# 定位:   守 `scripts/sw_gtol.py`（轮 119：从「真缺」档补的第五条能力）。
# 官方签名依据: 出厂反射 + `C:\\swapi\\types\\IGtol*\\*.md`
# 许可:   本仓库 MIT。无第三方代码引入。
#
# ★ 本模块**没有真机运行证据**（`stitched`）⇒ **静态判据是唯一防线**。
#   重点钉两件事：① **两条枚举的值**（照出厂反射独立抄一份）；
#   ② ★ **不走那条"只对 2022 之前有效"的旧路径**。
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

from scripts import sw_gtol  # noqa: E402


#: ★ **出厂反射**的值（独立抄一份 —— 实现里被改错这条会红）。
REFLECTION_BORDER = {"orientation_plane": 0, "intersection_plane": 1,
                     "collection_plane": 2, "direction_feature": 3}
REFLECTION_SYMBOL = {
    "none": 12, "symmetry": 13, "straightness": 14, "flatness": 15,
    "circularity": 16, "cylindricity": 17, "line_profile": 18, "surface_profile": 19,
    "angularity": 20, "perpendicularity": 21, "parallelism": 22, "position": 23,
    "concentricity": 24, "circular_runout": 25, "total_runout": 26,
    "circ_open_runout": 27, "total_open_runout": 28, "u_button": 29, "square": 30,
}


def test_border_enum_matches_the_type_library():
    """@brief `swGtolIndicatorBorderType_e` 必须与出厂反射一致。"""
    assert sw_gtol.GTOL_INDICATOR_BORDER == REFLECTION_BORDER


def test_geom_symbol_enum_matches_the_type_library():
    """@brief `swGtolGeomCharSymbol_e` 必须与出厂反射一致（**全 19 项**）。"""
    assert sw_gtol.GTOL_GEOM_SYMBOL == REFLECTION_SYMBOL
    assert len(sw_gtol.GTOL_GEOM_SYMBOL) == 19, "反射里就这 19 个，多一个少一个都要查"


def test_first_frame_is_one_based_per_official_doc():
    """@brief 官方 `GetFrame` 的 `FrameIndex` 是 **1 基**。"""
    assert sw_gtol.FIRST_FRAME == 1


def test_module_avoids_the_pre_2022_only_path():
    """@brief ★★ **不走** `SetFrameSymbols2` —— 官方明写它只对 **2022 之前**建的 Gtol 有效。

    ⚠ 这是本模块最要紧的一条：走那条路在 SW 2026 上**根本无效**，
    而且它的符号参数是**字形串**（文本协议传不了）。
    """
    t = (REPO_ROOT / "scripts" / "sw_gtol.py").read_text(encoding="utf-8")
    impl = t.rsplit("# ── 来源", 1)[0]
    assert "AddIndicator" in impl
    # ⚠ 查**调用形态**（带引号的成员名），不查裸名字 ——
    #   文档串里**必须**提到 `SetFrameSymbols2`（解释为什么不走它），
    #   裸名字会被自己的说明文字误伤（**第一版就这样错了**）。
    assert '"SetFrameSymbols2"' not in impl, "实现里不许**调用**只对 2022 之前有效的旧路径"
    assert "earlier than 2022" in t, "来源块要**原文**记下那句话"


def test_module_declares_stitched():
    """@brief 来源块必须写明等级 `stitched` 且**无本机运行证据**。"""
    t = (REPO_ROOT / "scripts" / "sw_gtol.py").read_text(encoding="utf-8")
    assert "stitched" in t
    assert "无本机运行证据" in t or "没有本机运行证据" in t


def test_insert_gtol_takes_no_official_arguments():
    """@brief 官方 `IModelDoc2.InsertGtol()` —— **0 参**。"""
    params = list(inspect.signature(sw_gtol.insert_gtol).parameters)
    assert params == ["model"], "官方 0 参 ⇒ 除了 model 不该有别的"


def test_add_indicator_signature_follows_official():
    """@brief 官方 `AddIndicator(Int32 BorderType, Int32 TolType, String Datum)`。"""
    params = list(inspect.signature(sw_gtol.add_gtol_indicator).parameters)
    assert params[0] == "gtol"
    for n in ("tol_type", "datum", "border_type", "frame"):
        assert n in params, n


class _FakeFrame:
    def __init__(self, ret=True):
        self.calls = []
        self._ret = ret

    def AddIndicator(self, *args):      # noqa: N802
        self.calls.append(args)
        return self._ret


class _FakeGtol:
    """桩：`GetFrameCount` 可配，`AddFrame` 会把它 +1（模拟官方语义）。"""

    def __init__(self, frame=None, count=1, add_ok=True):
        self._frame = frame
        self._count = count
        self._add_ok = add_ok
        self.frame_calls = []
        self.add_calls = 0

    def GetFrameCount(self):        # noqa: N802
        return self._count

    def AddFrame(self):             # noqa: N802
        self.add_calls += 1
        if not self._add_ok:
            return False
        self._count += 1
        return True

    def GetFrame(self, i):      # noqa: N802
        self.frame_calls.append(i)
        return self._frame


class _FakeModel:
    def __init__(self, gtol):
        self._g = gtol

    @property
    def InsertGtol(self):      # noqa: N802
        return self._g



# ── 轮 120：真机冒烟查出的那一步（帧要先存在）──────────────────────

def test_add_indicator_ensures_the_frame_exists_first():
    """@brief ★ **新 GTol 可能一帧都没有** ⇒ 取帧前必须补帧。

    ⚑ 轮 120 真机实测：`InsertGtol()` 建的 GTol `GetFrameCount()` 可能是 0/1，
    而 `GetFrame(1)` **返回 None** ⇒ 轮 119 的实现就栽在这里。
    """
    fr = _FakeFrame(ret=True)
    g = _FakeGtol(frame=fr, count=0)          # 一帧都没有
    assert sw_gtol.add_gtol_indicator(g, tol_type=22) is True
    assert g.add_calls == 1, "应当补 1 帧"
    assert g.frame_calls == [1]


def test_add_indicator_does_not_add_frames_when_already_enough():
    """@brief 帧已经够时**不该多补**（补帧会改 Gtol 状态）。"""
    g = _FakeGtol(frame=_FakeFrame(ret=True), count=1)
    sw_gtol.add_gtol_indicator(g, tol_type=22)
    assert g.add_calls == 0


def test_ensure_gtol_frame_rejects_zero_based_index():
    """@brief `frame` 是**1 基**，传 0 要拦下（官方 `FrameIndex` 1 基）。"""
    with pytest.raises(ValueError):
        sw_gtol.ensure_gtol_frame(_FakeGtol(), 0)


def test_ensure_gtol_frame_raises_when_count_does_not_grow():
    """@brief ★ `AddFrame()` 之后计数不涨 ⇒ **抛**（说明该 Gtol 不是 2022 格式）。"""
    with pytest.raises(RuntimeError) as ei:
        sw_gtol.ensure_gtol_frame(_FakeGtol(count=0, add_ok=False), 1)
    assert "2022" in str(ei.value), str(ei.value)


def test_add_gtol_frame_raises_on_false():
    """@brief `AddFrame()` 返回 `False` ⇒ **抛**（不静默）。"""
    with pytest.raises(RuntimeError):
        sw_gtol.add_gtol_frame(_FakeGtol(add_ok=False))


def test_module_documents_that_the_frame_path_is_unreachable_on_this_machine():
    """@brief ★★ **本轮最重要的判据**：源码里必须**如实写明**那条路在这台机器上到不了。

    ⚠ 没有这条，下一个人会以为 `add_gtol_indicator` 是能用的。
    """
    t = (REPO_ROOT / "scripts" / "sw_gtol.py").read_text(encoding="utf-8")
    assert "验证等级：分成两半" in t, "文件头要分开声明两半的等级"
    assert "不可用" in t
    assert "事实 53" in t, "要写明为什么停手"

def test_insert_gtol_raises_when_nothing_created():
    """@brief 建不出来时抛**带原因**的 `RuntimeError`。"""
    with pytest.raises(RuntimeError) as ei:
        sw_gtol.insert_gtol(_FakeModel(None))
    assert "InsertGtol" in str(ei.value)


def test_add_indicator_passes_three_official_arguments_in_order():
    """@brief 三个实参按官方顺序：`(BorderType, TolType, Datum)`。"""
    fr = _FakeFrame(ret=True)
    g = _FakeGtol(frame=fr)
    assert sw_gtol.add_gtol_indicator(
        g, tol_type=sw_gtol.GTOL_GEOM_SYMBOL["parallelism"], datum="A") is True
    assert g.frame_calls == [1], "默认取第 1 帧（1 基）"
    #: ⚠ TolType 是 **22**（`parallelism`）—— 官方 Remarks 只允许 5 个
    #: （20/22/21/25/13），`position`(23) **不在清单里** ⇒ 改用清单内的值。
    assert fr.calls == [(0, 22, "A")], "顺序必须是 (BorderType, TolType, Datum)"


def test_add_indicator_raises_on_false_and_on_missing_frame():
    """@brief ★ 官方返回 `False` 或取不到帧 ⇒ **都要抛**（不许静默成功）。"""
    with pytest.raises(RuntimeError):
        sw_gtol.add_gtol_indicator(_FakeGtol(frame=_FakeFrame(ret=False)),
                                   tol_type=22)
    with pytest.raises(RuntimeError) as ei:
        sw_gtol.add_gtol_indicator(_FakeGtol(frame=None), tol_type=22)
    assert "1 基" in str(ei.value), "错误信息要点出下标是 1 基"
