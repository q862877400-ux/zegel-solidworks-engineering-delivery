"""★ 测「官方页废弃判定」的**精确判据**、★ 并守住**两处已知差异**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `tools/check_obsolete_heuristic.py`（★ 只报不动）
# 定位:   ★ **为什么要它**：★ 我在 `output/_read_*_members.py` 里用的判据 `"Obsolete" in t`
#   ★★ **在 `IFeature/GetTypeName2.md` 那页是**假阳性**** ——
#   ★★★ 那页里 `Obsolete` 出现 4 次、**全是那张"类型 → 接口"表的**单元格内容**** ✓
#   ★★★★ **真机复核**（★ `python tools/check_obsolete_heuristic.py`）：
#     ★ 扫 **12123 页** ⇒ ★ **两种判据不一致的有 33 页**，★ 而**两类都有**：
#       · ★ **假阳性**：★ `IFeature.GetTypeName{,2}` · ★ `IModelView.*StereoSeparation` ·
#         ★★ **`INote.*` 一大批** ⇒ ★ 表格内容 ✓
#       · ★★ **假阴性**（★ **更危险**）：★ **`IModelDocExtension.DeleteRenderMaterial`** ·
#         ★ `AddRenderMaterial` · ★ `AddDefaultRenderMaterial` ⇒
#         ★★★ **它们写的是「Not supported in SOLIDWORKS 2011 and later」** ✓
#   ★★★★★ **而 `DeleteRenderMaterial` 正是本会话 T1 处理过的那条** ——
#     ★ 我当时的读数「官方页**没有** `Obsolete` 行、★ 而名单 `obsolete=True`、★ 措辞是
#       `Not supported in SOLIDWORKS 2011 and later`」⇒ ★★ **完全正确**（★ 新判据也认它）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "check_obsolete_heuristic.py"
SWAPI = Path(r"C:\swapi\types")

_spec = importlib.util.spec_from_file_location("_coh", TOOL)
coh = importlib.util.module_from_spec(_spec)
sys.modules["_coh"] = coh
_spec.loader.exec_module(coh)


def test_the_two_judges_disagree_on_a_known_false_positive() -> None:
    """★★★ **前提断言**：★ `GetTypeName2` 那页是**假阳性**（★ 判据的锚点）✓"""
    p = SWAPI / "IFeature" / "GetTypeName2.md"
    if not p.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = p.read_text(encoding="utf-8", errors="replace")
    assert coh.obsolete_naive(t) is True, "★ 旧判据竟然不命中了 ⇒ 判据要重看"
    assert coh.obsolete_precise(t) is False, "★ 新判据把它判成废弃了 ⇒ 那是错的"


def test_the_precise_judge_catches_the_not_supported_wording() -> None:
    """★★★★ 核心断言：★ 新判据能认出「**Not supported in SOLIDWORKS**」那种措辞 ✓

    ★★ **为什么重要**：★ 那条**旧判据看不到它**（★ 假阴性）⇒
      ★★★ **而 `DeleteRenderMaterial` 写的正是这句** ✓
    """
    p = SWAPI / "IModelDocExtension" / "DeleteRenderMaterial.md"
    if not p.is_file():
        return
    t = p.read_text(encoding="utf-8", errors="replace")
    assert coh.obsolete_naive(t) is False, "★ 旧判据竟然命中了 ⇒ 判据要重看"
    assert coh.obsolete_precise(t) is True, "★ 新判据没认出「Not supported in」措辞"


def test_negative_case_real_obsolete_pages_are_still_caught() -> None:
    """★★★ **负例 · 真废弃还要认**：★ 两条**真的**废弃页在新判据下**仍为 True** ✓"""
    for iface, name in (("IExtrudeFeatureData2", "GetFace"),
                        ("IWizardHoleFeatureData2", "FastenerType")):
        p = SWAPI / iface / (name + ".md")
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        assert coh.obsolete_precise(t) is True, (
            "★ `%s.%s` 真废弃、新判据却漏了" % (iface, name))


def test_negative_case_the_scope_is_written_down() -> None:
    """★★ **负例 · 影响面要写下来**：★ 工具里必须有那条复核读数 ✓"""
    t = TOOL.read_text(encoding="utf-8", errors="replace")
    assert "33 页" in t or "33" in t, "★ 没写影响面的页数"
    assert "假阴性" in t, "★ 没写「假阴性（更危险）」那一类"
    assert "12123" in t, "★ 没写扫了多少页"
