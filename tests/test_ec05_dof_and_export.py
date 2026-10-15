"""★ EC05 T03/T07 判据 —— 自由度计划 / 配置切换 / 导出比较。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/part_loop.py`（★ `DofPlan` · `config_switch_verdict` · `export_compare_verdict`）
#         `specs/307-ec05-first-part-loop/spec.md`（★ FR-003 · FR-007）
# 定位:   ★ EC05 **T03**（★ 自由度/关系/尺寸图 + **有意保留自由度必须标注**）与
#         **T07**（★ 保存重开/**配置切换**/**导出比较**）。
# 官方依据: 不适用（本仓的工程闭环层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from engineering import part_loop as P


# ══════════════════════════════════════════════════════════════════════
# T03 · 自由度计划
# ══════════════════════════════════════════════════════════════════════

def test_t03_fully_constrained_plan_is_acceptable():
    """★★ T03：★ **全约束 ⇒ 可接受**（★ 自由度 0）。

    ★ 公式：★ `dof = 2×实体 − 关系 − 尺寸` ⇒ ★ 本例 `2×3 − 2 − 4 = 0`。
    """
    plan = P.DofPlan(entities=3, relations=["h", "v"], dimensions=["w", "hgt", "x", "y"])
    out = P.check_dof_plan(plan)
    assert out["total_dof"] == 0, "★ 样本算错了自由度：%d" % out["total_dof"]
    assert out["ok"] is True, "★ 全约束却被判不可接受：%r" % out


def test_t03_intentional_dof_must_be_annotated():
    """★★★★★ T03：★ **有意保留的自由度必须标注**（★ 逐字承 EC05-T03）。

    ★★ 判据：★ 有自由度**但没标注理由** ⇒ ★ **不可接受**（★ 那是「忘了锁」不是「有意保留」）。
    """
    #: ★ `2×3 − 2 − 2 = 2` 个自由度
    plan = P.DofPlan(entities=3, relations=["h", "v"], dimensions=["w", "hgt"])
    assert plan.total_dof() == 2, "★ 这个样本该有 2 个自由度"
    out = P.check_dof_plan(plan)
    assert out["ok"] is False, (
        "★★ 有未标注的自由度却判可接受 ⇒ ★ 「忘了锁」会被当成「有意保留」")
    assert out["unexplained"] == 2
    assert "没标注理由" in out["reason"]


def test_t03_annotated_dof_is_acceptable():
    """★★★★ T03：★ **标注了理由 ⇒ 可接受**（★ **不机械要求全锁死** —— ★ 逐字）。

    ★★★ **这条是本任务的意义**：★ 它**不**要求自由度必须为 0 ——
      ★★ 它要求**每个自由度都有交代** ✓
    """
    plan = P.DofPlan(entities=3, relations=["h", "v"], dimensions=["w", "hgt"])
    assert plan.total_dof() == 2
    plan.add_intentional_dof("旋转", why="★ 装配时需要绕孔轴微调 ⇒ 有意保留")
    plan.add_intentional_dof("平移", why="★ 现场配作 ⇒ 有意保留")
    out = P.check_dof_plan(plan)
    assert out["ok"] is True, (
        "★★ 逐条标注了理由却被判不可接受 ⇒ ★ 那是「机械要求全锁死」：%r" % out)
    assert out["total_dof"] == 2, "★ 自由度应**仍 = 2**（★ 标注 ≠ 锁死）"
    assert out["unexplained"] == 0


def test_t03_partially_annotated_is_still_rejected():
    """★★★★ T03：★ **只标了一半 ⇒ 仍拒**（★ 逐条都要交代）。"""
    plan = P.DofPlan(entities=3, relations=["h", "v"], dimensions=["w", "hgt"])
    plan.add_intentional_dof("旋转", why="★ 有意保留")
    out = P.check_dof_plan(plan)
    assert out["ok"] is False, "★★ 只标了一个却判可接受"
    assert out["unexplained"] == 1


def test_t03_empty_reason_is_rejected():
    """★★ T03：★ **空理由 ⇒ 拒**（★ 「标注」不能是空的）。"""
    plan = P.DofPlan(entities=4, relations=["h"], dimensions=["w"])
    with pytest.raises(ValueError) as exc:
        plan.add_intentional_dof("旋转", why="   ")
    assert "必须给理由" in str(exc.value)


def test_t03_dof_formula_is_stable():
    """★★ T03：★ 自由度公式**可复核**（★ `2×实体 − 关系 − 尺寸`）。"""
    plan = P.DofPlan(entities=3, relations=["a", "b"], dimensions=["c"])
    assert plan.total_dof() == 2 * 3 - 2 - 1, "★ 公式不对：%d" % plan.total_dof()
    #: ★★ 不会算成负数
    over = P.DofPlan(entities=1, relations=["a", "b", "c", "d"], dimensions=["e"])
    assert over.total_dof() == 0, "★ 过约束时不该出负数"


# ══════════════════════════════════════════════════════════════════════
# T07 · 配置切换
# ══════════════════════════════════════════════════════════════════════

def test_t07_config_switch_requires_round_trip():
    """★★★ T07：★ **配置切换要能**切过去再切回来****（★ 判据与 EC00 T026 同口径）。"""
    ok = P.config_switch_verdict("默认", "EC05", "默认", "EC05")
    assert ok["ok"] is True, "★ 正常往返被判失败：%r" % ok
    assert ok["switched_to_target"] is True and ok["switched_back"] is True


def test_t07_config_switch_fails_if_never_switched():
    """★★ T07 **负例**：★ **没真的切过去 ⇒ 失败**（★ 不是「没报错就算过」）。"""
    out = P.config_switch_verdict("默认", "默认", "默认", "EC05")
    assert out["ok"] is False, "★★ 没切过去却判成功"
    assert out["switched_to_target"] is False


def test_t07_config_switch_fails_if_stuck_on_target():
    """★★ T07 **负例**：★ **切不回来 ⇒ 失败**（★ 会「串」）。"""
    out = P.config_switch_verdict("默认", "EC05", "EC05", "EC05")
    assert out["ok"] is False, "★★ 卡在目标配置却判成功 ⇒ ★ 会串"
    assert out["switched_back"] is False


# ══════════════════════════════════════════════════════════════════════
# T07 · 导出比较
# ══════════════════════════════════════════════════════════════════════

def test_t07_export_compare_requires_nonempty_files():
    """★★★ T07：★ **导出判据是文件**（★ 存在且**非零字节** —— ★ 承 EC00 口径）。"""
    out = P.export_compare_verdict({"step": {"exists": True, "bytes": 12345}})
    assert out["ok"] is True, "★ 正常导出被判失败：%r" % out
    #: ★★ **零字节 ⇒ 失败**（★ 那是 EC00 抓到过的假成功）
    bad = P.export_compare_verdict({"step": {"exists": True, "bytes": 0}})
    assert bad["ok"] is False, "★★ 零字节导出被判成功 ⇒ ★ 假成功"
    #: ★ 不存在 ⇒ 失败
    miss = P.export_compare_verdict({"step": {"exists": False, "bytes": 0}})
    assert miss["ok"] is False


def test_t07_export_compare_rejects_empty_input():
    """★★ T07：★ **空输入 ⇒ 不算通过**（★ 不能「没有导出」也算 ok）。"""
    assert P.export_compare_verdict({})["ok"] is False, (
        "★★ 一个导出都没有却判 ok ⇒ ★ 空集不算通过")


def test_t07_export_compare_checks_every_format():
    """★★ T07：★ **每个格式都要查**（★ 不是抽查一个）。"""
    out = P.export_compare_verdict({
        "step": {"exists": True, "bytes": 100},
        "stl": {"exists": True, "bytes": 0},      #: ★ 这个坏
        "pdf": {"exists": True, "bytes": 200},
    })
    assert out["ok"] is False, "★★ 有一个坏却判整体通过"
    assert out["items"]["stl"]["ok"] is False
    assert out["items"]["step"]["ok"] is True
