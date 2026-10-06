"""★ B4 的契约与负例：封闭码集 · 重试门控**不对称** · 重试前比对指纹。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_applicability.py`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B4**。★ 评审的四条判决逐条钉住：
#   ★ ①「工具层返回**结构化**的『不适用』，★ 不要抛字符串异常」⇒ ★ 码集**封闭且小**（6–8 个）✓
#   ★ ②「预检由共享装饰器按 `requires` **自动生成**」✓
#   ★ ③「自动重试**只在静态 ∩ 实证一致时开**；★ 不一致进人工复核，**不用多数决**」✓
#   ★ ④「**重试前先比对指纹** —— 没变才重试；★ 变了**不重试**、先对账」✓
# 判据:   ★★ 三条**负例**必须过：
#     · 码集**封闭** ⇒ 认不出的码**当场报出**（★ 不许悄悄流通）✓
#     · 重试门控**不对称** ⇒ ★ **任一侧存疑就不开**（★ 实证有写/静态有写/静态未知 三种都不开）✓
#     · 指纹**变了 ⇒ 不重试**（★ 哪怕标签说「安全」）✓
# 官方依据: 无 —— ★ 我方编排口径，如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_applicability as AP                                   # noqa: E402


# ── ① 码集：封闭且小，且每个码都能映射到一个动作 ────────────────────────
def test_code_set_is_closed_and_small():
    """★★ 评审要求：★ 码集**必须封闭且小**（6–8 个）⇒ ★ 用测试钉住它**不许长大** ✓"""
    assert 6 <= len(AP.CODES) <= 8, sorted(AP.CODES)
    assert set(AP.CODES) == set(AP.ACTION_MAP), "★ 每个码都要能映射到一个动作"


def test_unknown_code_is_rejected_not_silently_passed():
    """★★ **负例**：★ 不在封闭码集里的码 ⇒ ★ **当场报出**（★ 不许悄悄流通）✓"""
    with pytest.raises(ValueError):
        AP.NotApplicable("something_made_up")


def test_not_applicable_is_structured_not_a_bare_string():
    """★ 评审明确要求：★ **结构化**（★ 编排层要按 `code` 做映射），★ **不是**字符串异常 ✓"""
    d = AP.NotApplicable("missing_selection", needs=["face"], better=["select_by_selector"]).to_dict()
    assert d["not_applicable"] is True and d["code"] == "missing_selection"
    assert d["needs"] == ["face"] and d["better"] == ["select_by_selector"]
    assert d["action_hint"] == AP.CODES["missing_selection"]


# ── ② 重试门控：不对称 ───────────────────────────────────────────────────
def test_retry_gate_is_asymmetric(monkeypatch):
    """★★★ **本规格最要紧的一条 B4 判据**：★ 自动重试**只在静态 ∩ 实证一致时开** ✓

    ★★ 三种「存疑」情形**都必须不开**：★ 实证有写 · 静态有写 · 静态未知 ✓
    """
    #: ★ 假件**显式分支** —— ★ 我第一版用字典查，键与用例名撞了 ⇒ `KeyError` / 取错值 ✗
    def fake_static(name):
        if name == "static_writes_only":
            return ["document"]
        if name == "static_unknown":
            return None
        return []

    def fake_observed(name):
        if name == "observed_writes":
            return ["selection"]
        return None

    #: ★★ 这两行**必须留着** —— ★ 我上一版替换时把它们删了 ⇒ 断言全打在真表上 ✗
    monkeypatch.setattr(AP, "static_writes", fake_static)
    monkeypatch.setattr(AP, "observed_writes", fake_observed)

    assert AP.retry_allowed("both_silent")["allowed"] is True    # ★ 两侧都确认无写 ⇒ 开
    assert AP.retry_allowed("static_writes_only")["allowed"] is False   # ★ 静态有写 ⇒ 不开
    assert AP.retry_allowed("static_unknown")["allowed"] is False       # ★ 静态未知 ⇒ 不开
    assert AP.retry_allowed("observed_writes")["allowed"] is False      # ★ 实证有写 ⇒ 不开


def test_real_findings_are_not_retry_enabled():
    """★ 真机抓到的那两条（★ 实证有写）⇒ ★ **不许**开自动重试 ✓"""
    for name in ("solidworks_assembly_check_interference", "solidworks_motion_create_study"):
        r = AP.retry_allowed(name)
        assert r["allowed"] is False and r["observed"], (name, r)


# ── ③ 运行时保险：重试前比对指纹 ─────────────────────────────────────────
def test_fingerprint_insurance_blocks_retry_when_something_changed():
    """★★ **负例**：★ 指纹**变了** ⇒ ★ **不重试**、先对账（★ 哪怕标签说「安全」）✓"""
    before = {"readings": {"dirty": False, "features": 1, "bodies": 1, "selection": 0},
              "usable": True}
    after = {"readings": {"dirty": True, "features": 2, "bodies": 1, "selection": 0},
             "usable": True}
    r = AP.fingerprint_allows_retry(before, after)
    assert r["retry"] is False and "dirty" in r["changed"], r


def test_fingerprint_insurance_allows_retry_when_nothing_changed_but_admits_blind_spots():
    """★ 指纹没变 ⇒ 允许重试；★★ 但**必须同时报出盲区**（★ 不许把「没看到」说成「没有」）✓"""
    same = {"readings": {"dirty": False, "features": 1}, "usable": True}
    r = AP.fingerprint_allows_retry(same, same)
    assert r["retry"] is True
    assert r.get("caveat"), "★ 必须写明指纹有盲区"


# ── ④ 自动预检：★ 按声明的 inject 生成，★ 作者不手写 ─────────────────────
class _Doc:
    """★ 假文档：只实现 `GetType`（★ 1=零件 · 2=装配体 · 3=工程图）✓"""
    def __init__(self, t):
        self._t = t
    def GetType(self):
        return self._t


def test_precheck_accepts_a_matching_document():
    assert AP.precheck("model", _Doc(1))["kind"] == "part"
    assert AP.precheck("asm_model", _Doc(2))["kind"] == "assembly"
    assert AP.precheck("drawing_model", _Doc(3))["kind"] == "drawing"


def test_precheck_rejects_the_wrong_document_type_with_a_closed_code():
    """★★ **负例**：★ 拿**零件**去跑要**装配体**的工具 ⇒ ★ 必须抛 `wrong_doc_type`，
    ★ 且 `needs` 里写清要什么（★ 编排层据此去建/去换）✓"""
    with pytest.raises(AP.NotApplicable) as e:
        AP.precheck("asm_model", _Doc(1))
    d = e.value.to_dict()
    assert d["code"] == "wrong_doc_type" and d["needs"] == ["assembly"]


def test_precheck_reports_no_document_for_an_empty_host():
    with pytest.raises(AP.NotApplicable) as e:
        AP.precheck("model", None)
    assert e.value.to_dict()["code"] == "no_document"


def test_unbuilt_precheck_says_unchecked_instead_of_pretending():
    """★★ **不许假装查过**：★ `view`/`study`/`cost_manager`/`selection` 的预检**还没建** ⇒
    ★ 必须回 `unchecked: True` 并**写明原因** ✓（★ 与「判不出就写未知」同一条纪律）✓"""
    r = AP.precheck("view", object())
    assert r.get("unchecked") is True and "还没建" in r["why"], r


def test_precheck_tool_reads_the_declaration(tmp_path, monkeypatch):
    """★ `precheck_tool` 从**声明**读 `inject` ⇒ ★ **调用方不用知道**该检查什么 ✓"""
    monkeypatch.setattr(AP, "_table", lambda _p: {"t": {"inject": "asm_model"}})
    with pytest.raises(AP.NotApplicable):
        AP.precheck_tool("t", {"asm_model": _Doc(1)})
    assert AP.precheck_tool("t", {"asm_model": _Doc(2)})["kind"] == "assembly"
