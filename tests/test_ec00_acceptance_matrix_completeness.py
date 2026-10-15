"""★ EC00 T030/T031 判据：**验收矩阵完整** + **quickstart 入口真实**（★ 离线 · ★ 不连 COM）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/spec.md`（★ 15 条 FR · 6 个 US · 8 条 SC）
#         `specs/302-ec00-trustworthy-tool-base/acceptance.md`（★ FR→任务→测试→证据矩阵）
#         `specs/302-ec00-trustworthy-tool-base/tasks.md`（★ T001–T032）
# 定位:   ★ EC00 **T030**（★ 验收证据矩阵 · ★ 负面事实清单）与 **T031**（★ quickstart 与交接）。
#         ★★★ **T030 完成判据**：★ 每个完成任务**有证据**，★ **未运行真机不升级等级**；
#           ★ **范围外旧欠账仍保留**。
#         ★★★ **T031 完成判据**：★ **没有伪造命令或就绪声明**；★ 指明 **EC01/EC04 接口和边界**。
# 官方依据: 总计划 §1.3（★ 配套文件清单）· §8.2（★ 勾选规则）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"


def _read(name: str) -> str:
    p = SPEC / name
    assert p.is_file(), "★ 缺 `%s`" % name
    return p.read_text(encoding="utf-8", errors="replace")


# ── T030 ① 15 条 FR 全覆盖 ───────────────────────────────────────────

def test_t030_all_fifteen_frs_are_in_the_matrix():
    """★★★ T030：★ **15 条 FR 必须全部出现在验收矩阵里**（★ 无需求孤岛）。"""
    acc = _read("acceptance.md")
    missing = [n for n in range(1, 16) if ("FR-%03d" % n) not in acc]
    assert not missing, "★★ 验收矩阵缺这些 FR：%r" % ["FR-%03d" % n for n in missing]
    #: ★★ 每条 FR 都要有**任务**与**测试**列（★ 表格行必须带 `T0` 与 `.py`/`T0`）
    rows = [ln for ln in acc.splitlines() if ln.startswith("| **FR-")]
    assert len(rows) >= 15, "★ 矩阵行数不足 15：%d" % len(rows)
    for ln in rows:
        assert re.search(r"T0\d\d", ln), "★★ 某条 FR 行里没有任务号：%s" % ln[:70]
        assert ".py" in ln or "T0" in ln, "★★ 某条 FR 行里没有测试：%s" % ln[:70]


def test_t030_matrix_has_no_unsupported_pass_claim():
    """★★★ T030：★ 矩阵里**不得出现无证据的 `pass`**（★ 未运行 ⇒ 必须 `not_run`）。

    ★★ 依据（★ `tasks.md` §〇 逐字）：★「★ **未运行真机不升级等级**」。
    """
    acc = _read("acceptance.md")
    #: ★★ 真机 5 项（FR-012 等）**必须是 `not_run`**
    assert "not_run" in acc, "★★ 矩阵里没有 `not_run` ⇒ ★ 可能把未运行写成了通过"
    #: ★★ 三级结论表里 `runtime` 与 `product` 的**结论列**必须是 not_run
    #:   ⚠ 第一版按「行里含 runtime 且不含 not_run」判 ⇒ ★ 被**规则句**（★ V8 那行
    #:   「离线 pass 不升级 runtime 等级」）误判 ⇒ ★ 红了一次。
    #:   ★ 真判据：★ 只看**结论列**（★ 表格最后一格）里有没有 `pass`。
    bad = []
    for line in acc.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        #: ★ 第一格是「级别」时，★ 才检查结论列
        if cells[0] in ("**runtime**", "**product**", "runtime", "product"):
            verdict = cells[-1]
            if "not_run" not in verdict:
                bad.append(line[:100])
    assert not bad, (
        "★★ runtime/product 的结论列**不是 not_run** ⇒ ★ 未运行被写成了通过：\n  "
        + "\n  ".join(bad))


def test_t030_scope_keeps_out_of_scope_debt():
    """★★★ T030：★ **范围外旧欠账仍保留**（★ 逐字承完成判据）。

    ★★ 依据（★ `research.md` §一 逐字）：★ 212 的**有意挂起 4 项**不得被本特性清空。
    """
    r = _read("research.md")
    assert "有意挂起" in r, "★ 迁移表里没有「212 有意挂起 4 项」的特别登记"
    assert "原状态" in r, "★ 迁移表里没有「原状态是否变化」列"


# ── T030 ② 负面事实清单 ──────────────────────────────────────────────

def test_t030_negative_facts_are_listed():
    """★★ T030：★ **负面事实清单必须具名**（★ 计划 §8.3 逐字：「保留来源与负面结论」）。"""
    acc = _read("acceptance.md")
    assert "残余风险" in acc, "★ 验收记录里没有「残余风险」段"
    #: ★★ 必须点到**具体**的未完成项
    assert "真机" in acc, "★ 没有登记「真机未做」"
    assert "未提交" in acc, "★ 没有登记「未提交未部署」"


# ── T031 ① quickstart 不伪造命令 ─────────────────────────────────────

def test_t031_quickstart_has_no_fabricated_commands():
    """★★★ T031：★ quickstart **不得**含伪造命令（★ 逐字承完成判据）。

    ★★ 依据（★ 计划 §1.3 逐字）：★「★ 本文不运行任何命令。下列是正式施工的约束，
      ★ **不是本轮已执行结果**」。
    """
    q = SPEC / "quickstart.md"
    assert q.is_file(), "★ 缺 `quickstart.md`（★ T031 的产物）"
    body = q.read_text(encoding="utf-8", errors="replace")
    #: ★★ 必须**显式声明**「未运行」
    assert "未运行" in body or "not_run" in body, (
        "★★ quickstart 没有声明「未运行」⇒ ★ 会被当成已执行结果")
    #: ★★ 不许出现「已就绪」这类声明（★ 除非有真机证据）
    for bad in ("环境已就绪", "已确认就绪", "真机已验证"):
        assert bad not in body, "★★ quickstart 里出现了「%s」⇒ ★ 伪造了就绪声明" % bad


def test_t031_quickstart_points_to_ec01_and_ec04():
    """★★★ T031：★ quickstart 必须指明 **EC01/EC04 的接口和边界**（★ 逐字承完成判据）。"""
    body = (SPEC / "quickstart.md").read_text(encoding="utf-8", errors="replace")
    assert "EC01" in body, "★ quickstart 里没有指向 EC01"
    assert "EC04" in body, "★ quickstart 里没有指向 EC04"


def test_t031_quickstart_entry_paths_are_real():
    """★★ T031：★ quickstart 里提到的**路径必须真实存在**（★ 不伪造入口）。"""
    body = (SPEC / "quickstart.md").read_text(encoding="utf-8", errors="replace")
    #: ★ 抽出形如 `scripts/xxx.py` / `tests/test_xxx.py` / `tools/xxx.py` 的路径
    refs = set(re.findall(r"`((?:scripts|tests|tools|mcp-server)/[A-Za-z0-9_./\-]+\.py)`", body))
    missing = [r for r in sorted(refs) if not (ROOT / r).is_file()]
    assert not missing, "★★ quickstart 引用了**不存在**的路径：%r" % missing
    #: ★★ 至少要引用**真的**入口（★ 空集也算伪造）
    assert refs, "★ quickstart 里没有引用任何可核验的入口路径"


# ── T031 ② 交接必须写明下一动作 ──────────────────────────────────────

def test_t031_handoff_states_the_next_action():
    """★★ T031：★ 交接必须写明**下一轮第一动作**（★ 计划 §8.3 逐字）。"""
    body = (SPEC / "quickstart.md").read_text(encoding="utf-8", errors="replace")
    assert "下一轮的第一动作" in body or "下一步" in body or "下一动作" in body, (
        "★ 交接里没有「下一轮的第一动作」")
    #: ★★ 必须点到**具体任务号**
    assert re.search(r"T0\d\d", body), "★ 「下一步」没有点到具体任务号"
