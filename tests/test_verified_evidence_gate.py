"""★ A4 门禁的**契约与负例**（★ 事实 62：门禁"写了"不等于"有效"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_verified_evidence_gate.py
# 定位:   ★ 2026-10-03（轮 594）★ `scripts/check_verified_evidence.py` 的负例。
#
#   ★ 证明四件事：
#     ① ★ **能抓到**：`verified` 而无 `evidence` ⇒ 违规；
#     ② ★ **`evidence` 存在但全是空串** ⇒ **也算违规**（★ 空串不是证据）；
#     ③ ★ **`level` 不是 `verified`** 的条目 ⇒ **不该被管**（★ 不越界）；
#     ④ ★ **可核性只提示不拦**（★ 口述证据也可能是证据）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_verified_evidence", R / "scripts" / "check_verified_evidence.py")
GATE = importlib.util.module_from_spec(_spec)
sys.modules["check_verified_evidence"] = GATE
_spec.loader.exec_module(GATE)                                          # type: ignore[union-attr]


def test_catches_verified_without_evidence():
    """★ 正例：`verified` 而没有 `evidence` ⇒ **必须抓到**。"""
    bad, _w = GATE.check([{"id": "x", "level": "verified"}])
    assert bad, "verified 无 evidence 没被抓到 ⇒ 门禁失效"


def test_catches_verified_with_empty_strings():
    """★ 正例：`evidence` 存在但**全是空串** ⇒ 也算违规。"""
    bad, _w = GATE.check([{"id": "x", "level": "verified", "evidence": ["", "   "]}])
    assert bad, "evidence 全是空串没被抓到 ⇒ 空串被当成了证据"


def test_non_verified_is_out_of_scope():
    """★★ 负例：`level` 不是 `verified` 的 ⇒ **不该被管**（★ 不越界）。"""
    for lv in ("source_verified", "stitched", "indexed", "not_implemented"):
        bad, _w = GATE.check([{"id": "x", "level": lv}])
        assert not bad, "%s 被误判（★ 本门禁只管 verified）" % lv


def test_evidence_not_a_list_is_caught():
    """★ 正例：`evidence` 形状不对（不是列表）⇒ 抓到。"""
    bad, _w = GATE.check([{"id": "x", "level": "verified", "evidence": "一句话"}])
    assert bad, "evidence 不是列表没被抓到"


def test_citable_is_warn_only():
    """★ 负例：★ **可核性只提示、不拦**（★ 口述证据也可能是证据）。"""
    bad, warn = GATE.check([{"id": "x", "level": "verified",
                             "evidence": ["2026-10-03 真机建成，走 sw_guard，零弹窗"]}])
    assert not bad, "没有可核文件名的证据被拦了 ⇒ 太严（★ 应与实测一致）"
    assert warn, "没有可核文件名的证据没进提示 ⇒ 提示那一路失效"


def test_real_tree_is_clean():
    """★ 真实仓库：★ **当前不该有违规**（★ 轮 594 实测：95 条 verified、0 条无 evidence）。"""
    bad, _w = GATE.check()
    assert not bad, "仓库里有 verified 而无证据的条目：%r" % (bad[:5],)
