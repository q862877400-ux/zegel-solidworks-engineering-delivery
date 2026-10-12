"""★ 阶段 2 契约测试：真机变更传播（规格 317 的 D5 真机链）。

★★ 含**假通过堵漏**的回归：变更名**没落在任何步骤上**时，
   `propagation_report` **不得**回 `ok=True`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage2_change_run.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D5 真机链契约测试
# 官方依据: ① 真机实测（2026-10-12）`tools/run_stage2_plate.py --change 1`：
#              板宽 100→120 ⇒ bbox=[120,60,20] · 孔 4/4 · 三类产物 sha256 全变
#           ② 本仓**事实 51**（判据要贴合代码的组织单元）
#              —— 实测踩过：变更名用 `w` 而步骤里是 `x2_mm` ⇒ 影响面 0 ⇒ **假通过**
#           ③ 本仓**事实 561**（护栏沙盒会复制输入 ⇒ 工具内部 OpenDoc6 会失败）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import change_run as CR                        # noqa: E402
from scripts.engineering import drawing_obligations as DO               # noqa: E402
from scripts.engineering import registry as R                           # noqa: E402


#: ══ 变更清单 ═════════════════════════════════════════════════════════

def test_change_plan_lists_only_real_changes() -> None:
    """★ 只列**真的变了**的（★ 没变的不算 —— 否则传播报告假阳性）。"""
    rows = CR.change_plan({"a": 1, "b": 2}, {"a": 1, "b": 3})
    assert len(rows) == 1 and rows[0].name == "b"
    assert rows[0].old == 2 and rows[0].new == 3


def test_change_plan_handles_added_and_removed() -> None:
    """★ 新增/删除键也算变更。"""
    rows = CR.change_plan({"a": 1}, {"b": 2})
    assert {r.name for r in rows} == {"a", "b"}


def test_change_plan_empty_when_identical() -> None:
    """★ 完全一样 ⇒ 空清单。"""
    assert CR.change_plan({"a": 1}, {"a": 1}) == []


#: ══ ★★ 假通过堵漏（★ 真机抓到的）═══════════════════════════════════

def test_propagation_report_flags_unmatched_change_name() -> None:
    """★★ 变更名**没落在任何步骤上** ⇒ **不得**回 `ok=True`。

    ★ 实测（2026-10-12）：用例的参数叫 `w`，而步骤里承载它的是 `x2_mm`
      ⇒ 影响面 0 ⇒ **原实现回 `ok=True`** ⇒ **假通过**。
    ★★ 这条测试就是那个缺陷的回归。
    """
    steps = (R.PlanStep(step="sketch_add_rectangle",
                        params={"x1_mm": 0.0, "y1_mm": 0.0,
                                "x2_mm": 100.0, "y2_mm": 60.0}),)
    #: ★ `w` 不在步骤里 ⇒ unmatched
    bad = DO.propagation_report(steps, [DO.ChangeRecord("w", 100, 120,
                                                        propagated=True)])
    assert bad["ok"] is False, "★★ 假通过：变更名没落在任何步骤上却报 ok"
    assert bad["unmatched"] == ["w"]
    #: ★ 换成步骤里真的有的名字 ⇒ 通过
    good = DO.propagation_report(steps, [DO.ChangeRecord("x2_mm", 100, 120,
                                                         propagated=True)])
    assert good["ok"] is True
    assert good["unmatched"] == []


def test_propagation_report_flags_unpropagated() -> None:
    """★ 有受影响步骤却没传播 ⇒ 不算通过。"""
    steps = (R.PlanStep(step="extrude_boss", params={"depth_mm": 10.0}),)
    bad = DO.propagation_report(steps, [DO.ChangeRecord("depth_mm", 10, 20,
                                                        propagated=False)])
    assert bad["ok"] is False and bad["unpropagated"] == ["depth_mm"]


#: ══ 三类产物的传播判据 ═══════════════════════════════════════════════

def _d(kind: str, sha: str, rev: str = "rev-2") -> DO.ArtifactDigest:
    return DO.ArtifactDigest("%s.bin" % kind, sha, kind, rev)


def test_verify_propagation_all_three_must_pass() -> None:
    """★ 三条都要过：产物都变 + 版本一致 + 有受影响就传播。"""
    steps = (R.PlanStep(step="sketch_add_rectangle",
                        params={"x2_mm": 100.0}),)
    before = [_d("model", "a1"), _d("drawing", "b1"), _d("report", "c1", "rev-1")]
    after = [_d("model", "a2"), _d("drawing", "b2"), _d("report", "c2")]
    changes = [DO.ChangeRecord("x2_mm", 100, 120, propagated=True)]
    v = CR.verify_propagation(before, after, changes, steps)
    assert v["ok"] is True, v


def test_verify_propagation_catches_stale_drawing() -> None:
    """★★ N2：图纸**保留旧版本** ⇒ `verify_propagation` 必须回 False。"""
    steps = (R.PlanStep(step="sketch_add_rectangle",
                        params={"x2_mm": 100.0}),)
    before = [_d("model", "a1"), _d("drawing", "b1"), _d("report", "c1", "rev-1")]
    #: ★ 图纸 sha 与 before **相同** ⇒ 旧版本混入
    after = [_d("model", "a2"), _d("drawing", "b1"), _d("report", "c2")]
    changes = [DO.ChangeRecord("x2_mm", 100, 120, propagated=True)]
    v = CR.verify_propagation(before, after, changes, steps)
    assert v["ok"] is False
    assert v["changed"]["stale"] == ["drawing"]


def test_verify_propagation_catches_missing_artifact() -> None:
    """★ 有一类产物**空摘要**（文件不存在）⇒ 不算通过。"""
    steps = (R.PlanStep(step="sketch_add_rectangle",
                        params={"x2_mm": 100.0}),)
    before = [_d("model", "a1"), _d("drawing", "b1"), _d("report", "c1", "rev-1")]
    after = [_d("model", "a2"), _d("drawing", ""), _d("report", "c2")]
    v = CR.verify_propagation(before, after, steps=steps,
                              changes=[DO.ChangeRecord("x2_mm", 100, 120,
                                                       propagated=True)])
    assert v["ok"] is False


#: ══ digest_set ═══════════════════════════════════════════════════════

def test_digest_set_three_kinds(tmp_path: pathlib.Path) -> None:
    """★ 三类产物摘要（model / drawing / report）。"""
    m = tmp_path / "a.sldprt"; m.write_text("m", encoding="utf-8")
    d = tmp_path / "a.slddrw"; d.write_text("d", encoding="utf-8")
    r = tmp_path / "a.json"; r.write_text("r", encoding="utf-8")
    ds = CR.digest_set(m, d, r, revision="rev-9")
    assert {x.kind for x in ds} == {"model", "drawing", "report"}
    assert all(x.sha256 for x in ds)
    assert {x.revision for x in ds} == {"rev-9"}


def test_digest_set_missing_file_gives_empty_sha(tmp_path: pathlib.Path) -> None:
    """★ 文件不存在 ⇒ **空 sha256**（★ 不是伪造一个）。"""
    ds = CR.digest_set(tmp_path / "no.sldprt", tmp_path / "no.slddrw",
                       tmp_path / "no.json", revision="rev-1")
    assert all(x.sha256 == "" for x in ds)


#: ══ ★ 事实 561 的回归：沙盒会复制输入 ══════════════════════════════

def test_fact561_sandbox_copies_input() -> None:
    """★★ 事实 561 的**可核验痕迹**：沙盒会**复制沙盒外的输入**再用副本。

    ★ 真源是 `scripts/sw_sandbox.py` 的 `resolve_input`（★ 不是 `sw_guard.py`）——
      ⚠ 我第一版判据写在 `sw_guard.py` 上 ⇒ **测试当场失败**，才发现真源在别处
        （★ 这正是「判据要落在**真的存在**的那个组织单元上」的又一次实例，
          与事实 51 同族）。
    ★ 若有人删掉那段 ⇒ 本测试失败 ⇒ 后人不会在「没有沙盒复制」的前提下按事实 561 排查。
    """
    p = ROOT / "scripts" / "sw_sandbox.py"
    assert p.is_file(), "★ 沙盒模块没了：%s" % p
    t = p.read_text(encoding="utf-8", errors="replace")
    assert "resolve_input" in t, "★ 沙盒没有 resolve_input 了？"
    assert "复制进沙盒" in t, "★ 沙盒不再复制输入了？（事实 561 的前提变了）"
    #: ★ 事实 561 本身必须在台账里（★ 否则后人查不到）
    kf = (ROOT / "docs" / "known-facts.md").read_text(encoding="utf-8",
                                                      errors="replace")
    assert "## 561 ·" in kf, "★ 事实 561 没写进 known-facts.md"
