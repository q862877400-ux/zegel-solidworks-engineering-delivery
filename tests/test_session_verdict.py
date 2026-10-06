"""★ 会话裁决的契约与负例（规格 210 · B5-2）：一个裁决、两条探路，且**必须报出用的是哪条**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `tools/session_verdict.py`（★ 判定的**唯一之家**，护栏与回收脚本都复用它）
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-2**。★ 外部评审要求"把枚举文档 +
#   区分是否我方 + 读未保存标记**提到一处**"，★ 并点名本仓反复吃过的亏：同一套判定两处各写一份 ✓
# 判据:   ★★ **两条探路、一个裁决**：① COM 路（准，读 `GetPathName` + 官方 `GetSaveFlag`）·
#   ② 窗口标题路（糙，但**COM 已卡死时仍可用** —— ★ 那是回收脚本的真实场景，不是冗余）✓
#   ★★ 裁决**必须报 `path_used`**；★ 两条都探不通时 **`ok=False` 且说清是「探不通」**，
#   不是「会话干净」（★ 这两种的含义完全不同）✓
# 官方依据: `IModelDoc2.GetSaveFlag`（「dirty and needs to be saved」）· `ISldWorks.GetDocuments`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import session_verdict as SV                                    # noqa: E402


class _FakeRun:
    """★ 假 PowerShell 输出（★ 三种形态都覆盖：括号外隔空格、括号内、无标记）✓"""

    stdout = ("1\tTrue\t零件1 [MCP_Test.SLDPRT] *\n"
              "2\tFalse\t[x.sldprt*]\n"
              "3\tTrue\t[y.sldprt]\n"
              "4\tTrue\t客户件 [主轴壳体.sldprt]\n")


@pytest.fixture
def title_mode(monkeypatch):
    monkeypatch.setattr(SV.subprocess, "run", staticmethod(lambda *a, **k: _FakeRun()))
    return SV.title_documents()


# ── ① 标题解析：★ 未保存标记的两种位置都要认 ────────────────────────────
def test_unsaved_marker_inside_brackets():
    assert SV.parse_title_documents("零件1 [a.sldprt*]")[0]["dirty"] is True


def test_unsaved_marker_outside_brackets_with_space():
    """★★ 实测形态 `[...] *` —— ★ 我前两版各漏了一种，两次都把标记丢了（丢失 = 危险方向）✓"""
    assert SV.parse_title_documents("零件1 [a.sldprt] *")[0]["dirty"] is True


def test_no_marker_means_not_dirty():
    d = SV.parse_title_documents("零件1 [a.sldprt]")[0]
    assert d["dirty"] is False and d["title"] == "a.sldprt"


def test_title_parser_reports_no_path():
    """★ 标题路的**已知限度**：拿不到路径 ⇒ ★ 所以「是不是我方」要退回命名约定 ✓"""
    assert SV.parse_title_documents("零件1 [a.sldprt]")[0]["path"] == ""


# ── ② 标题探路与裁决 ─────────────────────────────────────────────────────
def test_title_probe_lists_processes_and_documents(title_mode):
    assert title_mode["usable"] is True and len(title_mode["processes"]) == 4
    assert [d["title"] for d in title_mode["documents"]] == \
        ["MCP_Test.SLDPRT", "x.sldprt", "y.sldprt", "主轴壳体.sldprt"]


def test_verdict_refuses_when_a_foreign_document_is_open(title_mode, monkeypatch):
    """★★ **负例**：标题路认出用户的文档（命名不符）⇒ ★ `ok=False` 且**说清原因** ✓"""
    monkeypatch.setattr(SV, "title_documents", lambda timeout_s=60: title_mode)
    v = SV.session_verdict(prefer="title")
    assert v["ok"] is False and v["path_used"] == "title"
    assert "拒绝开始" in v["why"], v


def test_verdict_reports_unsaved_documents(title_mode, monkeypatch):
    """★ **未保存改动**必须被报出来 —— ★ 它是「能不能安全杀进程/关会话」的依据（评审点名的风险）✓"""
    monkeypatch.setattr(SV, "title_documents", lambda timeout_s=60: title_mode)
    v = SV.session_verdict(prefer="title")
    assert len(v["unsaved"]) == 2, v["unsaved"]


# ── ③ 探不通 ≠ 干净（★ 这是最要紧的负例）────────────────────────────────
def test_verdict_does_not_claim_clean_when_both_paths_fail(monkeypatch):
    """★★★ **两条路都探不通 ⇒ 必须 `ok=False` 并说清「探不通」** ——
    ★ 绝不许静默当成「会话是干净的」（★ 那会让门禁在最需要它的时候失效）✓

    ★ 注意假件必须让**进程在、却读不出**才算「探不通」；
      ★ 而「**根本没有进程**」是另一种情况 —— ★ 那会话必然是空的 ⇒ **应当放行**
      （★ 见下一条测试）✓
    """
    monkeypatch.setattr(SV, "title_documents",
                        lambda timeout_s=60: {"usable": False, "why": "读不出标题",
                                              "processes": [{"pid": 1, "responding": True,
                                                             "title": ""}],
                                              "documents": []})
    v = SV.session_verdict(prefer="title")
    assert v["ok"] is False and v["path_used"] == ""
    assert "查不到" in v["why"] and "停下问人" in v["why"], v


def test_no_solidworks_process_means_clean_and_passes(monkeypatch):
    """★★ **「没在运行」不是「探不通」** —— ★ 没有任何 SLDWORKS 进程 ⇒ 会话必然是空的 ⇒ **放行** ✓

    ★ 为什么单列一条：★ 我第一版把两者混成同一种失败 ⇒ ★ **护栏会拒绝每一次跑**
      （★ 因为探针常常正是要先拉起 SolidWorks 的那些）—— 那等于把门禁写成了**路障** ✓
    """
    monkeypatch.setattr(SV, "title_documents",
                        lambda timeout_s=60: {"usable": False, "why": "没有进程",
                                              "processes": [], "documents": []})
    v = SV.session_verdict(prefer="title")
    assert v["ok"] is True and v["path_used"] == "title" and v["documents"] == []


def test_verdict_always_reports_which_path_was_used(title_mode, monkeypatch):
    """★ 裁决**必须报出用的是哪条路** —— ★ 免得读者以为「糙的那条」也是准的 ✓"""
    monkeypatch.setattr(SV, "title_documents", lambda timeout_s=60: title_mode)
    assert SV.session_verdict(prefer="title")["path_used"] == "title"


def test_reclaim_delegates_to_the_shared_verdict():
    """★★ **判定的家只有一处**：回收脚本的「是不是我方」用的必须是**共用**的正则 ✓"""
    import reclaim_solidworks as R
    assert R._OURS is SV.OURS, "★ 回收脚本又自己写了一份正则 ⇒ 本仓反复吃过的亏"
    mine, others = R._our_own_docs([{"title": "MCP_Test.SLDPRT"}, {"title": "主轴壳体.sldprt"}])
    assert len(mine) == 1 and len(others) == 1


# ── ④ 降级与矛盾（★ 真机查出的漏洞 + 我随后的过度纠正，两条都钉住）────────
def test_com_path_degrades_to_title_instead_of_going_blind(monkeypatch):
    """★★★ **真机查出的静默漏洞**：COM 路的 `GetDocuments` 返回**空**（★ 现场：明明开着文档）⇒
    ★ 当时裁决**照样放行** ✗（★ 门禁瞎着却报「干净」）。

    ★ 正解不是"读不出就拒绝"（★ 那会把门禁变成**路障**，会话干净时也拒）——
    ★ 而是**降级到标题路**并**记明用的是哪条** ✓
    """
    class _P:
        stdout = "1\tTrue\t[零件1]\n"
    monkeypatch.setattr(SV.subprocess, "run", staticmethod(lambda *a, **k: _P()))
    blind = {"usable": True, "why": "", "documents": [],
             "snapshot": {"documents": [], "readback_problem": "GetDocuments 返回空"}}
    monkeypatch.setattr(SV, "com_documents", lambda timeout_s=25: blind)
    v = SV.session_verdict(prefer="com")
    assert v["path_used"] == "title", v
    assert len(v["documents"]) == 1, "★ 降级之后应当看得见那个文档"
    assert "com" in (v.get("tried_paths") or []), v


def test_all_paths_blind_still_refuses_and_says_so(monkeypatch):
    """★ **所有探路都读不出**（且进程在）⇒ ★ 仍然**拒绝**并说清「查不到」，★ 不许说「干净」✓"""
    monkeypatch.setattr(SV, "com_documents",
                        lambda timeout_s=25: {"usable": False, "why": "连不上", "documents": []})
    monkeypatch.setattr(SV, "title_documents",
                        lambda timeout_s=60: {"usable": False, "why": "读不出标题",
                                              "processes": [{"pid": 1, "responding": True,
                                                             "title": ""}],
                                              "documents": []})
    v = SV.session_verdict(prefer="com")
    assert v["ok"] is False and v["path_used"] == ""
    assert "查不到" in v["why"] and "停下问人" in v["why"], v


def test_guard_refuses_when_the_two_rolls_disagree(monkeypatch):
    """★★ **真机现场**：标题路读到 1 个文档、COM 路读到 0 个 ⇒ ★ 两次说法不同 ⇒ **拒绝** ✓

    ★ 理由：★ 两次不一致说明**至少一次是瞎的**，★ 而我们**不知道是哪次** ⇒ 保守不放行 ✓
    """
    import sw_guard as G
    calls = []

    def fake(allowed_paths=(), *, allow_untitled=False, prefer="com", timeout_s=25):
        calls.append(prefer)
        n = 1 if prefer == "title" else 0
        return {"ok": True, "path_used": prefer, "why": "", "documents": [{}] * n,
                "ours": [], "foreign": [], "unsaved": [], "unsaved_unknown": 0}

    monkeypatch.setattr(SV, "session_verdict", fake)
    v = G.precheck_before_run()
    assert v["refused"] is True and "矛盾" in v["why"], v
    assert calls == ["title", "com"], calls
