"""示教器记录器的**离线判据**（不碰 COM）。

真机验收另有报告（18 项全过）；这里钉住渲染层的几条不许骗人的规则：
- 构造线必须在人读版里**标出来**，不能和普通线段混在一起
- 尺寸必须带上**参照实体的类型**（点/线段/边/面），否则读的人看不出量的哪里
- 自定义属性的 `_count` / `_error` 这类**元键**不许混进人读版
- 摘要行只报数量，不下结论
- 记录里没有的信息，渲染时不许凭空补
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "scripts"))

from teach import render_md, summary_line  # noqa: E402


def _part_doc() -> dict:
    return {
        "document": "参考案例.SLDPRT",
        "path": "x",
        "doc_type": "零件",
        "features": [{"name": "草图1", "type": "ProfileFeature"}],
        "sketches": [
            {
                "name": "草图2",
                "owner": "M6 间隙孔1",
                "constrained": 3,
                "constrained_meaning": "完全定义",
                "points": [{"x_mm": 10.0, "y_mm": -10.0}],
                "segments": [
                    {"shape": "直线", "construction": True,
                     "endpoints_mm": [[0.0, 0.0], [0.0, 60.0]]},
                    {"shape": "直线", "construction": False,
                     "endpoints_mm": [[0.0, 0.0], [100.0, 0.0]]},
                ],
                "relations": [
                    {"type": "DISTANCE", "value_mm": 10.0,
                     "entities": [{"kind": "草图点"}, {"kind": "草图线段",
                                                       "construction": False}]},
                ],
            },
        ],
        "bodies": [{"face_count": 10, "cylinder_faces": 4}],
        "custom_properties": {
            "材料": ["Q235B", "30", False],
            "图号": ["DEMO-001", "30", False],
            "_count": 29,
            "_error": None,
        },
    }


def test_render_marks_construction_lines() -> None:
    md = render_md(_part_doc())
    assert "构造线" in md
    assert "构造" in md
    #: 构造与非构造都要各自出现
    assert md.count("构造") >= 2


def test_render_shows_dimension_reference_kinds() -> None:
    md = render_md(_part_doc())
    assert "DISTANCE" in md
    assert "10.0" in md
    #: 参照实体类型必须出现在同一行
    assert "草图点" in md
    assert "草图线段" in md


def test_render_skips_meta_keys() -> None:
    md = render_md(_part_doc())
    assert "材料" in md and "Q235B" in md
    assert "_count" not in md
    assert "_error" not in md


def test_render_marks_sketch_owner() -> None:
    """孔内草图要能看出挂在哪个特征下。"""
    md = render_md(_part_doc())
    assert "M6 间隙孔1" in md


def test_summary_line_counts_only() -> None:
    s = summary_line(_part_doc())
    assert "特征" in s and "草图" in s and "实体" in s
    #: 不下结论
    for word in ("合格", "正确", "问题"):
        assert word not in s


def test_summary_line_assembly() -> None:
    s = summary_line({"doc_type": "装配", "components": [{}, {}], "mates": [{}],
                      "features": [{}]})
    assert "组件 2" in s and "配合 1" in s


def test_render_invents_nothing() -> None:
    """记录里没有的东西，渲染不许编出来。"""
    md = render_md({"document": "空", "doc_type": "零件"})
    assert "空" in md
    assert "草图" not in md
    assert "构造" not in md


def test_mate_and_view_constants_present() -> None:
    """枚举表要包含真机验证过的取值（防止被误删）。"""
    import sw_model_snapshot

    assert sw_model_snapshot.MATE_TYPE[5] == "DISTANCE"       #: 实测距离配合
    assert sw_model_snapshot.MATE_ALIGN[0] == "ALIGNED"
    assert sw_model_snapshot.SEGMENT_KIND[0] == "直线"
    assert sw_model_snapshot.CONSTRAINT[1] == "DISTANCE"
    assert sw_model_snapshot.CONSTRAINT[25] == "HORIZPOINTS"
    assert sw_model_snapshot.DOC_KIND[2] == "装配"
