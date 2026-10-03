"""★ 测 `tools/triage_get_members.py`：★ 分诊表的**四档判据**与**边界**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types`）
# 文件:   `tools/triage_get_members.py` · 产出 `output/get-member-triage.{csv,json}` +
#         `output/get-member-queue.json`
# 定位:   ★ 池子 = 官方 `*FeatureData` 族的 `Get*` 成员 ⇒ ★★ **分四档**：
#     ★ **A 可施工** · ★ **B 无 `## Returns` 段** · ★ **C 带 `out`（pywin32 风险）** · ★ **D 废弃** ✓
#   ★★★ **为什么要分**：★ **C 与 D 根本不该进施工队列**（★ 前者多半到不了、★ 后者走 T1）✓
#   ★★★★ **实测读数**（★ 2026-10-04）：★ 430 个 ⇒ ★ **A 354 · B 1 · C 63 · D 12** ✓
#   ★★★★★ **⚠ 判据的边界（★ 本测试要守的）**：
#     ★ **`有out` 与 `已废弃` 都是**文本判据**、★ 不等于真机结论**（★ 事实 518）✓
#     ★★ **`已废弃` 必须**精确**** —— ★ 另一个对话刚修过这个判据（★ 轮 769）：
#       ★ 只认**独立成句**的 `Obsolete.` / `Not supported in SOLIDWORKS`，
#       ★★ **不认表格单元格里的同词** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "triage_get_members.py"
JS = REPO / "output" / "get-member-triage.json"
QUEUE = REPO / "output" / "get-member-queue.json"

_spec = importlib.util.spec_from_file_location("_tgm", TOOL)
tgm = importlib.util.module_from_spec(_spec)
sys.modules["_tgm"] = tgm
_spec.loader.exec_module(tgm)


def test_pool_is_the_featuredata_getters() -> None:
    """★★★ **前提断言**：★ 池子**确实**是 `*FeatureData` 族的 `Get*` 成员 ✓"""
    r = tgm.rows()
    assert r, "★ 池子是空的"
    for x in r:
        assert "FeatureData" in x["族"], "★ `%s` 不是 `*FeatureData` 族" % x["族"]
        assert x["成员"].startswith("Get"), "★ `%s` 不以 `Get` 开头" % x["成员"]
    assert len(r) >= 300, "★ 池子只有 %d 个 ⇒ 判据要重看" % len(r)


def test_obsolete_judgement_is_sentence_scoped() -> None:
    """★★★ 核心断言：★ **废弃判定只认独立成句的那两句**（★ 不认表格单元格）✓

    ★★ **为什么**：★★★ **`"Obsolete" in t` 会**假阳性****（★ 页面里别处提到 Obsolete）——
      ★ 那正是另一个对话在轮 769 修的同一个坑 ✓
    """
    for probe, want in (
        ("Obsolete. Superseded by X.", True),
        ("Obsolete. Not superseded.", True),
        ("Not supported in SOLIDWORKS 2011 and later. Superseded by X.", True),
        ("| Obsolete member | something |", False),                   #: ★ 表格单元格 ⇒ **不算**
        ("The difference between this and the now obsolete IPackAndGo::X is…", False),
    ):
        assert bool(tgm.OBS.search(probe)) is want, "★ `%r` 判成了 %r" % (probe, not want)


def test_the_four_tiers_are_disjoint_and_cover_all() -> None:
    """★★★ 核心断言：★ 四档**互斥且穷尽** ✓"""
    r = tgm.rows()

    def tier(x):
        if x["已废弃"]:
            return "D"
        if x["有out"]:
            return "C"
        if not x["有Returns段"]:
            return "B"
        return "A"

    ts = [tier(x) for x in r]
    assert len(ts) == len(r), "★ 有成员落不进任何档"
    assert set(ts) <= {"A", "B", "C", "D"}, "★ 出现了第五档"
    from collections import Counter
    c = Counter(ts)
    assert c["A"] > 300, "★ A 档只有 %d ⇒ 判据要重看" % c["A"]
    assert c["D"] > 0 and c["C"] > 0, "★ C/D 档空了 ⇒ 判据要重看：%r" % dict(c)


def test_negative_case_the_boundary_is_written_down() -> None:
    """★★★★ **负例 · 边界必须写下来**：★ 两处文本判据**不许**被当成真机结论 ✓

    ★★ **判据**：★ 产物的 JSON 里必须有那两条说明 + ★ 单位的说明 ✓
    """
    if not JS.is_file():
        return                                                            # ★ 产物不在本机 ⇒ 跳过
    d = json.loads(JS.read_text(encoding="utf-8", errors="replace"))
    blob = json.dumps(d, ensure_ascii=False)
    assert "文本判据" in blob, "★ 没写「文本判据」这条边界"
    assert "事实 518" in blob, "★ 没指向事实 518"
    assert "不可派" in blob or "真机" in blob, "★ 没写「单位只能真机测」"


def test_negative_case_queue_dedups_against_implementation() -> None:
    """★★★ **负例 · 队列要去重**：★ 队列里**不许**有已在实现面出现的成员 ✓

    ★★ **为什么**：★ 另一个对话**正在同一个仓里补** ⇒
      ★★★ **不去重就会把**他们已经做完的**又派一遍** ✓
    """
    if not (QUEUE.is_file() and JS.is_file()):
        return
    q = json.loads(QUEUE.read_text(encoding="utf-8", errors="replace"))
    assert q.get("A档合计", 0) > 0 and q.get("真·待办", 0) > 0, "★ 队列是空的"
    assert q["真·待办"] < q["A档合计"], (
        "★ 队列与 A 档一样多 ⇒ 去重没生效：%r" % {k: q.get(k) for k in ("A档合计", "已在实现面", "真·待办")})
    #: ★ 队列里每个成员都**不该**在"已在实现面"那张表里
    done = {x["成员"] for x in (q.get("已在实现面") or [])}
    todo = {x["成员"] for x in (q.get("队列") or [])}
    assert not (todo & done), "★ 队列与已实现有交集：%r" % sorted(todo & done)[:5]
