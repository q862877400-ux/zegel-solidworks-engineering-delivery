"""★ 测 `AddMate5` 的**记档保留**是有据的（★ 阶段 2 · T1 · 含负例 · 且守住"别乱换"）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IAssemblyDoc\`）
# 文件:   `scripts/sw_assembly.py::add_mate` · `scripts/sw_assembly_doc.py::add_mate`
# 定位:   ★ 阶段 2 · T1 的逐条流程第一条：★ **先查官方签名与 Remarks** ✓
#   ★★ **官方逐字**（★ `IAssemblyDoc/AddMate5.md`）：「**Obsolete. Superseded by
#     `IAssemblyDoc::CreateMate`**.」✓
#   ★★★ **而它的 `## Remarks` 逐字给了**三条分流****：
#     ★ 「Standard, advanced, and mechanical mates ⇒ `IAssemblyDoc::CreateMate`」·
#     ★★ 「Misaligned concentric mates ⇒ `AddConcentricMateWithTolerance`」·
#     ★★★ 「Cylindrical distance mates ⇒ `AddDistanceMate`」✓
#   ★★★★ **而后继 `CreateMate(object MateData)` 要**先造 `I*MateFeatureData`** ⇒
#     ★ **本处是通用包装（`mate_type` 是运行时参数）⇒ 不能一处替换** ✓
#   ★★★★★ **∴ 本轮**记档保留**** —— ★ 而本测试守的就是「**要么换对、★ 要么写清为什么没换**」✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ASM = REPO / "scripts" / "sw_assembly.py"
DOC = REPO / "scripts" / "sw_assembly_doc.py"
OFF = Path(r"C:\swapi\types\IAssemblyDoc\AddMate5.md")


def test_official_page_gives_three_routes() -> None:
    """★★★ **前提断言**：★ 官方那页**确实**给了三条分流（★ 判据的锚点）✓"""
    if not OFF.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = OFF.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" in t and "IAssemblyDoc::CreateMate" in t, "★ 废弃链变了"
    for name in ("CreateMate", "AddConcentricMateWithTolerance", "AddDistanceMate"):
        assert name in t, "★ 官方 Remarks 里的分流 `%s` 不见了 ⇒ 判据要重看" % name


def test_both_sites_are_documented_as_kept_on_purpose() -> None:
    """★★★ 核心断言：★ **两处**都要写明「**记档保留（★ 有意不换）**」✓

    ★★ 本仓纪律：★★★ **「不可换」也要**有据、★ 且要写在**第一现场**** ✓
    """
    for p in (ASM, DOC):
        t = p.read_text(encoding="utf-8", errors="replace")
        i = t.find("def add_mate")
        assert i != -1, "★ 找不到 `add_mate`（%s）" % p.name
        seg = t[i:i + 3200]
        assert "记档保留" in seg, "★ %s 没写「记档保留」" % p.name
        assert "Obsolete" in seg, "★ %s 没写官方废弃依据" % p.name


def test_negative_case_the_reason_is_specific_not_vague() -> None:
    """★★★ **负例 · 理由要具体**：★ 必须写明**为什么不能一处替换**（★ 不只是"很复杂"）✓

    ★★ 判据：★ 要出现**三条分流里的至少两条** + ★ **`IMateFeatureData` 那个前置** ⇒
      ★★★ **说明理由是从**官方原文**读出来的，★ 不是我推的** ✓
    """
    t = ASM.read_text(encoding="utf-8", errors="replace")
    i = t.find("def add_mate")
    seg = t[i:i + 3200]
    routes = sum(1 for n in ("CreateMate", "AddConcentricMateWithTolerance", "AddDistanceMate")
                 if n in seg)
    assert routes >= 2, "★ 只写了 %d 条分流 ⇒ 理由不够具体" % routes
    assert "IMateFeatureData" in seg, "★ 没写后继的前置（★ 那才是不能硬换的真因）"


def test_negative_case_still_calls_the_working_member() -> None:
    """★★ **负例 · 别乱换**：★ 在这条**记档保留**的期间，★ 代码**仍要调 `AddMate5`** ✓

    ★★ 为什么：★ **硬换成错的分流会直接坏掉装配功能** ⇒
      ★★★ **"没换"必须是**有意的**、★ 而不是"忘了"** ✓
      ★★ 而**一旦某轮真去换**（★ 分流 + 真机验证）⇒ ★ **本测试会红** ⇒ **那时把它改成新入口** ✓
    """
    code = "\n".join(l for l in ASM.read_text(encoding="utf-8", errors="replace").splitlines()
                     if not l.lstrip().startswith("#"))
    assert re.search(r"\.AddMate5\(", code), (
        "★ `AddMate5` 的调用没了 —— ★ 要么真换了（请改本测试）、★ 要么被误删了")
