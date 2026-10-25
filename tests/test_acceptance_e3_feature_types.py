"""★ `e3_feature_types` 的契约：类型词表**全部来自真机实测**，不许凭印象。

## 真机读数（第 15 / 16 轮，`tools/probe_s3_e3_feature_tree.py` 与
## `tools/probe_s3_e3_imported_solid_negative.py`）

| 特征 | `GetTypeName2` 实测值 |
|---|---|
| 草图 | `ProfileFeature` |
| 凸台-拉伸 | `Extrusion` |
| **切除-拉伸** | **`ICE`** |
| 前/上/右视基准面 | `RefPlane` |
| 原点 | `OriginProfileFeature` |
| Tables | `ConfigTableFolder` |
| **导入的 STEP 实体** | **`MBimport`** |

## 为什么这份测试重要

E3 要判「原生特征 vs 导入死实体」。而**导入的 STEP 零件也带**三个基准面、原点和 Tables
（实测 6 个特征里 5 个是这类）⇒ 若把基准面算成「原生」，
「导入死实体」就会被判 pass —— 那正是 E3 明令要拒的伪造手法。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance import e3_feature_types as T  # noqa: E402


def test_交付件15个特征分对() -> None:
    """★ 第 15 轮真机：交付件 15 个特征 = 原生几何 10 + 基础设施 5。"""
    types = (
        ["RefPlane"] * 3
        + ["OriginProfileFeature", "ConfigTableFolder"]
        + ["ProfileFeature", "Extrusion"]
        + ["ProfileFeature", "ICE"] * 4
    )
    got = T.tally([{"type": t} for t in types])
    assert got["native"] == 10, "★ 原生几何特征应为 10，实得 %d" % got["native"]
    assert got["infra"] == 5
    assert got["import"] == 0
    assert got["unknown"] == 0


def test_导入体6个特征分对() -> None:
    """★★ 第 16 轮真机：导入 STEP 的零件 = 原生几何 **0** + 基础设施 5 + 导入 1。"""
    types = [
        "RefPlane",
        "RefPlane",
        "RefPlane",
        "OriginProfileFeature",
        "ConfigTableFolder",
        "MBimport",
    ]
    got = T.tally([{"type": t} for t in types])
    assert got["native"] == 0, (
        "★ 导入体不能有原生几何特征（基准面不算）—— 否则「导入死实体冒充原生」会判 pass"
    )
    assert got["import"] == 1
    assert got["infra"] == 5


def test_基准面不算原生几何() -> None:
    """★★ 关键边界：只有基准/容器的零件，原生几何必须是 0。"""
    got = T.tally([{"type": t} for t in ("RefPlane", "OriginProfileFeature")])
    assert got["native"] == 0
    assert got["infra"] == 2


@pytest.mark.parametrize(
    ("name", "kind"),
    [
        ("ProfileFeature", "native"),
        ("Extrusion", "native"),
        ("ICE", "native"),
        #: ★ 第 26 轮实测：异型孔向导的类型名是 HoleWzd
        ("HoleWzd", "native"),
        ("RefPlane", "infra"),
        ("OriginProfileFeature", "infra"),
        ("ConfigTableFolder", "infra"),
        ("MBimport", "import"),
    ],
)
def test_每个实测类型归对类(name: str, kind: str) -> None:
    assert T.classify(name) == kind


@pytest.mark.parametrize(
    "guess",
    ["Cut", "CutExtrude", "Extrude", "Sketch", "Import", "Imported",
     "HoleWizard", "WizardHole", "HoleWizard5"],
)
def test_凭印象的名字不入表(guess: str) -> None:
    """★★ 防后人「顺手」把猜出来的名字加进词表。

    ★ 本机给「切除-拉伸」的是 `ICE`、给导入实体的是 `MBimport`。
      加 `Cut` / `Import` 这类名字会让词表看起来更「可读」，但那不是实测值。
    """
    assert T.classify(guess) == "unknown", (
        "★ %r 是凭印象的名字，词表只收实测值" % guess
    )


def test_未收录类型回unknown并单独列出() -> None:
    """★ 遇到没量过的类型，必须能被看见 —— 漏计可能让伪造手法混过去。"""
    got = T.tally([{"type": "SomethingNew"}, {"type": "SomethingNew"}, {"type": "ICE"}])
    assert got["unknown"] == 2
    assert got["unknown_types"] == ["SomethingNew"]
    assert got["native"] == 1


def test_三组词表互不重叠() -> None:
    """★ 一个类型只能属于一组 —— 重叠会让计数自相矛盾。"""
    a, b, c = T.NATIVE_GEOMETRY_TYPES, T.INFRA_TYPES, T.IMPORT_TYPES
    assert not (a & b), "原生与基础设施重叠：%s" % (a & b)
    assert not (a & c), "原生与导入重叠：%s" % (a & c)
    assert not (b & c), "基础设施与导入重叠：%s" % (b & c)


def test_空输入不炸() -> None:
    got = T.tally([])
    assert got["native"] == 0 and got["unknown_types"] == []
