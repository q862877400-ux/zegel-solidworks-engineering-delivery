"""★ 关掉我方文档的契约与负例：★ 只关我方的，有别人的就一个都不碰。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `tools/close_our_docs.py`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5 收尾那一半**。★ 真机起因：
#   ★★ 探针留下一个我方未保存件 ⇒ ★ 下一次预检把它判成「非我方」⇒ **门禁把自己人挡在门外** ✗
#   ★ 根因不是门禁错，★ 是**我没收尾**（★ 本仓纪律：「收尾必做 …… 关掉自己开的文档」）✓
# 判据:   ★★ **两条负例**：★ 有非我方文档 ⇒ **一个都不许碰**（连我方的也不关）·
#   ★ 我方多个 ⇒ 全关且**不保存** ✓
# 官方依据: `ISldWorks.CloseDoc(Name)`（已读页面）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import close_our_docs as CD                                     # noqa: E402
import session_verdict as SV                                    # noqa: E402


class _Sw:
    def __init__(self):
        self.calls = []
    def CloseDoc(self, name):
        self.calls.append(name)


def _titles(monkeypatch, names):
    monkeypatch.setattr(SV, "title_documents",
                        lambda timeout_s=60: {"usable": bool(names),
                                              "processes": [{"pid": 1, "responding": True,
                                                             "title": "t"}] if names else [],
                                              "documents": [{"path": "", "title": n,
                                                             "dirty": True} for n in names]})


def test_closes_only_our_documents(monkeypatch):
    _titles(monkeypatch, ["零件1", "MCP_Thing"])
    sw = _Sw()
    r = CD.close_our_documents(connect=sw)
    assert sorted(r["closed"]) == ["MCP_Thing", "零件1"] and r["refused"] is False
    assert sw.calls, "★ 应当真的调了 CloseDoc"


def test_never_touches_anything_when_a_foreign_document_is_open(monkeypatch):
    """★★★ **负例**：会话里混着**非我方**文档 ⇒ ★ **一个都不许碰**（★ 连我方的也不关）✓"""
    _titles(monkeypatch, ["零件1", "客户件"])
    sw = _Sw()
    r = CD.close_our_documents(connect=sw)
    assert r["refused"] is True and r["closed"] == []
    assert sw.calls == [], "★★ 有别人的文档时碰了会话：%s" % sw.calls
    assert "非我方" in r["why"]


def test_no_documents_is_a_noop(monkeypatch):
    _titles(monkeypatch, [])
    sw = _Sw()
    r = CD.close_our_documents(connect=sw)
    assert r["closed"] == [] and r["refused"] is False and sw.calls == []
