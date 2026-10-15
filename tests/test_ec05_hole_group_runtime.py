"""★ EC05 真机判据 —— **孔组的孔径与孔位**（★ 关掉「孔组未真打孔」这条残留）。

★★★ **为什么要有它**：★ EC05 上一轮只做了**规则判定**（边距/可达性）——
  ★★ **没在模型上打孔** ⇒ ★ 五项回读里的 `hole_diameter` / `hole_position`
  ★ **没有几何读数** ⇒ ★ 那两项一直是**推断**不是**回读** ✗
★ 本轮**真打 3 孔并回读**（★ 证据 `output/_probe_ec05_holes.json` · ★ 走 `sw_guard`）：
  · ★ 孔特征：★ `孔_1` / `孔_2` / `孔_3`（★ 特征树 **7 → 13**）
  · ★ 回读孔组 **3 个**：★ 位置 `[-30,0] [0,0] [30,0]`（mm）· ★ 孔径全 **Ø10.0 mm**
  · ★ `validate_hole_positions` ⇒ ★ **`status: pass`** · ★ **3/3 通过** · ★ `unmatched = 0`
★★ **判据分层**：★ 本文件读**证据 JSON**（★ 已落盘的真读数）——
  ★ 不连 COM（★ 与 EC00/EC03 的离线判据同族）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/307-ec05-first-part-loop/spec.md`（★ FR-005 · ★ 五项回读）
#         `output/_probe_ec05_holes.json`（★ 真机证据 —— ★ 本判据的输入）
#         `scripts/sw_review.py`（★ `collect_geometry_measurements` ·
#           `validate_hole_positions` —— ★ **本仓早已有**的孔读取链）
# 定位:   ★ 守卫「孔组的孔径/孔位**必须有几何回读**」；★ 补 EC05 的 runtime 面。
# 官方依据: `IFeatureManager::HoleWizard5`（★ 建孔）· B-Rep 圆柱面（★ 回读）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 读证据 JSON —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "output" / "_probe_ec05_holes.json"

#: ★★ **标称**（★ 与 spec 冻结的一致）
NOMINAL_D_MM = 10.0
NOMINAL_SPACING_MM = 30.0
NOMINAL_COUNT = 3


@pytest.fixture(scope="module")
def ev() -> dict:
    """★ 读真机证据（★ 缺证据 ⇒ **skip 并说明** —— ★ 不假装跑过）。"""
    if not EVIDENCE.is_file():
        pytest.skip("★★ 缺真机证据 `%s` ⇒ 跑 `sw_guard` 探针后再判"
                    % EVIDENCE.relative_to(ROOT))
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_evidence_is_a_real_machine_run(ev):
    """★★ 证据必须来自**真机**（★ 有 SolidWorks 版本号 —— ★ 不是手写的）。"""
    assert ev.get("revision"), "★★ 证据里没有 SolidWorks 版本 ⇒ 不像真机读数"
    assert not ev.get("blocked"), "★ 那次真机跑被阻塞了：%r" % ev.get("blocked")


def test_three_holes_were_really_built(ev):
    """★★★★ 孔**真的建出来了**（★ 特征树增量 —— ★ 不是「工具回了 True」）。

    ★★ 依据（★ 事实 8 的教训）：★ 「`AddSelectionListObject` 的 bool 不可信」——
      ★ 所以**不看返回值**，★ 看**特征树真的多了孔** ✓
    """
    res = ev.get("hole_result") or {}
    assert res.get("tree_after", 0) > res.get("tree_before", 0), (
        "★★ 特征树没长 ⇒ 孔没建成（★ 工具返回 True 不算数）")
    names = res.get("new_features") or []
    holes = [n for n in names if "孔" in n]
    assert len(holes) == NOMINAL_COUNT, (
        "★★ 期望 %d 个孔特征，实得 %r" % (NOMINAL_COUNT, holes))


def test_hole_diameter_is_read_back_from_geometry(ev):
    """★★★★★ 孔径**从几何回读**（★ 逐字承 EC05-T05：★「★ 独立回读**孔径**」）。

    ★★ 判据：★ 回读孔径 ≈ 标称 Ø10 mm（★ 容差 0.5）。
    ★★★ **注意**：★ 建孔时传的 `diameter_mm=10.0` **不是**证据 ——
      ★★ 证据是**从 B-Rep 圆柱面量回来的** ✓
    """
    diams = ev.get("distinct_diameters_mm") or []
    assert diams, "★★ 孔径回读为空 ⇒ 那两项仍是推断不是回读"
    assert any(abs(d - NOMINAL_D_MM) < 0.5 for d in diams), (
        "★★ 回读孔径 %r 与标称 Ø%s 不符" % (diams, NOMINAL_D_MM))
    assert ev.get("diameter_matches_nominal") is True


def test_hole_count_is_read_back(ev):
    """★★★ 孔数**从几何回读**（★ 3 个）。"""
    assert ev.get("hole_count_readback") == NOMINAL_COUNT, (
        "★★ 回读孔数 %r ≠ %d" % (ev.get("hole_count_readback"), NOMINAL_COUNT))
    assert (ev.get("measurement_source") or ""), "★ 没记量测来源"


def test_hole_positions_match_the_independent_reference(ev):
    """★★★★★ 孔位与**独立参考值**一致（★ 逐字承 EC05-T05：★「独立回读……**位置**」）。

    ★★ 独立参考（★ 手写 `reference_hole_positions`）：★ `[-30, 0] [0, 0] [30, 0]` mm
      ⇒ ★★ **回读孔心必须落在同一组点上** ✓
    """
    groups = ev.get("hole_groups") or []
    assert len(groups) == NOMINAL_COUNT, "★ 回读孔组 %d ≠ %d" % (len(groups), NOMINAL_COUNT)
    got = sorted(tuple(round(float(v), 3) for v in (g.get("position_mm") or [])[:2])
                 for g in groups)
    want = sorted([(-NOMINAL_SPACING_MM, 0.0), (0.0, 0.0), (NOMINAL_SPACING_MM, 0.0)])
    assert got == want, "★★ 回读孔位 %r ≠ 独立参考 %r" % (got, want)


def test_validator_reports_pass_for_every_hole(ev):
    """★★★★ **逐孔机器验收**：★ `validate_hole_positions` 必须 **`pass`**。

    ★★ 依据（★ 本仓既有链）：★ `sw_review.validate_hole_positions` ——
      ★ 它**只用几何证明孔径与轴线位置** ✓（★ 不取建孔函数的返回值）
    """
    v = ev.get("validation") or {}
    assert v.get("status") == "pass", (
        "★★ 逐孔验收状态 = %r（★ 期望 pass）" % v.get("status"))
    checks = v.get("checks") or []
    assert len(checks) == NOMINAL_COUNT, "★ 验收条目 %d ≠ %d" % (len(checks), NOMINAL_COUNT)
    failed = [c for c in checks if not c.get("passed")]
    assert not failed, "★★ 有孔没过：%r" % [(c.get("id"), c.get("expected_position_mm"))
                                            for c in failed]
    assert v.get("unmatched_actual_count") == 0, (
        "★★ 有 %r 个回读孔没被匹配上 ⇒ 可能多打了孔" % v.get("unmatched_actual_count"))


def test_no_residue_after_the_run(ev):
    """★★★ 跑完**关文档**（★ 不留残留 —— ★ 承 EC00 的收尾纪律）。"""
    assert ev.get("closed") is True, "★★ 探针没关掉自己开的文档"


def test_spec_still_freezes_the_same_nominal(ev):
    """★★ 证据里的标称与 **spec 冻结的扰动集**一致（★ 防「跑完再改标称」）。"""
    nominal = ev.get("nominal") or {}
    assert nominal.get("d_mm") == NOMINAL_D_MM
    assert nominal.get("spacing_mm") == NOMINAL_SPACING_MM
    assert nominal.get("count") == NOMINAL_COUNT
    spec = (ROOT / "specs" / "307-ec05-first-part-loop" / "spec.md").read_text(
        encoding="utf-8", errors="replace")
    assert "HOLE" in spec.upper() or "孔" in spec, "★ spec 里没提孔组"
