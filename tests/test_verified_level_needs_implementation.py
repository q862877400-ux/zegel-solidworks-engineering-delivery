"""★ 测「标了 `verified` 的能力**必须真有能力层实现**」（★ `JUDGE-A_B` 🔴 的深层发现 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `capabilities.yaml` · `scripts/` `subskills/` `mcp-server/` 的实现面
# 定位:   ★ 起点是 `JUDGE-A_B.md` 的 🔴 **A-drawing 一**（★ evidence 是**循环自证**）——
#   ★★ **而顺着它往下核，发现的是更重的事**：★ 该条目自己的 `limitations[0]` 早就记着
#     「★ **核了实现在哪 —— 结论是「实现层没有对应函数」**」✓
#   ⇒ ★★★ **即：★ 一条 `level: verified` 的能力、★ 能力层**零实现**** ✓
#   ★★★★ **本测试守的就是这件事**：★★★ **`verified` 必须**至少有一个**非签名的实现痕迹** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: ★★ **签名索引**（★ 它们只是名字表、**不算实现**）—— ★ 与事实 518 那条同族 ✓
SIGNATURE_ONLY = {"sw_api_sldworks.py", "sw_api_sldcostingapi.py", "sw_api_SWRoutingLib.py"}


def _implementation_text() -> str:
    """★ 实现面的文本（★ **排除签名索引**）。"""
    out = []
    for d in ("scripts", "subskills", "mcp-server"):
        for f in (REPO / d).rglob("*.py"):
            if f.name in SIGNATURE_ONLY:
                continue
            out.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(out)


def test_drawing_dimension_is_downgraded() -> None:
    """★★★ 核心断言：★ `drawing_dimension_insertion` **不许**再是 `verified` ✓

    ★★ 因为它**能力层零实现** —— ★ 全仓搜 `AddDimension` / `InsertDimension`
      命中的**只有** ARITY 表（★ 那是签名索引）✓
    """
    d = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))
    c = [x for x in d["capabilities"] if x.get("id") == "drawing_dimension_insertion"]
    assert c, "★ 条目没了"
    assert c[0]["level"] != "verified", (
        "★ 又变回 `verified` 了 —— ★ 而它没有实现层（★ 见它的 limitations[0]）")


def test_drawing_dimension_has_no_unattended() -> None:
    """★★★ 核心断言：★ 降级后**不许**留 `unattended` ✓

    ★★ 判据：★ **没有实现的东西不能无人值守** ✓（★ 与 `assembly_and_mates` 同一纪律）
    """
    d = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))
    c = [x for x in d["capabilities"] if x.get("id") == "drawing_dimension_insertion"][0]
    assert "unattended" not in (c.get("allowed_modes") or []), (
        "★ 它还允许无人值守 ⇒ 会真去跑一个没有实现的东西")


def test_negative_case_no_insert_model_dimensions_anywhere() -> None:
    """★★★ **负例**：★ 实现面里**仍然没有** `InsertModelDimensions`（★ 确认降级是对的）✓

    ★★★★ **判据要精确**（★ 值记）：★ `AddDimension2` **确实有实现** ——
      它在 `scripts/sw_part.py` L768（★ 那是**零件上**的尺寸标注 `solidworks_add_dimension`）✓
      ★★ **而 `drawing_dimension_insertion` 要的是**工程图上**的模型尺寸插入** ⇒
      ★★★ 那是**另一个成员** `InsertModelDimensions` ⇒ ★ **本判据只盯它** ✓
      ★★★★ **⇒ 可复用判据**：★★★ **判「有没有实现」时，名字要精确到**那件事的那个成员** ——
        ★ 用"看起来同族"的名字会**误判成"已经做了"** ✓
    """
    impl = _implementation_text()
    assert "InsertModelDimensions" not in impl, (
        "★ 实现面里出现了 `InsertModelDimensions` ⇒ ★ 能力可能已经做了 ⇒ 请复核本测试的前提")


def test_negative_case_add_dimension2_does_exist_but_for_parts() -> None:
    """★★ **负例 · 别把两件事混起来**：★ `AddDimension2` 在 `sw_part.py`（★ **零件**那条）✓"""
    src = (REPO / "scripts" / "sw_part.py").read_text(encoding="utf-8", errors="replace")
    assert "AddDimension2(" in src, (
        "★ 零件那条尺寸标注没了 ⇒ 本测试的分辨点要重看")


def test_negative_case_the_historical_note_is_kept() -> None:
    """★★ **负例 · 补正而不删除**：★ 那条「实现层没有对应函数」的历史记录**必须**还在 ✓"""
    d = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))
    c = [x for x in d["capabilities"] if x.get("id") == "drawing_dimension_insertion"][0]
    blob = " ".join(str(x) for x in (c.get("limitations") or []))
    assert "实现层没有对应函数" in blob, "★ 把那条历史记录删了 ⇒ 应「补正而不是删除」"
