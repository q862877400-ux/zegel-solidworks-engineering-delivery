"""★ 会话预检的契约与负例（规格 210 · B5-1）：有非我方文档就必须**拒绝开始**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_session.py` 的 `open_documents` / `classify_open_documents` / `precheck_session`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-1/B5-2**。★ 来源：外部评审的判决 ——
#   「不要拦 SolidWorks 的内部写，要守的规则是**它打开的永远不是原件**；★ 真机跑**开始前**
#    枚举已打开的文档，★ 只要有**不是我们打开的**就**拒绝开始**」✓
# 判据:   ★ 官方 `ISldWorks.GetDocuments`（已读该页与官方示例的调用序）；
#   ★★ **判据用回读**：`GetDocumentCount` 与 `GetDocuments` 数组长度**互相校验**，不一致要如实报出 ✓
#   ★★ **保守方向**：路径为空的（新建未存盘）**算非我方**，除非显式 `allow_untitled=True` ✓
# 官方依据: `C:\swapi\types\ISldWorks\GetDocuments.md` + `Get_Paths_of_Open_Documents_Example_VB.md`
#   ★ 并**据官方 Remarks 排除了** `GetFirstDocument`（装配体时它返回首个组件，不是完整枚举）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_session as S                                        # noqa: E402


class _FakeDoc:
    def __init__(self, path="", title=""):
        self._d = {"GetPathName": path, "GetTitle": title}


class _FakeSw:
    """★ 假 COM：只实现预检要用的三个读法（★ 不连 SolidWorks）✓"""

    def __init__(self, docs, count=None):
        self._docs = list(docs)
        self._count = len(self._docs) if count is None else count
        self._map = {"GetDocumentCount": self._count, "GetDocuments": self._docs or None}


@pytest.fixture(autouse=True)
def _patch_com(monkeypatch):
    """★ 把 `get_com_member` 换成「查字典」（★ 与真机同一调用形状，但不碰 COM）✓"""
    def fake_get(obj, member, default=None, *a, **kw):
        if isinstance(obj, dict):
            return obj.get(member, default)
        #: ★ 假文档把读法放在 `_d` 里；★ 假会话放在 `_map` 里 ✓（第一版漏了 `_d` ⇒ 路径全空）
        table = getattr(obj, "_d", None) or getattr(obj, "_map", None)
        if isinstance(table, dict) and member in table:
            return table[member]
        return getattr(obj, member, default)
    monkeypatch.setattr(S, "get_com_member", fake_get)


# ── ① 枚举与回读校验 ──────────────────────────────────────────────────────
def test_open_documents_enumerates_paths_and_titles():
    sw = _FakeSw([_FakeDoc(r"D:\sandbox\a.sldprt", "a"), _FakeDoc(r"D:\sandbox\b.sldasm", "b")])
    snap = S.open_documents(sw)
    assert [d["path"] for d in snap["documents"]] == [r"D:\sandbox\a.sldprt", r"D:\sandbox\b.sldasm"]
    assert snap["count"] == 2 and snap["count_matches"] is True


def test_count_mismatch_is_reported_not_hidden():
    """★★ 回读不一致**必须如实报出** —— ★ 本仓一贯纪律：被调成员的返回值不可信，读数要互相校验 ✓"""
    sw = _FakeSw([_FakeDoc(r"D:\sandbox\a.sldprt", "a")], count=3)
    snap = S.open_documents(sw)
    assert snap["count_matches"] is False
    assert "回读不一致" in snap["readback_problem"], snap


def test_missing_getdocuments_is_reported_as_not_found():
    """★ 拿不到数组 ⇒ ★ 按铁律 5 记「查不到」，★ **不许**静默当成「没有文档」（那会让门禁失效）✓"""
    snap = S.open_documents(_FakeSw([], count=0))
    assert "查不到" in snap["readback_problem"], snap


# ── ② 分类：路径归一化与保守方向 ──────────────────────────────────────────
def test_allowed_paths_match_case_insensitively_and_ignore_trailing_sep():
    docs = [{"path": r"D:\Sandbox\A.sldprt"}, {"path": r"d:\sandbox\b.sldprt"}]
    ours, foreign = S.classify_open_documents(docs, [r"d:\sandbox\a.sldprt", r"D:\sandbox\b.sldprt\\"])
    assert len(ours) == 2 and foreign == [], (ours, foreign)


def test_untitled_document_is_foreign_by_default():
    """★★ 保守方向：★ 路径为空的文档**默认算非我方** —— ★ 因为「没法证明是我们开的」 ✓"""
    docs = [{"path": "", "title": "Part1"}]
    ours, foreign = S.classify_open_documents(docs, [r"D:\sandbox\a.sldprt"])
    assert ours == [] and len(foreign) == 1
    ours2, _ = S.classify_open_documents(docs, [], allow_untitled=True)
    assert len(ours2) == 1


# ── ③ 门禁本身：负例是唯一的证明（事实 62）──────────────────────────────
def test_precheck_refuses_when_a_foreign_document_is_open():
    """★★★ **负例**：会话里开着别人（用户）的文档 ⇒ **必须抛异常拒绝开始** ✓"""
    sw = _FakeSw([_FakeDoc(r"D:\sandbox\ours.sldprt", "ours"),
                  _FakeDoc(r"D:\user\客户件.sldprt", "客户件")])
    with pytest.raises(S.ForeignDocumentError) as exc:
        S.precheck_session(sw, allowed_paths=[r"D:\sandbox\ours.sldprt"])
    assert "拒绝开始" in str(exc.value) and "1" in str(exc.value)


def test_precheck_passes_when_only_our_documents_are_open():
    sw = _FakeSw([_FakeDoc(r"D:\sandbox\ours.sldprt", "ours")])
    info = S.precheck_session(sw, allowed_paths=[r"D:\sandbox\ours.sldprt"])
    assert info["foreign"] == [] and len(info["ours"]) == 1


def test_precheck_passes_on_an_empty_session():
    """★ 空会话（没有文档）⇒ 放行 —— ★ 这是最常见的真机跑起点 ✓"""
    info = S.precheck_session(_FakeSw([]), allowed_paths=[])
    assert info["ours"] == [] and info["foreign"] == []
