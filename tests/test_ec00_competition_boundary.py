"""★ EC00 残留 ④ 判据 —— 双客户端 COM 竞争的**永久边界**必须写死且有据。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/acceptance/residual-04-competition-boundary.md`
#         `output/_probe_t027_mutex.json`（★ 真机互斥读数）
#         `C:\swprojects\Slacker-LLC\README.md`（★ **Apache-2.0** ⇒ 可引）
#         `AGENTS.md` §〇（★ 已知事实 24）· 铁律 2（★ COM 是 STA）
# 定位:   ★ 清 **EC00 残留 ④**。★★★ **判据**：★ 永久边界**有据**、★ **不能**用「跑一次试试」、
#         ★ 结论是 **`blocked`（有据）** 而**不是** `not_run`。
# 官方依据: 见上
# 许可:   本仓库 MIT。★ 引用的 `Slacker-LLC` 是 **Apache-2.0**（★ 仅引 README 一句，★ 未抄代码）。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"
BOUNDARY = SPEC / "acceptance" / "residual-04-competition-boundary.md"
MUTEX_PROBE = ROOT / "output" / "_probe_t027_mutex.json"
SLACKER_README = Path(r"C:\swprojects\Slacker-LLC\README.md")


def test_boundary_doc_exists_and_cites_the_deadlock_quote():
    """★★★ 残留 ④：★ 永久边界必须**逐字引**那条死锁依据（★ 不能只说「会死锁」）。"""
    assert BOUNDARY.is_file(), "★ 缺 `acceptance/residual-04-competition-boundary.md`"
    body = BOUNDARY.read_text(encoding="utf-8", errors="replace")
    #: ★★ **归一化空白后**比对（★ 原文在 `Two` 后有**排版换行** ⇒ 逐字比对要先归一）
    flat = " ".join(body.split())
    assert ("Two clients driving the same session at once will deadlock it" in flat), (
        "★★ 边界文档里没有**逐字**引那条死锁依据")
    #: ★★ 且必须标明**来源与许可**（★ Apache-2.0 ⇒ 可引）
    assert "Slacker-LLC" in body and "Apache-2.0" in body, (
        "★★ 引文没标来源与许可 ⇒ ★ 违反铁律 6")


def test_the_cited_quote_actually_exists_in_the_source():
    """★★★★★ 残留 ④：★ 引文必须**真的在**源文件里（★ 防我编一句）。

    ★★ 这是**引文的判据** —— ★ 与**事实 62**「门禁写了 ≠ 有效」同族：
      ★ 引一句不存在的话，★ 比不引更糟。
    ★★ **归一化空白后**比对（★ 源文件在 `Two` 后有排版换行）。
    """
    if not SLACKER_README.is_file():
        import pytest
        pytest.skip("★ 只读对照仓不在本机 ⇒ 引文无法复核（★ 如实跳过，不假绿）")
    src = " ".join(SLACKER_README.read_text(encoding="utf-8", errors="replace").split())
    assert "Two clients driving the same session at once will deadlock it" in src, (
        "★★★ 引文**不在源文件里** ⇒ ★ 要么引错了、要么源变了")


def test_boundary_forbids_the_unsafe_reproduction():
    """★★★ 残留 ④：★ 必须**写明**「不能跑一次试试」及其**代价**（★ 不是「懒得验」）。"""
    body = BOUNDARY.read_text(encoding="utf-8", errors="replace")
    assert "不故意破坏用户会话" in body, "★ 没引 T027 的那条禁令"
    assert "死锁" in body, "★ 没说清代价是死锁"
    #: ★★ 必须点出**两个后果**（★ 强杀丢工作 / 等待挂死）
    assert "未保存" in body or "丢" in body, "★ 没说「会丢用户未保存的工作」"


def test_boundary_records_what_was_verified_instead():
    """★★★ 残留 ④：★ 必须记**改验了什么**（★ 且那是**能验的**部分）。"""
    body = BOUNDARY.read_text(encoding="utf-8", errors="replace")
    assert "CreateMutexW" in body, "★ 没写互斥是**命名 Mutex**（跨进程）"
    assert "serialized" in body or "enter:A" in body, "★ 没记真机的**串行**读数"
    #: ★★ 真机读数必须**真的**说串行
    assert MUTEX_PROBE.is_file(), "★ 缺互斥真机读数"
    d = json.loads(MUTEX_PROBE.read_text(encoding="utf-8"))
    assert d.get("serialized") is True, "★★ 真机读数里 `serialized` 不是 True"
    assert d.get("no_interleave") is True, "★★ 真机读数里 `no_interleave` 不是 True"


def test_conclusion_is_blocked_not_not_run():
    """★★★★★ 残留 ④：★ 结论必须是 **`blocked`（有据）**，★ **不是** `not_run`。

    ★★ 区别（★ 边界文档 §四 逐字）：
      · `blocked` = ★ **做了能做的，剩下的无安全条件**
      · `not_run` = ★ **没开始**
    """
    body = BOUNDARY.read_text(encoding="utf-8", errors="replace")
    assert "`blocked`" in body, "★ 边界没写明结论是 `blocked`"
    assert "`not_run`" in body, "★ 边界没区分 `not_run`"
    #: ★★ 且必须写明**永久**不做（★ 不是「下一轮做」）
    assert "永久" in body, "★★ 边界没写「永久不做」⇒ ★ 接手方会重走"
    #: ★★ 以及 EC04 的分工
    assert "EC04" in body, "★ 没写明「节点级租约属 EC04」"


def test_t027_acceptance_links_to_this_boundary():
    """★★ 残留 ④：★ T027 的验收必须**指回**这条边界（★ 单一事实源）。"""
    t027 = SPEC / "acceptance" / "T027-recovery.md"
    assert t027.is_file(), "★ 缺 `acceptance/T027-recovery.md`"
    body = t027.read_text(encoding="utf-8", errors="replace")
    assert "residual-04" in body or "永久边界" in body, (
        "★ T027 的验收没指回永久边界文档 ⇒ ★ 两处会漂移")
