"""★ 测 C8 台账分叉门禁（`scripts/check_refuted_patterns.py`）—— ★ 含**负例**（事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_refuted_patterns_gate.py
# 定位:   ★ 事实 62：「**一个门禁「写了」不等于它「有效」—— 负例测试是唯一的证明**」⇒
#         ★★ 本测试**必须**有一条负例：★ 把某条的 `anchor_quote` 改成一个**在事实表里不存在**的句子
#           ⇒ ★ **门禁必须 FAIL 并点名那个 id** ✓
#         ★ C8 的判据（`GATE-FINAL.md` 逐字）：
#           「`docs/refuted-patterns.json` 里每条的 `anchor_quote` **必须逐字出现在
#            `docs/known-facts.md` 中**。★ 有一个不命中 ⇒ 失败」
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_refuted_patterns as gate                                    # noqa: E402

PATTERNS = ROOT / "docs" / "refuted-patterns.json"


def test_gate_passes_on_current_tree() -> None:
    """★ 正例：★ 当前仓里的表**应当**通过（★ 10 条全部逐字命中）。"""
    ok, msg = gate.check()
    assert ok, msg


def test_gate_fails_when_anchor_quote_missing() -> None:
    """★★ **负例**（★ 事实 62）：★ 把一条的 `anchor_quote` 改坏 ⇒ **必须 FAIL 并点名 id**。"""
    orig = PATTERNS.read_text(encoding="utf-8")
    try:
        data = json.loads(orig)
        broken_id = data["patterns"][0]["id"]
        data["patterns"][0]["anchor_quote"] = "★ 这句在 known-facts.md 里绝对不存在_xyz"
        PATTERNS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        ok, msg = gate.check()
        assert not ok, "★ 负例**没有**被拦住 ⇒ 门禁抓不到它真正要抓的东西（事实 62）"
        assert broken_id in msg, "★ 报错里应当**点名**那一条 id（★ 否则定位不了）：%r" % msg
    finally:
        PATTERNS.write_text(orig, encoding="utf-8")
    #: ★ 复原后**必须**回到通过（★ 否则测试自己污染了仓）
    ok2, _ = gate.check()
    assert ok2, "★ 负例测试没有把文件复原 ⇒ 它污染了仓"


def test_gate_fails_when_table_missing() -> None:
    """★★ 第二个负例：★ **表不存在**也必须 FAIL —— ★ 那正是 A-3 查出的原始状态 ✓"""
    orig = PATTERNS.read_text(encoding="utf-8")
    try:
        PATTERNS.unlink()
        ok, msg = gate.check()
        assert not ok, "★ 表不存在时门禁**不该**「通过」（★ 事实 40：没有可读对象 ≠ 通过）"
        assert "不存在" in msg, "★ 报错应说清「不存在」：%r" % msg
    finally:
        PATTERNS.write_text(orig, encoding="utf-8")
    ok2, _ = gate.check()
    assert ok2
