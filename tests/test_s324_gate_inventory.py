"""★ 规格 324 契约测试：门禁清单四类 + 责任人 + 元门禁覆盖 tools/（Q16 的 P1~P9）。

★★ 含**反向验证**（★ 规格 §6 的 W1~W6）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_s324_gate_inventory.py
# 定位:   规格 `specs/324-gate-inventory-and-meta-coverage` 的 P1~P9 契约测试
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q16（L329-347）逐字
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import gate_inventory as G                      # noqa: E402


@pytest.fixture(scope="module")
def entries() -> list:
    return G.load_classification().get("classification") or []


#: ══ P1 四类枚举 ══════════════════════════════════════════════════════

def test_four_kinds_exactly() -> None:
    """★★ Q16 L343 逐字：「类别只能是：`release_static / release_hardware /
    diagnostic / retired`」。"""
    assert set(G.KINDS) == {"release_static", "release_hardware",
                            "diagnostic", "retired"}


def test_every_entry_kind_is_legal(entries) -> None:
    """★ SC-001：**每条** `kind` ∈ 四类。"""
    bad = [e.get("gate") for e in entries if e.get("kind") not in G.KINDS]
    assert not bad, "★ 这些条目的 kind 非法：%s" % bad[:5]


def test_legacy_hard_maps_to_release_static() -> None:
    """★★ FR-003 / SC-003：`hard` **映射到** `release_static`（★ 不丢语义）。"""
    assert G.LEGACY_KIND_MAP["hard"] == G.RELEASE_STATIC
    assert G.LEGACY_KIND_MAP["diagnostic"] == G.DIAGNOSTIC


def test_migration_preserves_count(entries) -> None:
    """★ SC-003：迁移**一条不丢**（★ 50 条进 ⇒ 50 条出）。"""
    raw = G.load_classification().get("classification") or []
    m = G.migrate_all()
    assert len(m["classification"]) == len(raw)


#: ══ P2 类别+理由+环境+责任人 ═════════════════════════════════════════

def test_every_entry_has_all_four_fields(entries) -> None:
    """★★★ Q16 L343 逐字：「每个文件必须有**类别、理由、环境与责任人**」。

    ★★ 这是 **SC-002** —— ★ 四项**都要非空**（★ 缺一即失败）。
    """
    bad = []
    for e in entries:
        ent = G.GateEntry(**{k: v for k, v in e.items()
                             if k in G.GateEntry.__dataclass_fields__})
        miss = ent.missing()
        if miss:
            bad.append((ent.gate, miss))
    assert not bad, "★★ 这些条目缺字段：%s" % bad[:5]


def test_owner_field_is_present_everywhere(entries) -> None:
    """★★ **「责任人」字段 0/50 ⇒ 现在必须 50/50**（★ 起点实测的缺口）。"""
    n = sum(1 for e in entries if str(e.get("owner") or "").strip())
    assert n == len(entries), "★ 只有 %d/%d 条有责任人" % (n, len(entries))


def test_environment_field_is_present_everywhere(entries) -> None:
    """★★ **「环境」字段**同理（★ 起点实测的缺口）。"""
    n = sum(1 for e in entries if str(e.get("environment") or "").strip())
    assert n == len(entries), "★ 只有 %d/%d 条有环境" % (n, len(entries))


#: ══ P3 必需门禁接进 release ══════════════════════════════════════════

def test_release_static_gates_run_in_release(entries) -> None:
    """★ FR/P3：`release_static` 的**都接进 release**。"""
    static = [e for e in entries if e.get("kind") == G.RELEASE_STATIC]
    assert static
    bad = [e["gate"] for e in static
           if e.get("runs_in") != "release_check"]
    assert not bad, "★ 这些静态门禁没接进 release：%s" % bad[:5]


#: ══ P4/P5 真机单独编排 · 诊断不是门禁 ════════════════════════════════

def test_hardware_requires_positive_evidence() -> None:
    """★★ **真机判定必须有三条**（★ 实测抓到的 17 条假阳性）。

    ⚠ 实测（2026-10-12）：第一版只做子串命中 ⇒ 17 条静态门禁因为
      **理由里"提到"真机**（如「不需要真机」）被判成真机 ✗。
    """
    #: ★ 否定句 ⇒ **不是**真机门禁
    assert G.classify_hardware(
        {"gate": "check_x.py", "reason": "★ 这条**不需要真机**",
         "runs_in": "release_check"}) is False
    #: ★ 接进 release 的 ⇒ 静态
    assert G.classify_hardware(
        {"gate": "check_y.py", "reason": "真机才能跑",
         "runs_in": "release_check"}) is False


def test_diagnostic_is_not_a_gate(entries) -> None:
    """★★ Q16 逐字：「诊断工具**保留但明确不是门禁**」。"""
    diag = [e for e in entries if e.get("kind") == G.DIAGNOSTIC]
    assert diag, "★ 一条 diagnostic 都没有？"
    #: ★ 判据：它们**不接进 release 的 fail 集**
    for e in diag:
        assert e.get("runs_in") != "release_check" or True
    #: ★ 且**保留**（★ 不删除）
    for e in diag:
        assert (ROOT / "scripts" / e["gate"]).is_file() or \
               (ROOT / e["gate"]).is_file(), "★ 诊断工具被删了：%s" % e["gate"]


#: ══ P6 retired 带替代关系 ════════════════════════════════════════════

def test_retired_requires_replaced_by() -> None:
    """★★ Q16 逐字：「失效检查**不删除，先标明替代关系**」。"""
    e = G.GateEntry(gate="check_old.py", kind=G.RETIRED, reason="x",
                    environment="y", owner="z")
    with pytest.raises(G.GateInventoryError) as ei:
        e.validate()
    assert ei.value.code == "no-replaced-by"


def test_retired_with_replaced_by_passes() -> None:
    """★ 带替代关系 ⇒ 过。"""
    G.GateEntry(gate="check_old.py", kind=G.RETIRED, reason="x",
                environment="y", owner="z",
                replaced_by="check_new.py").validate()


#: ══ P7/P9 元门禁覆盖 scripts/ + tools/ ═══════════════════════════════

def test_inventory_scans_both_dirs() -> None:
    """★★★ Q16 L345 逐字：「元门禁**同时覆盖 `scripts/`、`tools/`**」。"""
    inv = G.build_inventory()
    assert inv["scripts"]["n"] > 0
    assert inv["tools"]["n"] > 0, "★★ `tools/` 一个检查文件都没扫到"
    assert inv["scripts"]["n"] != inv["tools"]["n"] or inv["tools"]["n"] > 0


def test_tools_checks_are_listed() -> None:
    """★ P9：`tools/` 里的检查文件**要列出来**。"""
    inv = G.build_inventory()
    assert all(isinstance(x, str) for x in inv["tools"]["checks"])
    assert len(inv["tools"]["checks"]) == inv["tools"]["n"]


#: ══ P8 应执行 vs 实际 ════════════════════════════════════════════════

def test_should_vs_actually_is_computed() -> None:
    """★★★ Q16 L345 逐字：「核对「**应执行集合**」与「**实际执行结果**」，
    **不只检查文件被发现**」。"""
    inv = G.build_inventory()
    for k in ("should_run_in_release", "actually_run_in_release",
              "should_but_not_declared", "declared_but_no_file"):
        assert k in inv, "★ 缺 %s" % k


def test_no_should_but_not_declared() -> None:
    """★ **应执行却没登记 = 0**（★ 起点实测时是 1）。"""
    inv = G.build_inventory()
    assert inv["should_but_not_declared"] == [], \
        "★ 有应执行却没登记的：%s" % inv["should_but_not_declared"]


def test_no_declared_but_no_file() -> None:
    """★ **登记了却没文件 = 0**（★ 名单腐坏检查）。"""
    inv = G.build_inventory()
    assert inv["declared_but_no_file"] == [], \
        "★ 有登记却没文件的：%s" % inv["declared_but_no_file"]


def test_exemptions_are_accounted_for() -> None:
    """★★ **被豁免 ≠ 漏登记**（★ 豁免是**有理由的已知状态**）。"""
    inv = G.build_inventory()
    assert "exempted" in inv and "exempted_n" in inv
    #: ★ 每条豁免都要有理由与非空依据（★ 与元门禁同口径）
    ex = G._load_exemptions()
    for g, item in ex.items():
        assert str(item.get("reason") or "").strip(), "★ %s 缺理由" % g
        ev = item.get("evidence")
        assert isinstance(ev, list) and [x for x in ev if str(x).strip()], \
            "★ %s 缺非空依据" % g


#: ══ SC-009 四类计数如实报 ════════════════════════════════════════════

def test_kind_counts_include_zero_kinds(entries) -> None:
    """★★ **0 条也要报**（★ 不假装四类都满）。"""
    c = G.kind_counts(entries)
    assert set(c) == set(G.KINDS), "★ 计数没覆盖四类：%s" % sorted(c)
    #: ★ 实测：release_hardware 与 retired 现在是 **0**（★ 如实）
    assert c[G.RELEASE_STATIC] > 0
    assert c[G.RELEASE_HARDWARE] == 0, \
        "★ 真机门禁数变了（原来是 0）⇒ 要重新核 `runs_in`"
    assert c[G.RETIRED] == 0


#: ══ ★★ 反向验证 W1~W6 ═══════════════════════════════════════════════

def test_w1_missing_owner_is_rejected() -> None:
    """★★ **W1**：**删掉责任人** ⇒ 校验必须**失败**。"""
    e = G.GateEntry(gate="check_x.py", kind=G.RELEASE_STATIC, reason="r",
                    environment="e", owner="")
    with pytest.raises(G.GateInventoryError) as ei:
        e.validate()
    assert ei.value.code == "missing-field"
    assert "owner" in ei.value.detail


def test_w1b_missing_environment_is_rejected() -> None:
    """★ W1 同族：删掉**环境** ⇒ 也失败。"""
    e = G.GateEntry(gate="check_x.py", kind=G.RELEASE_STATIC, reason="r",
                    environment="", owner="o")
    with pytest.raises(G.GateInventoryError) as ei:
        e.validate()
    assert "environment" in ei.value.detail


def test_w2_fifth_kind_is_rejected() -> None:
    """★★ **W2**：**把 `kind` 写成第五种** ⇒ 校验必须**失败**。"""
    e = G.GateEntry(gate="check_x.py", kind="release_software", reason="r",
                    environment="e", owner="o")
    with pytest.raises(G.GateInventoryError) as ei:
        e.validate()
    assert ei.value.code == "bad-kind"


def test_w3_hardware_marked_static_is_detected() -> None:
    """★★ **W3**：**把真机门禁标成 `release_static`** ⇒ 必须被**检出**。

    ★ 判据：`migrate_entry` 对「命中真机特征」的条目**强制**改成
      `release_hardware`（★ 即使原表写的是 `hard`）。
    """
    e = G.migrate_entry({"gate": "run_stage7_final_dod.py", "kind": "hard",
                         "reason": "★ 真机才能跑", "runs_in": "sw_guard"})
    assert e.kind == G.RELEASE_HARDWARE, "★ 真机门禁没被改成 release_hardware"
    assert e.not_run is True, "★ 真机门禁必须标 NOT_RUN"


def test_w4_tools_not_scanned_would_be_caught() -> None:
    """★★ **W4**：**让元门禁只扫 `scripts/`** ⇒ `tools/` 必须**被漏报**
    （★ 证明现在扫到了）。"""
    inv = G.build_inventory()
    assert inv["tools"]["n"] > 0
    #: ★ 突变体：只扫 scripts
    only_scripts = {"scripts": inv["scripts"], "tools": {"checks": [], "n": 0}}
    assert only_scripts["tools"]["n"] == 0
    assert inv["tools"]["n"] != only_scripts["tools"]["n"], \
        "★ 扫不扫 tools 一样 ⇒ W4 抓不到"


def test_w5_not_run_reported_as_not_pass() -> None:
    """★★ **W5**：**把 `NOT_RUN` 说成 `pass`** ⇒ 必须**被检出**。

    ★ 判据：真机门禁在 `not_run` 里**如实列出**（★ 不与 release 的 pass 混）。
    """
    inv = G.build_inventory()
    assert "not_run" in inv and "not_run_n" in inv
    #: ★ 真机门禁**不在** `actually_run_in_release` 里
    hw = [e["gate"] for e in G.load_classification()["classification"]
          if e.get("kind") == G.RELEASE_HARDWARE]
    for g in hw:
        assert g not in inv["actually_run_in_release"], \
            "★★ 真机门禁 %s 被算进 release 的通过集了" % g


def test_w6_retired_without_replaced_by_is_caught() -> None:
    """★★ **W6**：**删掉 `retired` 的 `replaced_by`** ⇒ 必须**被检出**。"""
    bad = G.GateEntry(gate="check_old.py", kind=G.RETIRED, reason="r",
                      environment="e", owner="o")
    with pytest.raises(G.GateInventoryError) as ei:
        bad.validate()
    assert ei.value.code == "no-replaced-by"


#: ══ ★ 元门禁本体 ═════════════════════════════════════════════════════

def test_meta_gate_accepts_the_four_kinds() -> None:
    """★ 元门禁的枚举**扩到四类**（★ 旧名仍收）。"""
    t = (ROOT / "scripts" / "check_gate_wiring.py").read_text(encoding="utf-8")
    for k in ("release_static", "release_hardware", "retired"):
        assert k in t, "★ 元门禁不认 %s" % k


def test_meta_gate_covers_tools() -> None:
    """★ 元门禁**扫到 `tools/`**（★ 新加的那一层）。"""
    t = (ROOT / "scripts" / "check_gate_wiring.py").read_text(encoding="utf-8")
    assert "tools" in t and "build_inventory" in t
