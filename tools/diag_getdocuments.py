"""★ 诊断：`ISldWorks.GetDocuments` / `GetDocumentCount` 到底怎么调才拿得到值。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性诊断脚本）
# 文件:   tools/diag_getdocuments.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2 收口第 4 条**。★ 起因：
#   ★★ 真机现场 —— SolidWorks **明明开着文档**，而 `sw_session.open_documents` 读出
#     `count=None · 文档数=0` ⇒ ★ 于是 B5 的 COM 路**瞎着**，门禁一度"瞎着放行" ✗
#   ⇒ ★ 本脚本**只读**：把各种调用形状都试一遍，看**哪种拿得到值** ✓
# 判据:   ★ 官方签名（已读）：`ISldWorks.GetDocuments()` ⇒ "Array of open documents"；
#   ★ `ISldWorks.GetDocumentCount()` ⇒ 数量 ✓
#   ★ 本脚本**不推断根因**，只**列出实测**：★ 哪种形状回什么、抛什么 ✓
# 官方依据: `C:\swapi\types\ISldWorks\GetDocuments.md` · `GetDocumentCount.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _show(label, fn):
    try:
        v = fn()
    except Exception as exc:  # noqa: BLE001
        print("  %-46s ⇒ ★ 抛 %s: %s" % (label, type(exc).__name__, str(exc)[:70]))
        return None
    t = type(v).__name__
    if v is None:
        print("  %-46s ⇒ None" % label)
    elif isinstance(v, (list, tuple)):
        print("  %-46s ⇒ %s(len=%d)" % (label, t, len(v)))
    else:
        print("  %-46s ⇒ %s = %r" % (label, t, str(v)[:60]))
    return v


def main() -> int:
    import sw_connect

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    print("连上 =", sw is not None)
    if sw is None:
        return 2

    print("\n★ A 组：直接调（pywin32 迟到绑定）")
    _show("sw.GetDocumentCount()", lambda: sw.GetDocumentCount())
    _show("sw.GetDocuments()", lambda: sw.GetDocuments())

    print("\n★ B 组：先取属性再调（有些成员是 property）")
    _show("getattr(sw,'GetDocuments') 不调用", lambda: getattr(sw, "GetDocuments"))
    _show(
        "getattr(sw,'GetDocumentCount') 不调用", lambda: getattr(sw, "GetDocumentCount")
    )

    print("\n★ C 组：用本仓的 get_com_member（★ 无实参 ⇒ 先无参调一次）")
    import sw_connect as SC

    _show(
        "get_com_member(sw,'GetDocumentCount')",
        lambda: SC.get_com_member(sw, "GetDocumentCount"),
    )
    _show(
        "get_com_member(sw,'GetDocuments')",
        lambda: SC.get_com_member(sw, "GetDocuments"),
    )

    print("\n★ D 组：枚举回读（★ 独立读数，用来判 A/B/C 谁对）")
    _show("sw.GetFirstDocument()", lambda: sw.GetFirstDocument())
    _show("sw.ActiveDoc", lambda: sw.ActiveDoc)

    print("\n★ E 组：窗口标题（★ 不碰 COM 的那条路，作为对照）")
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from session_verdict import title_documents

        td = title_documents()
        print(
            "  title_documents ⇒ usable=%s · 文档 %s"
            % (td["usable"], [d["title"] for d in td["documents"]])
        )
    except Exception as exc:  # noqa: BLE001
        print("  title_documents ⇒ 抛 %s" % type(exc).__name__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
