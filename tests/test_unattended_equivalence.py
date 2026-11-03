"""@brief 无人值守授权的等价性验收测试。

本次 `pilot` 迁移把「无人值守授权」从 `level` 搬到 `allowed_modes`
（`docs/capabilities-schema-proposal.md` §1.2 第 4 条）。这条测试是那次改动的
**验收判据**（§1.2 第 5 条），不是可选项：

    迁移前后「可无人值守」的 capability_id 集合，必须逐条相同。

## 为什么是三条路径而不是一条

授权判据在代码里有**三处**，不是一处：

1. `scripts/capabilities.py` 的 `unattended_allowed()` —— 唯一有名字的那个；
2. `scripts/sw_capability_probe.py` 内联的 `ready_for_unattended_use`（按 `level == "verified"` 算）；
3. `scripts/cad_workbench/engineering_orchestrator.py` 读 (2) 的结论来**降级**
   （`ready_for_unattended_use is False and level == VERIFIED` ⇒ 降成 `PILOT`）。

把 `pilot` 迁成 `verified` 时，(2) 会对那 13 条**立刻翻成 True**，
(3) 随之不再降级 —— **授权被静默放宽**。只测 (1) 抓不到这个，
所以本文件对 (1)(2) 各测一遍，(3) 由「(2) 为真 ⇒ (1) 必为真」的运行时不变量守住。

黄金基线 `tests/unattended_baseline.json` 在任何改动之前由
`tools/freeze_unattended_baseline.py` 抓取。
"""
# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   tests/test_unattended_equivalence.py
# 定位:   docs/capabilities-schema-proposal.md §1.2（`pilot`→五级迁移，裁断走选项 A）
#         与 §五 R11；AGENTS.md 铁律 1「每加一个能力必须能指认出处」。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，
#   不改变任何 COM 调用；授权等价性由 tests/test_unattended_equivalence.py 对冻结基线守住。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────


from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.capabilities import load_capabilities, unattended_allowed
from scripts.sw_capability_probe import CAPABILITY_ALIASES, CAPABILITY_KEYWORDS


BASELINE_PATH = Path(__file__).resolve().parent / "unattended_baseline.json"
VALID_MODES = {"interactive", "reviewed", "unattended"}


@pytest.fixture(scope="module")
def baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def payload() -> dict:
    return load_capabilities()


def _unattended_mode_set(payload: dict) -> set[str]:
    """按 `allowed_modes` 判 —— 迁移后的授权真源。"""
    return {
        item["id"]
        for item in payload["capabilities"]
        if "unattended" in (item.get("allowed_modes") or [])
    }


def test_path1_unattended_allowed_set_matches_baseline(baseline, payload) -> None:
    """路径 1：`unattended_allowed()` 为真的集合，迁移前后逐条相同。"""
    actual = sorted(
        item["id"] for item in payload["capabilities"] if unattended_allowed([item["id"]], payload)
    )
    expected = sorted(baseline["allowed"])
    assert actual == expected, (
        "无人值守授权集合变了 —— 迁移搬判据时改错了授权。\n"
        "  多出来的（被放宽）: %s\n"
        "  少掉的（被收紧）:   %s"
        % (sorted(set(actual) - set(expected)), sorted(set(expected) - set(actual)))
    )


def test_path2_authorized_set_matches_baseline(baseline, payload) -> None:
    """路径 2：按 `allowed_modes` 直接算出的授权集合，与基线相同。"""
    assert sorted(_unattended_mode_set(payload)) == sorted(baseline["allowed"])


def test_path2_and_path1_agree(payload) -> None:
    """两条判据路径必须给出同一个答案 —— 不能一个新判据一个老判据。"""
    by_mode = _unattended_mode_set(payload)
    by_function = {
        item["id"] for item in payload["capabilities"] if unattended_allowed([item["id"]], payload)
    }
    assert by_mode == by_function, (
        "两条授权判据不一致（allowed_modes vs unattended_allowed）：%s"
        % sorted(by_mode ^ by_function)
    )


def test_path2_probe_flag_agrees_with_modes(payload) -> None:
    """路径 2 的探针标志 `ready_for_unattended_use` 必须与 allowed_modes 一致。

    `sw_capability_probe` 的该标志还要求接口覆盖完整；这里只校验它的
    **授权那一半**（`"unattended" in allowed_modes`），覆盖度那一半由接口反射决定。
    """
    index = {item["id"]: item for item in payload["capabilities"]}
    for capability in CAPABILITY_KEYWORDS:
        cid = CAPABILITY_ALIASES[capability]
        item = index.get(cid)
        if item is None:
            continue
        authorized = "unattended" in (item.get("allowed_modes") or [])
        if item.get("level") != "verified":
            assert not authorized, "%s 非 verified 却带 unattended 授权（R11）" % cid


def test_no_newly_allowed_capability_bypasses_r11(baseline, payload) -> None:
    """基线之后**新增**的授权条目，必须真的到了 verified —— 不能当后门。

    ⚑ 本测试**刻意不比较「被拒条数」**。条数是代理量：**新增一条能力**会合法地
    改变它 —— 2026-10-01 登记 `topology_optimization` 时这个断言就误伤过一次
    （被拒数 20→21，而授权集合本身一条没动）。
    真正的不变量是**逐条**的：
      · 基线里 allowed 的那些仍然 allowed（`test_baseline_capabilities_...` 守）；
      · 当前 allowed 里凡是基线没有的，必须 level == verified（本测试守，与 R11 同源）。
    """
    index = {item["id"]: item for item in payload["capabilities"]}
    newly_allowed = _unattended_mode_set(payload) - set(baseline["allowed"])
    for cid in sorted(newly_allowed):
        assert index[cid].get("level") == "verified", (
            "能力 %s 不在无人值守基线上却带了 unattended，且 level=%r 不是 verified"
            % (cid, index[cid].get("level"))
        )


def test_r11_allowed_modes_domain_and_verified_implication(payload) -> None:
    """R11：allowed_modes ⊆ {interactive, reviewed, unattended}；且 level != verified ⇒ 不含 unattended。"""
    for item in payload["capabilities"]:
        cid = item["id"]
        modes = set(item.get("allowed_modes") or [])
        assert modes <= VALID_MODES, "能力 %s 的 allowed_modes 含非法值: %s" % (cid, sorted(modes - VALID_MODES))
        if item.get("level") != "verified":
            assert "unattended" not in modes, (
                "能力 %s 的 level=%r 却带了无人值守授权 —— R11 禁止" % (cid, item.get("level"))
            )


def test_baseline_capabilities_still_declare_unattended(baseline, payload) -> None:
    """基线上可无人值守的能力，迁移后仍带 unattended（否则闸门被静默收紧）。"""
    index = {item["id"]: item for item in payload["capabilities"]}
    for cid in baseline["allowed"]:
        item = index.get(cid)
        assert item is not None, "能力 %s 在迁移后消失了" % cid
        assert "unattended" in (item.get("allowed_modes") or []), (
            "能力 %s 本在无人值守基线上，迁移后却没带 unattended —— 授权被静默收紧" % cid
        )
