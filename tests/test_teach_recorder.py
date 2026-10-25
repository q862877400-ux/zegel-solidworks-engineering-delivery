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
    #: 枚举**保留官方成员名**（LINE/ARC…），中文在 SEGMENT_KIND_ZH —— 两者都要在
    assert sw_model_snapshot.SEGMENT_KIND[0] == "LINE"
    assert sw_model_snapshot.SEGMENT_KIND_ZH[0] == "直线"
    assert sw_model_snapshot.CONSTRAINT[1] == "DISTANCE"
    assert sw_model_snapshot.CONSTRAINT[25] == "HORIZPOINTS"
    assert sw_model_snapshot.DOC_KIND[2] == "装配"


def test_render_external_references() -> None:
    """外部引用必须在人读版里写清「哪个特征 → 引用哪个实体的哪个对象」。"""
    doc = _part_doc()
    doc["external_references"] = [
        {"feature": "凸台-拉伸1", "model_path": "D:/a.SLDPRT",
         "component_path": "D:/b.SLDPRT", "data_type": "EDGE", "status": "5",
         "ref_entity": "边(0,0,0)-(1,0,0)", "ref_component": "零件B-1"},
        {"error": "ListExternalFileReferences2 调用失败"},
    ]
    md = render_md(doc)
    assert "外部引用" in md
    assert "凸台-拉伸1" in md
    assert "边(0,0,0)-(1,0,0)" in md
    assert "零件B-1" in md
    #: 失败也要如实写出来，不许静默
    assert "读取失败" in md


def test_render_no_external_section_when_empty() -> None:
    md = render_md(_part_doc())
    assert "外部引用" not in md


def test_useedge_marks_external_sketch_reference() -> None:
    """★ 草图级外部引用：关系类型 32 = USEEDGE，必须在枚举表里且被人读版标出。"""
    import sw_model_snapshot

    assert sw_model_snapshot.CONSTRAINT[32] == "USEEDGE"
    doc = _part_doc()
    doc["sketches"][0]["use_edge_count"] = 1
    doc["sketches"][0]["use_edge_entities"] = [["草图线段", "草图线段"]]
    md = render_md(doc)
    assert "USEEDGE" in md
    assert "外部" in md


def test_angle_value_not_misread_as_length() -> None:
    """★★ 实测 bug：角度尺寸 GetSystemValue2 回的是**弧度**，
    按长度 ×1000 会记成 "785.398 mm"（假数值）⇒ 必须分开记 value_deg。"""
    import sw_model_snapshot

    assert 2 in sw_model_snapshot.ANGLE_TYPES
    doc = _part_doc()
    doc["sketches"][0]["relations"] = [
        {"type": "DISTANCE", "type_int": 1, "value_mm": 100.0,
         "entities": [{"kind": "草图点"}, {"kind": "草图点"}]},
        {"type": "ANGLE", "type_int": 2, "value_rad": 0.785398,
         "value_deg": 45.0,
         "entities": [{"kind": "草图线段"}, {"kind": "草图线段"}]},
    ]
    md = render_md(doc)
    assert "100.0 mm" in md
    assert "45.0°" in md
    #: 角度不许以 mm 出现
    assert "0.785398" not in md
    assert "785" not in md


def test_duplicate_sketch_merged() -> None:
    """★ 同一张草图既是顶层特征又是某特征子特征 ⇒ 合并，不许记成两张。"""
    import sw_model_snapshot

    acc: list = []
    sk1 = {"name": "草图1", "constrained": 3, "owner": None,
           "points": [], "segments": [], "relations": []}
    acc.append(sk1)
    sw_model_snapshot._merge_sketch_duplicate(acc, sk1)
    sk2 = {"name": "草图1", "constrained": 3, "owner": "凸台-拉伸1",
           "points": [], "segments": [], "relations": []}
    acc.append(sk2)
    sw_model_snapshot._merge_sketch_duplicate(acc, sk2)
    assert len(acc) == 1
    assert acc[0].get("also_owned_by") == ["凸台-拉伸1"]


def test_enums_not_handwritten() -> None:
    """★ 根因 A：枚举必须来自生成表，且关键值正确（手抄曾把 7/8 抄错）。"""
    import sw_enums

    assert sw_enums.CONSTRAINT_TYPE[7] == "swConstraintType_PARALLEL"
    assert sw_enums.CONSTRAINT_TYPE[8] == "swConstraintType_PERPENDICULAR"
    assert sw_enums.CONSTRAINT_TYPE[6] == "swConstraintType_TANGENT"
    assert sw_enums.CONSTRAINT_TYPE[32] == "swConstraintType_USEEDGE"
    #: 生成表规模（官方文件有 80+ 项；手抄版只有 30 出头）
    assert len(sw_enums.CONSTRAINT_TYPE) >= 60


def test_dimension_units_dispatch() -> None:
    """★ 根因 B：长度回 mm、角度回 rad+deg、未知量纲标 unit_unverified。"""

    class _D:
        def __init__(self, v):
            self.v = v

        #: N802：替身方法用小写名；被测代码按原属性名调用，故同时挂一个别名
        def get_system_value2(self, _cfg):
            return self.v

        GetSystemValue2 = get_system_value2

    import sw_units

    length = sw_units.dimension_reading(_D(0.1), 1)
    assert length["value_mm"] == 100.0
    ang = sw_units.dimension_reading(_D(0.7853981634), 2)
    assert abs(ang["value_deg"] - 45.0) < 1e-6
    assert "value_mm" not in ang          #: 角度**不许**以 mm 出现
    other = sw_units.dimension_reading(_D(3.5), 43)
    assert other.get("unit_unverified") is True
    assert "value_mm" not in other


def test_sketch_point_does_not_conflate_user_and_all() -> None:
    """★ 根因 F：用户点与全部点必须分开记（曾是 6 个点里混 5 个线段端点）。"""
    doc = _part_doc()
    sk = doc["sketches"][0]
    sk["all_point_count"] = 6
    sk["user_points"] = [{"x_mm": 0.0, "y_mm": 0.0}]
    sk["user_point_count"] = 1
    md = render_md(doc)
    assert "1" in md


def test_feature_params_no_annotation_in_data() -> None:
    """★ 根因 G：口径说明不许混进数据；长度值必须带 _mm 后缀。"""
    import sw_model_snapshot

    out = sw_model_snapshot._param_with_unit("GetDepth", 0.025)
    assert out == {"depth_mm": 25.0}
    #: 嵌套 dict 要递归（forward/reverse 就是嵌套的）
    nested = sw_model_snapshot._param_with_unit("forward", {"GetDepth": 0.025, "GetEndCondition": 0})
    assert nested["forward"]["depth_mm"] == 25.0
    assert "GetDepth" not in nested["forward"]


def _fake_summary(title: str, path: str, states: list) -> dict:
    return {
        "title": title, "path": path, "doc_type": 1,
        "features": 5, "sketches": 1, "sketch_states": states,
        "relations": 3, "dimensions": 1, "holes": 0, "mates": 0,
    }


def test_timeline_first_poll_records(tmp_path) -> None:
    """★ 首次采样**必须**记一条。

    2026-10-26 质检抓到我自己引入的回归：修 doc-switch 时把首次的 `last`
    也设成了当前摘要 ⇒ `changed_fields(摘要, 摘要)` 为空 ⇒ **一条都不记**。
    """
    import sw_model_timeline as T

    real = T.loudness
    T.loudness = lambda _d: _fake_summary("A", "/a", [2])
    try:
        tl = T.Timeline(tmp_path, 0.0)
        rec = tl.poll(object())
    finally:
        T.loudness = real
    assert rec is not None, "首次必须记一条"
    assert "features" in (rec.get("changed") or {})


def test_timeline_doc_switch_records_once(tmp_path) -> None:
    """★ 切换文档只记**一条** `doc-switch`。

    曾产生 2 条（切换 + 首次），下游会误以为发生了两次变化。
    """
    import sw_model_timeline as T

    real = T.loudness
    tl = T.Timeline(tmp_path, 0.0)
    try:
        T.loudness = lambda _d: _fake_summary("A", "/a", [2])
        r1 = tl.poll(object())          #: 首次
        r2 = tl.poll(object())          #: 同文档重复
        T.loudness = lambda _d: _fake_summary("B", "/b", [3])
        r3 = tl.poll(object())          #: 切文档
        r4 = tl.poll(object())          #: 切后重复
    finally:
        T.loudness = real
    assert r1 is not None, "首次要记"
    assert r2 is None, "同文档重复不记"
    assert r3 is not None and r3.get("kind") == "doc-switch", "切换要记 doc-switch"
    assert r4 is None, "切后同文档重复不记"
    lines = [x for x in (tmp_path / "timeline.jsonl").read_text(
        encoding="utf-8").splitlines() if x.strip()]
    assert len(lines) == 2, f"应共 2 条，实际 {len(lines)}"


def test_timeline_snapshot_on_sketch_state_change(tmp_path) -> None:
    """★ 草图状态变化（欠定义→完全定义）**必须**留完整快照。"""
    import sw_model_timeline as T

    real = T.loudness
    tl = T.Timeline(tmp_path, 0.0)
    try:
        T.loudness = lambda _d: _fake_summary("A", "/a", [2])
        tl.poll(object())
        T.loudness = lambda _d: _fake_summary("A", "/a", [3])
        r = tl.poll(object())
    finally:
        T.loudness = real
    assert r is not None
    assert "sketch_states" in (r.get("changed") or {})
    assert r.get("snapshot"), "状态变化必须留快照（业主最关心的中间态）"


def test_no_escape_residue_in_teach_sources() -> None:
    """★ 源码不许有「行内 TAB」——那是写入转义残留的指纹。

    实测踩过：`\\timeline.jsonl` 被写成 TAB+`imeline.jsonl`，
    其中一处还在**字符串里**，会直接把乱码输出到报告。
    """
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    files = [
        root / "scripts" / "sw_model_timeline.py",
        root / "scripts" / "sw_dialog_text.py",
        root / "scripts" / "sw_model_snapshot.py",
        root / "scripts" / "sw_units.py",
        root / "tools" / "demo_capture.py",
        root / "tools" / "extract_psr_shots.py",
        root / "tools" / "gen_sw_enums.py",
        root / "tools" / "teach.py",
    ]
    bad = []
    for f in files:
        if not f.is_file():
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if "\t" in line.lstrip("\t"):
                bad.append(f"{f.name}:{i}")
    assert not bad, "发现行内 TAB（写入转义残留）：" + ", ".join(bad)
