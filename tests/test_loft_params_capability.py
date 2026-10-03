"""★ 测「放样能力」+「类型名表那套机制」（★ 含负例 · 轮 131）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ILoftFeatureData\\*.md` +
#         真机证据 `output/loft-params-capability-recheck.json`
# 文件:   tests/test_loft_params_capability.py（★ 新）
# 定位:   ★★★★★★★ 2026-10-04（轮 131）**三条真读数**：
#     ★ **① 机制**：★ 与上一轮 `Revolve`/`Revolution` **同型的第二次**（★ 我猜 `Loft`、
#       而真机是 **`Blend`**）⇒ ★★ **⇒ 把"猜名字"换成 `FEATURE_TYPE_NAMES` 表**、
#       ★ **表中每个名字都要有**证据引用**** ✓
#     ★★ **② 真机读数**：★ `放样1` · ★ `GetProfileCount = **2**` · ★ `IsBossFeature = true` ·
#       ★ `IsThinFeature = false` · ★ `Close = false` · ★ `StartTangentLength = **0.1**` ✓
#     ★★★ **③ 而 `NumberOfSections = 1.0` 与 `GetProfileCount = 2` 不一致** ——
#       ★ **那不是矛盾**（★ 官方那两个名字是「Number of sections」与「Number of profiles」）✓
#   ★★★★ **⚠ 那几个量的口径仍 `unknown`**（★ 都带前置）⇒ ★ **不谎称** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402

SRC = REPO / "scripts" / "sw_feature_readback.py"
PROBE = REPO / "tools" / "probe_loft_params_recheck.py"


def test_the_real_readings_are_recorded() -> None:
    """★★★ 核心断言：★ 真机那几个读数在能力里（★ 那是"怎么知道的"）✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "loft_params")
    assert "放样1" in body or "Blend" in body, "★ 真机那个类型名没记下"
    assert "GetProfileCount = **2**" in body or "GetProfileCount = 2" in body, \
        "★ 轮廓数那个读数没记下"
    assert "0.1" in body, "★ `StartTangentLength` 那个读数没记下"


def test_the_two_similar_names_are_not_conflated() -> None:
    """★★★★ 核心断言：★ `NumberOfSections` 与 `GetProfileCount` **是不同的量** ✓

    ★★ **为什么**：★ 真机上 `NumberOfSections = 1.0` 而 `GetProfileCount = 2`
      ⇒ ★★★ **⇒ 若我把它当成"矛盾"、★ 就会去"修"一个不存在的问题**** ✓
    """
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "loft_params")
    assert "sections" in body and "profiles" in body, (
        "★ 两个名字的**区别**要写在 docstring 里（★ 免得后人当成矛盾）")


def test_the_open_units_are_marked_open() -> None:
    """★★★ 核心断言：★ **没量到的**仍标 `unknown`（★ 不谎称）✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "loft_params")
    for q in ("StartConstraintDraftAngle", "StartTangentLength", "GetWallThickness"):
        assert q in body, "★ `%s` 的口径没标" % q
    assert "unknown" in body, "★ 要如实标 `unknown`"


def test_negative_case_type_names_come_from_a_table_with_evidence() -> None:
    """★★★★★ 核心断言：★ 类型名走 **`FEATURE_TYPE_NAMES` 表**、★ **不再就地猜字面量** ✓

    ★★ **为什么这条最重要**：★ 本会话**连续两轮**在"猜类型名"上栽了
      （★ 轮 130 猜 `Revolve` 而真机是 `Revolution`；★ 轮 131 猜 `Loft` 而真机是 `Blend`）⇒
      ★★★ **⇒ 根因不是"不够小心"、★ 是**名字写在代码里、★ 没有出处**** ⇒
      ★★ **⇒ 机制：集中一张表 + ★ 每行带证据引用** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    assert "FEATURE_TYPE_NAMES" in t, "★ 没有那张表"
    #: ★★ **每个族都要走表**（★ 不许再有就地字面量）✓
    import re
    inplace = re.findall(
        r"_read_feature_params\(\s*\n?(?:\s*#:[^\n]*\n)*\s*model, feature_name, (\"[^\"]+\")", t)
    assert not inplace, "★ 还有就地字面量：%r（★ 应走表）" % inplace
    #: ★★★ **表里每行都要有证据引用**（★ `output/` 里的 json）✓
    i = t.find("FEATURE_TYPE_NAMES = {")
    j = t.find("}", i)
    seg = t[i:j]
    assert seg.count("output/") >= 4, (
        "★ 表中每个**已核**的名字都要指到一份 `output/*.json` 证据 ⇒ 现在只有 %d 处"
        % seg.count("output/"))
    #: ★★★★ 而**未核的**要写 `unknown`（★ 铁律 5）✓
    assert "unknown" in seg, "★ 未核的族要写 `unknown`、★ 不许猜"


def test_negative_case_the_probe_writes_evidence_incrementally() -> None:
    """★★★★ **负例**：★ 探针的 `step` 要**每步落盘**（★ 超时也看得到卡在哪）✓

    ★★ **为什么**：★ 轮 130 我读到的是**上一轮的旧证据文件** ⇒
      ★★★ **⇒ 每步落盘让"这一次"与"上一次"分得开** ✓
    """
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    i = t.find("def step(")
    j = t.find("\ndef ", i + 1)
    body = t[i:j if j > 0 else i + 900]
    assert "write_text" in body, "★ `step` 里没有落盘"
