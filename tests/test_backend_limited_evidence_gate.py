"""★ 「后端到不了」名单门禁的**契约与负例**（★ 事实 62）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_backend_limited_evidence_gate.py
# 定位:   ★ 2026-10-03（轮 600）★ `scripts/check_backend_limited_evidence.py` 的负例。
#
#   ★ 证明五件事：
#     ① ★ **能抓到**：某条缺 `section` ⇒ 违规；
#     ② ★ **能抓到**：某条没有 `facts` ⇒ 违规（★ 那正是"写明依据"的那一半）；
#     ③ ★ **能抓到**：`section` 在边界文档里**找不到** ⇒ 违规（★ 依据要能指到真小节）；
#     ④ ★★ **负例**：**空名单** ⇒ 违规（★ 空名单 = 什么都没单列，与任务书矛盾）；
#     ⑤ ★ **负例**：**合法的一条** ⇒ **不该报**（★ 否则门禁太严、会被忽略）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_backend_limited_evidence", R / "scripts" / "check_backend_limited_evidence.py")
GATE = importlib.util.module_from_spec(_spec)
sys.modules["check_backend_limited_evidence"] = GATE
_spec.loader.exec_module(GATE)                                          # type: ignore[union-attr]


def _ok_item(**over):
    base = {"toolbar": "线性阵列", "member": "ILinearPatternFeatureData.AccessSelections",
            "where": "0x80010105", "section": "§2.2.1", "facts": [474], "note": ""}
    base.update(over)
    return base


def test_catches_missing_section():
    """★ 正例：缺 `section` ⇒ 抓到。"""
    bad = GATE.check({"items": [_ok_item(section="")]})
    assert bad, "缺 section 没被抓到"


def test_catches_missing_facts():
    """★ 正例：**没有 `facts`** ⇒ 抓到（★ 那正是"写明依据"的一半）。"""
    bad = GATE.check({"items": [_ok_item(facts=[])]})
    assert bad, "没有 facts 没被抓到 ⇒ 「写明依据」这一半没守"


def test_catches_section_not_in_doc():
    """★ 正例：`section` 在边界文档里**找不到** ⇒ 抓到。"""
    bad = GATE.check({"items": [_ok_item(section="§9.9.9-nonexistent")]})
    assert bad, "section 指不到真小节却没被抓到 ⇒ 依据可以随便写"


def test_negative_empty_list_is_bad():
    """★★ 负例：**空名单** ⇒ 违规（★ 空名单 = 什么都没单列，与任务书矛盾）。"""
    bad = GATE.check({"items": []})
    assert bad, "空名单被放过了 ⇒ 那等于「什么都没单列」"


def test_negative_valid_item_passes():
    """★ 负例：**合法的一条** ⇒ **不该报**（★ 否则门禁太严、会被忽略）。"""
    bad = GATE.check({"items": [_ok_item()]})
    assert not bad, "合法的一条被误报：%r" % (bad,)


def test_real_file_is_clean():
    """★ 真实仓库：★ 当前名单**不该有违规**（★ 轮 599 建的，9 条）。"""
    bad = GATE.check()
    assert not bad, "真实名单有违规：%r" % (bad[:5],)
