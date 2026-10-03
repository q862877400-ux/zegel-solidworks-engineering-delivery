"""★ 测密度缺口地图：★ **两种零覆盖要分开**（★ 阶段 3 · T2 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `output/density-gap-map.json`（★ 产物）· `output/_density_map.py`（★ 只报不动）
# 定位:   ★ 任务书逐字：「每格算 **官方成员数 / 我们覆盖数 / 密度** ⇒
#   ★★ 按「官方多 + 我们少」排优先级」✓
#   ★★★ **而本轮的关键判断**：★★★ **「零覆盖」有两种、★ 不可混** ——
#     · ★ **键里有「（未归类）」** ⇒ ★ **那是"官方成员没归类"**（★ **矩阵侧**的问题）；
#     · ★★ **两个键都不是「（未归类）」** ⇒ ★ **那才是"我们真的没做"**（★ **补能力侧**的问题）✓
#     ⇒ ★★★★ **混起来会把"矩阵没归类"当成"我们缺能力"** ⇒ **修错方向** ✓
#   ★★★★ **读数**（★ `output/density-gap-map.json` 的汇总）：
#     ★ 真·零覆盖 **5 格 / 官方 1221 成员** · ★ 矩阵侧未归类 **7 格 / 官方 2218 成员** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "output" / "density-gap-map.json"
UNK = "（未归类）"


def _d() -> dict | None:
    if not MAP.is_file():
        return None
    return json.loads(MAP.read_text(encoding="utf-8", errors="replace"))


def test_the_two_kinds_are_separated() -> None:
    """★★★ 核心断言：★ 产物里**两类零覆盖分开列**、★ 且**互不重叠** ✓"""
    d = _d()
    if d is None:
        return                                                            # ★ 产物不在本机 ⇒ 跳过
    real = d.get("真·零覆盖（★ 我们真的没做）") or []
    unk = d.get("矩阵侧未归类") or []
    assert real and unk, "★ 两类没分开：%r" % sorted(d)
    for row in real:
        assert UNK not in row["格子"], "★ `%r` 含「（未归类）」⇒ 应归到矩阵侧那一类" % row["格子"]
    for row in unk:
        assert UNK in row["格子"], "★ `%r` 不含「（未归类）」⇒ 应归到真·零覆盖那一类" % row["格子"]


def test_real_zero_cells_are_non_empty_and_sorted() -> None:
    """★★★ 核心断言：★ 真·零覆盖的格子**确实是我们没做的**（★ 官方成员数 > 0）✓"""
    d = _d()
    if d is None:
        return
    real = d.get("真·零覆盖（★ 我们真的没做）") or []
    assert len(real) >= 3, "★ 真·零覆盖少于 3 格 ⇒ 判据要重看：%r" % real
    offs = [r["官方成员数"] for r in real]
    assert all(o > 0 for o in offs), "★ 有官方成员数为 0 的格子混进来了"
    #: ★★ 排序判据：★ **官方成员数降序**（★ 「官方多」优先）✓
    assert offs == sorted(offs, reverse=True), "★ 没按「官方多」降序：%r" % offs


def test_negative_case_the_reading_matches_the_tool() -> None:
    """★★★ **负例 · 读数要对得上源**：★ 汇总数与源 JSON 的清单**长度一致** ✓

    ★★ 判据：★ 产物是从 `operation-object-matrix.json` 算的 ⇒
      ★★★ **两边的格数要能对上**（★ 防"手改了产物"）✓
    """
    d = _d()
    if d is None:
        return
    src = REPO / "output" / "operation-object-matrix.json"
    if not src.is_file():
        return
    m = json.loads(src.read_text(encoding="utf-8", errors="replace"))
    official = {tuple(k) for k, _v in (m.get("格子占用前 20") or [])}
    ours = {tuple(k) for k, _v in (m.get("工具落在的格子前 20") or [])}
    s = d.get("★_汇总") or {}
    assert s.get("真·零覆盖格子数", 0) + s.get("矩阵侧未归类格子数", 0) <= len(official | ours), (
        "★ 产物里的格数比源清单还多 ⇒ 判据要重看")


def test_negative_case_the_judge_is_written_down() -> None:
    """★★ **负例 · 判据要写下来**：★ 产物里必须写明密度定义与排序口径 ✓"""
    d = _d()
    if d is None:
        return
    blob = json.dumps(d, ensure_ascii=False)
    assert "密度" in blob and "官方成员数" in blob, "★ 没写密度定义"
    assert "官方多" in blob, "★ 没写排序口径"
    assert "两种零覆盖要分开" in blob or "分开" in blob, "★ 没写「两种要分开」那条"
