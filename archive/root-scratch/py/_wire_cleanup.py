"""★ 一次性：把"跑完关掉我方文档"接进护栏，并给它加契约/负例测试。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

# ── ① 护栏：跑完收尾（★ 接在 collect 之后）────────────────────────────────
g = ROOT / "tools/sw_guard.py"
gs = g.read_text(encoding="utf-8")
OLD = """            try:
                import sw_sandbox as _sb
                print("   （沙盒：%s · 输出根：%s）" % (_sb.sandbox_root(), _sb.output_root()))
            except Exception:                                          # noqa: BLE001
                pass"""
NEW = """            try:
                import sw_sandbox as _sb
                print("   （沙盒：%s · 输出根：%s）" % (_sb.sandbox_root(), _sb.output_root()))
            except Exception:                                          # noqa: BLE001
                pass
            #: ★★ **收尾**（规格 210 · B5）：★ 关掉**我方**打开的文档 ——
            #:   ★ 不这么做，下一次预检就会把**上一次留下的我方件**判成"非我方" ⇒
            #:   ★★ **门禁把自己人挡在门外**（★ 真机现场就是这样）✓
            #:   ★★ 只关我方的；★ **有非我方文档就整体停手**（★ 一个都不碰）✓
            if not args.skip_doc_cleanup:
                try:
                    import close_our_docs as _cd
                    r = _cd.close_our_documents()
                    if r["closed"]:
                        print("── 收尾：关掉我方文档 %s ──" % "、".join(r["closed"]))
                    if r["refused"]:
                        print("── 收尾：**没动任何文档**（%s）──" % r["why"])
                except Exception as exc:                                # noqa: BLE001
                    print("── 收尾关文档失败（★ 不影响结论）：%s ──" % type(exc).__name__)"""
assert OLD in gs
gs = gs.replace(OLD, NEW)
gs = gs.replace('    ap.add_argument("--skip-sandbox-collect", action="store_true",',
                '    ap.add_argument("--skip-doc-cleanup", action="store_true",\n'
                '                    help="★ 跑完不关我方文档（★ 默认会关；★ 有非我方文档时本来就不碰）")\n'
                '    ap.add_argument("--skip-sandbox-collect", action="store_true",')
g.write_text(gs, encoding="utf-8")
import ast
ast.parse(gs)
print("① 护栏已接收尾步骤")

# ── ② 测试：契约 + 两条负例 ───────────────────────────────────────────────
t = ROOT / "tests" / "test_close_our_docs.py"
t.write_text('''"""★ 关掉我方文档的契约与负例：★ 只关我方的，有别人的就一个都不碰。"""
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
''', encoding="utf-8")
ast.parse(t.read_text(encoding="utf-8"))
print("② 测试已写")
