"""示教器 L2/L4 的离线判据：配方提炼、校验、个人化档案注入。

不碰 COM（L3 需要真机，另有真机报告）；这里钉住「数据层不许骗人」：
- 从业主示范的语义快照**真能**提炼出配方，且孔位数/关系数与快照一致
- assertion 键写错 ⇒ **报错**（否则等于没验）
- 未知档案键 ⇒ **报错**（否则用户以为设了、其实没生效）
- 档案只填空字段，**不覆盖**配方已写的值
- profile id 防路径穿越
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import sw_habits  # noqa: E402
import sw_recipe  # noqa: E402

CAPTURE = REPO / "output" / "coop" / "参考案例.SLDPRT"


def _snapshot() -> dict:
    """业主示范的语义快照（真机读出的结构；字段与 sw_model_snapshot 一致）。"""
    return {
        "document": "参考案例.SLDPRT",
        "path": str(CAPTURE),
        "features": [
            {"name": "草图1", "type": "ProfileFeature"},
            {"name": "凸台-拉伸1", "type": "Extrusion"},
            {"name": "M6 间隙孔1", "type": "HoleWzd"},
        ],
        "sketches": [
            {"name": "草图1", "constrained": 3,
             "points": [[0.0, 0.0], [100.0, -60.0], [0.0, -60.0], [100.0, 0.0]],
             "relations": [{"type": "FIXED", "refs": ["点(0,0)"]}]},
        ],
        "holes": [
            {"name": "M6 间隙孔1", "standard": "GB", "fastener": "螺钉间隙",
             "size": "M6", "sketches": [
                 {"name": "草图2", "constrained": 3,
                  "points": [[10.0, -10.0], [90.0, -10.0],
                             [90.0, -50.0], [10.0, -50.0]],
                  "relations": [
                      {"type": "HORIZPOINTS", "refs": ["点(90,-10)", "点(10,-10)"]},
                      {"type": "VERPOINTS", "refs": ["点(90,-10)", "点(90,-50)"]},
                      {"type": "HORIZPOINTS", "refs": ["点(90,-50)", "点(10,-50)"]},
                      {"type": "VERPOINTS", "refs": ["点(10,-50)", "点(10,-10)"]},
                      {"type": "DISTANCE", "value_mm": 10.0,
                       "refs": ["点(10,-10)", "线[(0,0)→(0,-60)]"]},
                      {"type": "DISTANCE", "value_mm": 10.0,
                       "refs": ["点(10,-10)", "线[(100,0)→(0,0)]"]},
                  ]},
                 {"name": "草图3", "constrained": 3, "points": [], "relations": []},
             ]},
        ],
    }


def test_derive_extracts_plate_and_holes() -> None:
    r = sw_recipe.derive_from_snapshot(_snapshot(), capture="output/teach/x")
    assert r["inputs"]["plate"]["width_mm"] == 100.0
    assert r["inputs"]["plate"]["height_mm"] == 60.0
    assert len(r["inputs"]["positions_mm"]) == 4
    assert r["inputs"]["hole"]["standard"] == "GB"
    assert r["inputs"]["hole"]["size"] == "M6"
    assert r["assertions"]["feature_count_hole"] == 1
    assert r["assertions"]["cylinder_count"] == 4
    #: 关系要提炼出来（不含尺寸）
    assert set(r["hints"]["relations"]) == {"HORIZPOINTS", "VERPOINTS"}


def test_derive_output_passes_validation() -> None:
    r = sw_recipe.derive_from_snapshot(_snapshot())
    assert sw_recipe.validate(r) == []


def test_derive_is_honest_about_missing_thickness() -> None:
    """拉伸深度读不到时**不猜**：留空并写 notes。"""
    r = sw_recipe.derive_from_snapshot(_snapshot())
    assert r["inputs"]["plate"]["thickness_mm"] is None
    assert any("拉伸深度" in n for n in r["notes"])


def test_derive_normalises_hole_positions_to_plate_corner() -> None:
    """★ 示范件孔位是负 Y，执行时板从 (0,0) 建 ⇒ 必须归一化，否则射线打空。"""
    r = sw_recipe.derive_from_snapshot(_snapshot())
    pos = r["inputs"]["positions_mm"]
    assert all(x >= 0 and y >= 0 for x, y in pos), pos
    assert sorted(tuple(p) for p in pos) == [(10.0, 10.0), (10.0, 50.0),
                                            (90.0, 10.0), (90.0, 50.0)]


def test_derive_thickness_from_bbox_is_metres() -> None:
    """★ bbox 的 raw 是**米**（真机实测 0.02 = 20mm）⇒ 板厚必须换算成毫米。"""
    snap = _snapshot()
    snap["bbox_mm"] = [0.0, -0.06, 0.0, 0.1, 0.0, 0.02]
    r = sw_recipe.derive_from_snapshot(snap)
    assert r["inputs"]["plate"]["thickness_mm"] == 20.0
    assert r["notes"] == []


def test_unknown_assertion_key_is_rejected() -> None:
    """写错 assertion 键 ⇒ 必须报错（否则等于没验）。"""
    r = sw_recipe.derive_from_snapshot(_snapshot())
    r["assertions"]["hole_sketch_fully_defined"] = True
    problems = sw_recipe.validate(r)
    assert problems and "未知键" in problems[0]


def test_missing_required_field_is_rejected() -> None:
    assert sw_recipe.validate({"title": "x", "assertions": {"cylinder_count": 4}})


def test_roundtrip_yaml() -> None:
    r = sw_recipe.derive_from_snapshot(_snapshot())
    text = sw_recipe.dump(r)
    back = sw_recipe._mini_yaml_load(text)
    assert back["id"] == r["id"]
    assert back["inputs"]["positions_mm"] == r["inputs"]["positions_mm"]
    assert back["assertions"]["cylinder_count"] == 4


def test_save_and_load(tmp_path) -> None:
    r = sw_recipe.derive_from_snapshot(_snapshot())
    p = sw_recipe.save(r, tmp_path / "recipe.yaml")
    assert p.is_file()
    back = sw_recipe.load(p)
    assert back["assertions"]["hole_standard"] == "GB"


def test_load_rejects_bad_recipe(tmp_path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("id: x\ntitle: y\nassertions:\n  nonsense: 1\n", encoding="utf-8")
    with pytest.raises(sw_recipe.RecipeError):
        sw_recipe.load(p)


def test_profile_defaults_when_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SW_PROFILES_DIR", str(tmp_path))
    eff = sw_habits.load("owner")
    assert eff["hole_standard"] == "GB"
    #: ★ 本机实测：AddDimension 对成对实体返回 None ⇒ 默认走 fixed_points
    assert eff["dimension_style"] == "fixed_points"


def test_profile_save_load_and_unknown_key(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SW_PROFILES_DIR", str(tmp_path))
    sw_habits.save("owner", {"hole_standard": "ISO", "hole_size": "M8"})
    eff = sw_habits.load("owner")
    assert eff["hole_standard"] == "ISO"
    assert eff["hole_size"] == "M8"
    #: 未覆盖的键仍是默认
    assert eff["hole_fastener"] == "螺钉间隙"
    with pytest.raises(sw_habits.HabitsError):
        sw_habits.save("owner", {"hole_standrd": "ISO"})


def test_profile_id_rejects_traversal(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SW_PROFILES_DIR", str(tmp_path))
    for bad in ("../evil", "a/b", "", "Owner"):
        with pytest.raises(sw_habits.HabitsError):
            sw_habits.habits_path(bad)


def test_apply_to_recipe_does_not_override() -> None:
    """档案只填空字段 ⇒ 配方里明确写了的**不许**被档案改掉。"""
    recipe = {"inputs": {"hole": {"standard": "ISO", "size": ""}},
              "hints": {"dimension_style": "to_edge"}}
    habits = dict(sw_habits.DEFAULT_HABITS)
    habits["hole_standard"] = "GB"
    habits["hole_size"] = "M6"
    out = sw_habits.apply_to_recipe(recipe, habits)
    assert out["inputs"]["hole"]["standard"] == "ISO"   #: 配方优先
    assert out["inputs"]["hole"]["size"] == "M6"        #: 空字段被填
    assert out["hints"]["dimension_style"] == "to_edge"


def test_apply_to_recipe_fills_dimension_style() -> None:
    recipe = {"inputs": {"hole": {}}, "hints": {}}
    habits = dict(sw_habits.DEFAULT_HABITS)
    habits["dimension_style"] = "points_plus_fixed"
    out = sw_habits.apply_to_recipe(recipe, habits)
    assert out["hints"]["dimension_style"] == "points_plus_fixed"


def test_type_mismatch_is_rejected() -> None:
    problems = sw_habits.validate({"prefer_pattern_over_points": "yes"})
    assert problems and "bool" in problems[0]
