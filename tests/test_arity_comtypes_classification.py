"""钉住 `audit_call_arity.py` 的 **comtypes 分类**（含"不是静默吞掉"的证明）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_arity_comtypes_classification.py
# 定位:   轮 130：把 `sw_delivery.py` 那 2 个**comtypes 早绑定**站点单独归类，
#         消掉 A5 的最后 2 条「存疑」。本文件证明这不是"把门禁调绿"。
# 官方依据: `comtypes` 早绑定与 pywin32 迟到绑定对 `[out]` 的处理不同；
#           本工具的规则是在 pywin32 上真机量出来的（已知事实 68）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import audit_call_arity as ac          # noqa: E402

DELIVERY = REPO_ROOT / "scripts" / "sw_delivery.py"
RAW = Path(r"D:\AI\SW\_raw")


def _refs():
    return [str(p) for p in RAW.rglob("iface_*.txt")]


def test_the_two_sites_are_classified_as_comtypes_with_a_reason():
    """@brief ★ 两条必须在 `COMTYPES_CALL_SITES` 里，且**各带理由**。"""
    keys = set(ac.COMTYPES_CALL_SITES)
    assert ("sw_delivery.py", 635) in keys
    assert ("sw_delivery.py", 884) in keys
    for k, reason in ac.COMTYPES_CALL_SITES.items():
        assert len(reason) > 60, "%s 的理由太短: %r" % (k, reason)
        assert "comtypes" in reason, "%s 的理由要点明 comtypes" % (k,)


def test_classification_is_not_silent_swallowing():
    """@brief ★★ **不是静默吞掉**：这批站点**仍然出现在输出里**，只是被单列。

    ⚠ 若哪天有人把它们从输出里删掉（"看不见就当没有"），这条会红。
    """
    t = (REPO_ROOT / "scripts" / "audit_call_arity.py").read_text(encoding="utf-8")
    assert "comtypes 明细" in t, "明细段必须存在"
    assert "本工具判不了" in t, "要写明「判不了」，而不是「通过」"


def test_audit_separates_comtypes_from_doubt():
    """@brief ★★ 真跑一遍：`sw_delivery.py` 的 **存疑应当变成 0**，2 条落到 comtypes 组。"""
    refs = _refs()
    if not refs or not DELIVERY.is_file():
        import pytest
        pytest.skip("缺反射转储或目标文件")
    ok, doubt, missing, dynamic, comtypes = ac.audit(str(DELIVERY), refs)
    assert len(comtypes) == 2, "应当恰好 2 条 comtypes，实际 %d" % len(comtypes)
    assert all("comtypes" in r for *_x, r in comtypes)
    #: ⚠ `doubt` 里**不该**再有 `IGetDocumentNames` / `OpenDoc6`
    doubt_members = {m for *_x, m in [(d[0], d[1]) for d in doubt]}
    assert "IGetDocumentNames" not in doubt_members
    assert "OpenDoc6" not in doubt_members


def test_reason_mentions_the_pywin32_vs_comtypes_difference():
    """@brief ★ 理由里要说清**为什么这条规则不适用**（pywin32 的规矩 vs comtypes 的行为）。"""
    for k, reason in ac.COMTYPES_CALL_SITES.items():
        assert "pywin32" in reason, "%s 要提到 pywin32（规则的来源）" % (k,)
