"""★ EC00 T006/T007 判据：官方签名核验留档 + `round_chain` 副作用清单（★ 静态 · ★ 不连接 COM）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/research/T006-official-signature.md`（★ 官方签名核验）
#         `C:\swapi\types\ISketchRelationManager\AddRelation.md`（★ 官方逐字 · 2 参）
#         `C:\swapi\types\ISketchRelationManager\IAddRelation.md`（★ 指针变体 · 3 参）
#         `C:\swapi\enums\swConstraintType_e.md`（★ 86 个成员）
#         `tools/round_chain.ps1`（★ 副作用清单 · ★ T007）
# 定位:   ★ EC00 **T006**（官方签名核验）与 **T007**（`round_chain` 副作用清单）的判据。
#         ★★ 纪律（★ 计划 §10.4）：**静态**、★ **不连接 COM**、★ **文件缺失时结论为 blocked**。
# 官方依据: 见上（★ 三页逐字）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"
REL_SRC = ROOT / "scripts" / "sw_sketch_relations.py"
ROUND_CHAIN = ROOT / "tools" / "round_chain.ps1"
SWAPI = Path(r"C:\swapi")


# ── T006 ──────────────────────────────────────────────────────────────

def test_t006_signature_record_exists_and_quotes_official():
    """★★★ T006：官方签名核验留档必须存在，且**逐字**含官方签名。"""
    p = SPEC / "research" / "T006-official-signature.md"
    assert p.is_file(), "★ 缺 T006 的核验留档"
    body = p.read_text(encoding="utf-8", errors="replace")
    #: ★★ 官方签名逐字（★ 2 参 · `object` + `int`）
    assert "SketchRelation AddRelation( System.object Entities, System.int RelationType )" in body, (
        "★ 留档里没有 `AddRelation` 的**官方签名逐字**")
    #: ★★ 指针变体逐字（★ 3 参）—— ★ 两者必须**被区分**
    assert "IAddRelation( System.int NumEntities, ref System.object EntityArray, System.int RelationType )" in body, (
        "★ 留档里没有区分指针变体 `IAddRelation`（★ 3 参）⇒ ★ 会重蹈「参数个数不正确」")


def test_t006_repo_call_matches_official_arity():
    """★★★ T006：本仓对 `AddRelation` 的调用**形参个数**必须与官方（**2**）一致。

    ★★ 依据：★ 官方 `AddRelation` **2 参**、★ `IAddRelation` **3 参**
      ⇒ ★★★ **传错个数 ⇒ `0x8002000E`「参数个数不正确」**（★ 历史第 20 轮的坑）。
    """
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
            if name == "add_relation":
                calls.append(node)
    assert calls, "★ 找不到 `add_relation(...)` 的调用点"
    #: ★ 至少一处是 2 实参（★ 官方口径）
    arities = [len(c.args) for c in calls]
    assert 2 in arities, (
        "★★ `add_relation` 的调用实参个数是 %r ⇒ ★ **没有一处是官方的 2 参**" % arities)


def test_t006_remarks_precondition_is_recorded():
    """★★★ T006：官方 `## Remarks` 的**唯一前置**（★ 活动草图）必须被留档。

    ★ 官方逐字：★「A sketch must be active for this method to have any effect.」
    """
    body = (SPEC / "research" / "T006-official-signature.md").read_text(encoding="utf-8", errors="replace")
    assert "A sketch must be active for this method to have any effect" in body, (
        "★ 留档里没有官方 Remarks 的**唯一前置**逐字")
    #: ★★ 并且必须**如实登记**本仓未显式查「活动草图」这个缺口
    assert "活动草图" in body, "★ 没登记「本仓未显式查活动草图」这个缺口"


def test_t006_constraint_enum_names_are_distinguished():
    """★★ T006：`swConstraintType_*`（★ 官方枚举）与 `sg*`（★ 字符串口径）**必须被区分**。

    ★★ 依据：★ `AddRelation` 收 **`swConstraintType_e` 数值**；
      ★ 而 `SketchAddConstraints` 收 **`sg*` 字符串** —— ★★ **两个不同入口、两套命名**。
    """
    body = (SPEC / "research" / "T006-official-signature.md").read_text(encoding="utf-8", errors="replace")
    assert "swConstraintType_" in body and "sg*" in body, (
        "★ 留档没有区分 `swConstraintType_*` 与 `sg*` 两套命名")


# ── T007 ──────────────────────────────────────────────────────────────

def test_t007_round_chain_side_effects_are_inventoried():
    """★★★ T007：`tools/round_chain.ps1` 的**副作用**必须被**实测登记**（★ 静态扫源码）。

    ★★ 依据（★ 计划 §6.2 逐字）：★「已发现 `round_chain.ps1` 收尾包含**全量暂存与关闭 SW**
      等风险动作 …… ★★ **它不是纯只读收尾**」。
    ★ 判据：★ ① 该脚本里**确实有** `git add -A`；★ ② **确实有** `reclaim_solidworks.py --close`。
    """
    assert ROUND_CHAIN.is_file(), "★ 找不到 `tools/round_chain.ps1`"
    src = ROUND_CHAIN.read_text(encoding="utf-8", errors="replace")
    n_add = len(re.findall(r"^\s*git add -A\s*$", src, re.M))
    assert n_add >= 1, (
        "★★ 没在 `round_chain.ps1` 里找到 `git add -A` ⇒ ★ 要么脚本变了、要么判据失效")
    assert "--close" in src and "reclaim_solidworks" in src, (
        "★★ 没找到 `reclaim_solidworks.py --close` ⇒ ★ 副作用清单失效")


def test_t007_side_effect_record_exists():
    """★★ T007：副作用清单必须**落档**（★ 不能只在测试里）。"""
    body = (SPEC / "research.md").read_text(encoding="utf-8", errors="replace")
    assert "round_chain" in body, "★ `research.md` 里没有 `round_chain` 的副作用段"
    #: ★★ 必须写明「不跑整条链」的替代
    assert "release_check.py" in body, "★ 没写明替代（★ 用 `release_check.py` + 聚焦 pytest）"


def test_t007_this_spec_does_not_run_the_whole_chain():
    """★★★ T007 的**行为判据**：本特性的文档**不得**指示运行整条 `round_chain.ps1`。

    ★★ 依据：★ 拆分（T029）完成前，★★ **不直接运行整条链**（★ 计划 §6.2）。
    """
    for name in ("plan.md", "tasks.md", "research.md", "baseline.md"):
        p = SPEC / name
        if not p.is_file():
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        #: ★ 允许**提到**它（★ 那是登记风险），★ 但不允许写成「运行它」
        bad = re.findall(r"运行\s*`?pwsh[^\n]*round_chain", body)
        assert not bad, "★ `%s` 里指示运行整条 `round_chain.ps1`：%r" % (name, bad)
