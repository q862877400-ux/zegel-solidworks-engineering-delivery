"""★ `Get/SetSystemValue3` 的单位契约：系统单位是**米**，与文档单位无关。

## 这份测试补的是什么

`tests/test_sw_document_data.py` 里的假文档 `FakeModelForUnits` **特意声明自己是米文档**
（`swLengthUnit_e = 2`），所以「毫米文档」这个**真实默认**从来没被测过。

⇒ 旧实现按 `GetUnits()` 推倍数：毫米文档得 `1.0` ⇒ **读** 100 mm 的尺寸得 `0.1`、
   **写** 120 mm 变成 `120 米`，读写两侧都差 1000 倍，而米文档的测试照样绿。

## 判据（真机几何证据）

`tools/probe_s3_dimension_units.py` 在**毫米文档**（`GetUnits() = [0, 1, 8, 2, 0]`）上实测：

```
一条 100 mm 宽的驱动尺寸：SystemValue = 0.1 · GetSystemValue3(1,None) = [0.1]
SetSystemValue3(0.15, 1, None) → 返回 0（success）
  改后：SystemValue = 0.15 · GetSystemValue3 = [0.15]
  ★ 包围盒 X 跨度：100.0 mm → 150.0 mm      ← 几何证实
```

⇒ 写 `0.15` 得到 150 mm ⇒ **单位是米**。官方 `SetSystemValue3.md` 逐字：
「Sets the value of this dimension in **system units (meters)**」。

详见 `docs/state/facts/R-engineering-path.md` R-19。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import sw_connect  # noqa: E402
import sw_document_data as D  # noqa: E402


class FakeDim:
    """★ 一条尺寸；内部**以米存放**（官方系统单位）。"""

    def __init__(self, value_m: float = 0.1) -> None:
        self.value_m = value_m
        self.last_set = None

    def GetSystemValue3(self, mode, names):        # noqa: N802
        return (self.value_m,)

    def SetSystemValue3(self, value, mode, names):  # noqa: N802
        self.last_set = value
        self.value_m = value
        return 0


class _Model:
    def __init__(self, unit_code: int) -> None:
        self._u = [unit_code, 1, 8, 2, 0]

    def GetUnits(self):                            # noqa: N802
        return self._u

    def Parameter(self, name):                     # noqa: N802
        return _DIM


#: `update_dimension_mm` 会先 `model.Parameter(name)` 拿尺寸 ⇒ 用模块级替身
_DIM = FakeDim(0.1)


def _patch_empty(monkeypatch) -> None:
    """★ `_dimension_value_mm` 内部 `from .sw_connect import create_empty_dispatch_variant`
    ⇒ 必须 patch **`sw_connect`** 上的那个名字，patch 本模块没用。
    """
    monkeypatch.setattr(sw_connect, "create_empty_dispatch_variant", lambda: object())


def test_毫米文档上读_0_1_米得_100mm(monkeypatch) -> None:
    """★★ 核心回归：毫米文档 + 系统值 0.1 m ⇒ 必须读成 **100 mm**。

    ★ 旧实现在这里回 **0.1**（差 1000 倍）—— 这就是 T008 卡住的原因。
    """
    _patch_empty(monkeypatch)
    got = D._dimension_value_mm(FakeDim(0.1), model=_Model(0))
    assert got == 100.0, "★ 0.1 米应读成 100 mm，实得 %r" % got


def test_文档单位不影响读数(monkeypatch) -> None:
    """★★ 系统单位按定义是米 ⇒ 换文档单位，读数必须一样。

    ★ 旧实现会随 `GetUnits()` 变（毫米 1.0 / 厘米 10.0 / 米 1000.0）—— 那是错的。
    """
    _patch_empty(monkeypatch)
    vals = [
        D._dimension_value_mm(FakeDim(0.1), model=_Model(code)) for code in (0, 1, 2)
    ]
    assert vals == [100.0, 100.0, 100.0], "★ 三种文档单位应读同一值，实得 %r" % vals


def test_update_dimension_mm_在毫米文档上传_0_12(monkeypatch) -> None:
    """★★ 核心回归：写 120 mm ⇒ `SetSystemValue3` 收到的必须是 **0.12**（米）。

    ★ 旧实现在毫米文档上传 **120**（当成米）⇒ 几何变成 120 米。
    """
    _patch_empty(monkeypatch)
    global _DIM
    _DIM = FakeDim(0.1)
    D.update_dimension_mm(_Model(0), "D1@Sketch1", 120.0, rebuild=False, save=False)
    assert _DIM.last_set is not None, "★ 没调到 SetSystemValue3"
    assert abs(_DIM.last_set - 0.12) < 1e-12, (
        "★ 120 mm 应传 0.12 米，实得 %r" % _DIM.last_set
    )


def test_update_dimension_mm_不随文档单位变(monkeypatch) -> None:
    """★ 写成米这件事与文档单位无关。"""
    _patch_empty(monkeypatch)
    for code in (0, 1, 2):
        global _DIM
        _DIM = FakeDim(0.1)
        D.update_dimension_mm(_Model(code), "D1@Sketch1", 120.0, rebuild=False, save=False)
        assert abs(_DIM.last_set - 0.12) < 1e-12, (
            "★ 文档单位 code=%d 时仍应传 0.12，实得 %r" % (code, _DIM.last_set)
        )


def test_换算常量是固定的_1000() -> None:
    """★ `SYSTEM_UNIT_MM` 是**定义**（米→毫米固定 1000），不是从文档单位探出来的。"""
    assert D.SYSTEM_UNIT_MM == 1000.0


def test_不再把文档单位接进系统值换算() -> None:
    """★ 这条防后人「顺手」把 `_document_length_unit_scale` 接回来。

    ★ 它是**另一种**换算（文档单位→毫米），与 `Get/SetSystemValue3` 的**系统单位（米）**
      不是一回事。接回来就会重新引入 1000 倍偏差。
    """
    src = (REPO / "scripts" / "sw_document_data.py").read_text(encoding="utf-8")
    assert "return float(raw) * SYSTEM_UNIT_MM" in src, "读侧未用固定 1000"
    assert "float(value_mm) / SYSTEM_UNIT_MM" in src, "写侧未用固定 1000"
    assert "_scale = _document_length_unit_scale" not in src, (
        "★ 又把文档单位接回系统值换算了 —— 会重新引入 1000 倍偏差"
    )
