"""★ 测 `mold_evidence` 的**「读不到」与「没有分型」分得开**（★ `JUDGE-C_D_E` 🔴 #14 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `scripts/sw_mold.py::mold_evidence` · `mcp-server/tool_specs_batch1.py`（ToolSpec 的 doc）
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #9`）逐字：「★ `mold_evidence` doc 说**可回读**、
#   ★ 目标自述真机**恒为全 `None`**」✓
#   ★★ **两处说法逐字**：
#     · ToolSpec ⇒「Read back the mold state of the active part: … **Read-only.**」✓
#     · 能力层 ⇒「⚠ 本函数当前仍从旧位置读 ⇒ **它在真机上只会返回全 `None`**」✓
#   ★★★ **真因（轮 172 真机 + 反射复核）**：★ 那些计数**不在 `IFeatureManager`/`IModelDoc2` 上**、
#     而在 **`I*FeatureData`** 上（★ 事实 36 那一族）✓
#   ★★★★ **修法**：★ 光改 doc 不够 —— ★ **调用方无法从返回值区分**「读不到」与「真的没有分型」
#     ⇒ ★ 必须给一个**显式的位**（`readable`）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MOLD = REPO / "scripts" / "sw_mold.py"
SPEC = REPO / "mcp-server" / "tool_specs_batch1.py"


def _seg(path: Path, fn: str) -> str:
    """★ 取函数代码段（★ 剥掉它自己的 docstring —— ★ 事实 513）。"""
    src = path.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            if n.body and isinstance(n.body[0], ast.Expr) and isinstance(
                    getattr(n.body[0], "value", None), ast.Constant) and isinstance(
                    b := n.body[0].value.value, str):
                n.body[0] = ast.Pass()
            return ast.unparse(n)
    return ""


def test_capability_exposes_a_readable_flag() -> None:
    """★★★ 核心断言：★ 返回值里**必须**有 `readable`（★ 否则两种情况分不开）✓"""
    seg = _seg(MOLD, "mold_evidence")
    assert seg, "★ 找不到 `mold_evidence`"
    assert "'readable'" in seg or '"readable"' in seg, "★ 没有 `readable` 位"
    assert "readable_note" in seg, "★ 没给可读的说明"
    assert "_all_none" in seg, "★ 没有可核的判据（★ 四项 + 两属性全 None）"


def test_capability_keeps_counting_the_same_six_fields() -> None:
    """★★ 契约：★ **六个读数字段一个都不能少**（★ 改了形状会破坏调用方）✓"""
    seg = _seg(MOLD, "mold_evidence")
    for k in ("parting_lines", "parting_surfaces", "cavity_surfaces", "core_surfaces",
              "parting_type", "core_cavity_split"):
        assert k in seg, "★ 少了 `%s`" % k


def test_negative_case_doc_says_it_cannot_read() -> None:
    """★★★ **负例 · 说实话**：★ ToolSpec 的 doc **必须**写明「读不到」 ✓

    ★★ 判据：★ doc 里**不许**只有「Read back …」那种**肯定语气** ——
      ★ 必须**同时**出现「读不到」/「`None`」/「`readable`」这类**如实**说法 ✓
    """
    src = SPEC.read_text(encoding="utf-8", errors="replace")
    i = src.find("solidworks_mold_evidence")
    assert i != -1, "★ 找不到那条 ToolSpec"
    seg = src[i:i + 2600]
    assert "readable" in seg, "★ doc 里没提 `readable`"
    assert ("读不到" in seg) or ("返回全 `None`" in seg), "★ doc 没说「读不到」"


def test_negative_case_does_not_claim_no_parting() -> None:
    """★★★ **负例 · 不许过度解读**：★ 必须写明「读不到 **≠** 没有分型」✓

    ★★ 为什么重要：★ 这正是本条最容易出新错的地方 ——
      ★ 把「我读不到」写成「这个零件没有分型」会**误导使用者**（★ 与事实 40 同族）✓
    """
    seg = _seg(MOLD, "mold_evidence")
    assert "不等于" in seg or "不是" in seg, "★ 没写明「读不到 ≠ 没有分型」"
