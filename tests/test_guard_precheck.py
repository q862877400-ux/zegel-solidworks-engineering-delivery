"""★ 护栏预检的契约与负例（规格 210 · B5-2b）：会话不干净时**不许放行**，且**探针不许被启动**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `tools/sw_guard.py` 的 `precheck_before_run` 与 `run_guarded(precheck=True)`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-2b**。★ 外部评审的设计点原话：
#   「**启动 SolidWorks 之前先问一次、连上之后再问一次**」⇒ ★ 所以要**点名两次**并都留证据 ✓
# 判据:   ★★ **保守方向**：有非我方文档 ⇒ 拒绝；★ 进程在、却两条路都读不出 ⇒ **也拒绝**
#   （★ 「读不到」本身就是要停下问人的理由）；★ 唯一放行例外：**根本没有 SLDWORKS 进程** ✓
#   ★★★ 最强的负例：**拒绝时探针必须**根本没有被启动**（★ 不是「启动了再拦」，那已经晚了）✓
# 官方依据: `IModelDoc2.GetSaveFlag` · `ISldWorks.GetDocuments`（见 `tools/session_verdict.py` 来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_guard as G                                            # noqa: E402
import session_verdict as SV                                    # noqa: E402


def _verdict(ok=True, why="", foreign=0, documents=0, path_used="com"):
    return {"ok": ok, "path_used": path_used, "why": why, "documents": [{}] * documents,
            "ours": [], "foreign": [{}] * foreign, "unsaved": [], "unsaved_unknown": 0}


# ── ① 两次点名都要发生，且都留证据 ──────────────────────────────────────
def test_precheck_rolls_twice_and_records_both(monkeypatch):
    """★★ 评审的设计点：**启动之前问一次、连上之后再问一次** ⇒ ★ 两次都要**留下证据** ✓"""
    calls = []

    def fake(allowed_paths=(), *, allow_untitled=False, prefer="com", timeout_s=25):
        calls.append(prefer)
        return _verdict()

    monkeypatch.setattr(SV, "session_verdict", fake)
    v = G.precheck_before_run()
    assert calls == ["title", "com"], calls
    assert [r["roll"] for r in v["rolls"]] == [1, 2] and v["ok"] is True and v["refused"] is False


# ── ② 保守方向：非我方文档 ⇒ 拒绝 ────────────────────────────────────────
def test_precheck_refuses_on_foreign_document_and_stops_early(monkeypatch):
    """★★ **负例**：第一次点名就发现非我方文档 ⇒ ★ **拒绝**，★ 且**不再问第二次**
    （★ 已经该停了，再连一次 COM 只是多一次风险）✓"""
    calls = []

    def fake(allowed_paths=(), *, allow_untitled=False, prefer="com", timeout_s=25):
        calls.append(prefer)
        if prefer == "title":
            return _verdict(ok=False, why="★ 会话里有 1 个不是我们打开的文档", foreign=1)
        return _verdict()

    monkeypatch.setattr(SV, "session_verdict", fake)
    v = G.precheck_before_run()
    assert v["refused"] is True and v["ok"] is False
    assert calls == ["title"], calls
    assert "不放行" in v["why"]


def test_precheck_refuses_when_session_cannot_be_read(monkeypatch):
    """★ 标题路放行、**COM 路读不出** ⇒ ★ 仍然**拒绝** —— ★ 「连上了却读不到」不许当成「干净」 ✓

    ★ 这里刻意让**第 1 次过、第 2 次不过**：★ 这样才真的走到两次点名。
      ★ 我第一版让两次都不过 ⇒ 第 1 次就停了、断言「第 2 次」自然失败
      ⇒ ★ 是**我的测试写错**，不是代码错 ✓
    """
    def fake(allowed_paths=(), *, allow_untitled=False, prefer="com", timeout_s=25):
        if prefer == "title":
            return _verdict()
        return _verdict(ok=False, why="★ 连上却读不到文档 ⇒ 停下问人")

    monkeypatch.setattr(SV, "session_verdict", fake)
    v = G.precheck_before_run()
    assert v["refused"] is True and "第 2 次" in v["why"], v
    assert len(v["rolls"]) == 2, v["rolls"]


# ── ③ ★★★ 最强的一条：拒绝时探针**根本没被启动** ────────────────────────
def test_refused_precheck_never_spawns_the_probe(monkeypatch):
    """★★★ **负例中的负例**：预检拒绝 ⇒ ★ `subprocess.run` **一次都不许被调用**。

    ★ 为什么这条最要紧：★ 若写成「先启动、再拦」，★ **探针早已经把 SolidWorks 拉起来、
      可能已经打开甚至写了文档** ⇒ ★ 那就不是保护，是**事后告警** ✓
    """
    monkeypatch.setattr(G, "precheck_before_run",
                        lambda *a, **k: {"ok": False, "refused": True, "rolls": [],
                                         "why": "★ 会话不干净"})
    spawned = []
    monkeypatch.setattr(G.subprocess, "run",
                        lambda *a, **k: spawned.append(a) or pytest.fail("★ 探针不该被启动"))
    r = G.run_guarded([sys.executable, "-c", "print(1)"], precheck=True)
    assert r["refused_by_precheck"] is True and r["ok"] is False
    assert spawned == []


def test_precheck_is_off_by_default_so_unit_tests_are_not_slowed(monkeypatch):
    """★ 默认**关**预检（★ 免得每次单测都去起 PowerShell/COM）；★ 由护栏 CLI 显式打开 ✓"""
    called = []
    monkeypatch.setattr(G, "precheck_before_run",
                        lambda *a, **k: called.append(1) or {"refused": False})
    monkeypatch.setattr(G, "Sentinel", lambda *a, **k: type(
        "S", (), {"start": lambda self: self, "stop": lambda self: None,
                  "events": []})())
    monkeypatch.setattr(G.subprocess, "run", lambda *a, **k: type(
        "P", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    G.run_guarded([sys.executable, "-c", "pass"])
    assert called == [], "★ 默认不许跑预检"
