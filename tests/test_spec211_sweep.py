"""★ 规格 211 · B2-2「扫描曲面（路 B）」的契约与负例（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`scripts/sw_surface_features.py` 的 `sweep_surface_report`）
# 文件:   tests/test_spec211_sweep.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B2-2**。★ 官方页三样已读
#   （★ `C:\swapi\types\IFeatureManager\InsertSweepSurface2.md`）✓
#   ★★★ **本条的定性（★ 关键，★ 不许说成"试死"）**：
#     ★ **只到「查了行为」** —— ★ 真机读数是在**"没选轮廓/路径"**下取的
#     （`selection_count_before = 0`）⇒ ★ **静默回 `None` 很可能只是因为"前置没上"** ✗
#     ★★ **必须与事实 392 分开**：★ 392 的静默是「**前置全对上仍静默**」⇒ **那才是试死** ✓
# 判据:   ★★ **三条契约**（★ 全部确定性、★ 不猜语义 ✓）：
#     ★ ① `SWEEP_MARKS` 必须与官方 `## Remarks` 的 mark 表**逐字一致**（1 / 2 / 4）✓
#     ★ ② **官方那两条前提必须写进返回值**（`official_marks` · `selection_contract`）✓
#     ★ ③ **必须声明"走路 B、不走路 A"**（`route`）——
#       ★★ 因为路 A 已按**事实 392** 试死，★ 不声明会被后人误当同一条路 ✓
#   ★ 另一条：★ **`side_effects` 非空**（★ 会新建曲面体、非只读 ✓）
# 官方依据: 见上
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_surface_features as SF                               # noqa: E402


def test_sweep_marks_match_official_remarks():
    """★ 官方 `## Remarks` 逐字：1 = Profile · 2 = Guide curve · 4 = Sweep path ✓"""
    assert SF.SWEEP_MARKS == {"profile": 1, "guide": 2, "path": 4}


def test_route_is_declared_as_B_and_says_A_is_dead():
    """★★ **必须声明"走路 B"** —— ★ 路 A 已按事实 392 试死，★ 不声明会被误当同一条路 ✓"""
    r = SF.sweep_surface_report(None)
    route = str(r.get("route", ""))
    assert "B" in route and ("CreateDefinition" in route or "路 A" in route), route[:120]


def test_official_selection_contract_is_returned():
    r = SF.sweep_surface_report(None)
    assert r.get("official_marks") == {"profile": 1, "guide": 2, "path": 4}
    sc = str(r.get("selection_contract", ""))
    assert "SelectByID2" in sc and "Profile" in sc and "Sweep path" in sc, sc[:150]


def test_use_auto_select_note_keeps_official_wording():
    """★ 官方逐字：`UseAutoSelect = false` 时「the user **must select the bodies**」✓"""
    r = SF.sweep_surface_report(None)
    assert "must select the bodies" in str(r.get("use_auto_select_note", ""))


def test_none_model_is_refused():
    """★ **负例**：`model=None` ⇒ ★ 必须 `ok=False` + 有原因（★ 不抛 ✓）"""
    r = SF.sweep_surface_report(None)
    assert r["ok"] is False and r["error"]


def test_side_effects_declared():
    r = SF.sweep_surface_report(None)
    assert r.get("side_effects"), "★ 会新建曲面体的能力必须声明副作用（★ 不许被当只读）"


def test_path_align_and_twist_notes_are_present():
    """★ 官方两条"只在某模式下有意义"的说明必须在（★ 免得调用方误用）✓"""
    r = SF.sweep_surface_report(None)
    assert "FollowPath" in str(r.get("path_align_note", ""))
    assert "ConstantTwistAlongPath" in str(r.get("twist_angle_note", ""))
