"""★ 一次性：把"读不到"变成"大声拒绝"（★ 修 B5-1/B5-2b 的静默漏洞）。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

# ── ① session_verdict：探路"读不出"时不许放行 ────────────────────────────
p = ROOT / "tools/session_verdict.py"
s = p.read_text(encoding="utf-8")

OLD = """        unsaved = [d for d in docs if (d or {}).get("dirty") is True]
        return {
            "ok": not foreign,"""
NEW = """        unsaved = [d for d in docs if (d or {}).get("dirty") is True]
        #: ★★★ 2026-10-06 **真机查出的静默漏洞**（★ 这是本规格最值钱的一条修正）：
        #:   ★ 现场：SolidWorks **明明开着一个文档**，而 COM 路的 `GetDocuments` 返回**空** ⇒
        #:     `count=None · 文档数=0`，★ 而当时的裁决**照样放行** ✗✗
        #:   ⇒ ★★ 那就是「**一个存在但没人用的守卫**」的同类：★ **它瞎着，却报"干净"** ✓
        #:   ★ 判据改法：★ **只要读过之后仍然"读不出文档"**（`readback_problem` 非空）
        #:     且**一个文档都没读到** ⇒ ★ **不许放行** —— ★ 读不到 ≠ 没有 ✓
        problem = str((probe.get("snapshot") or {}).get("readback_problem") or "")
        if not docs and problem:
            return {
                "ok": False, "path_used": path, "documents": [], "ours": [], "foreign": [],
                "unsaved": [], "unsaved_unknown": 0,
                "why": "★★ 这条路**读不出已打开的文档** ⇒ 拒绝放行（★ 读不到 ≠ 没有）：%s" % problem,
            }
        return {
            "ok": not foreign,"""
assert OLD in s, "session_verdict 的返回块没匹配上"
s = s.replace(OLD, NEW)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① session_verdict 已改成「读不出 ⇒ 拒绝」")

# ── ② precheck_before_run：两次点名**互相矛盾** ⇒ 拒绝 ──────────────────
g = ROOT / "tools/sw_guard.py"
gs = g.read_text(encoding="utf-8")
OLD2 = """        if not v.get("ok"):
            return {"ok": False, "refused": True, "rolls": rolls,
                    "why": "★ 第 %d 次点名（%s）不放行：%s" % (roll, label, v.get("why") or "")}
    return {"ok": True, "refused": False, "rolls": rolls, "why": ""}"""
NEW2 = """        if not v.get("ok"):
            return {"ok": False, "refused": True, "rolls": rolls,
                    "why": "★ 第 %d 次点名（%s）不放行：%s" % (roll, label, v.get("why") or "")}
    #: ★★★ **两次点名不一致 ⇒ 也拒绝**（★ 真机现场：标题路读到 1 个文档、COM 路读到 0 个 ⇒
    #:   ★ 当时**放行了** ✗）—— ★ 两次说法不同，说明**其中一次瞎了**；★ 我们不知道是哪次 ✓
    #:   ⇒ ★ 保守做法：★ **不放行**，把两次读数都交回给人看 ✓
    counts = [r["documents"] for r in rolls]
    if len(set(counts)) > 1:
        return {"ok": False, "refused": True, "rolls": rolls,
                "why": "★★ 两次点名**互相矛盾**（文档数 %s）⇒ 至少一次是瞎的 ⇒ 拒绝放行 ✓"
                       % "、".join(str(c) for c in counts)}
    return {"ok": True, "refused": False, "rolls": rolls, "why": ""}"""
assert OLD2 in gs, "precheck 的返回块没匹配上"
gs = gs.replace(OLD2, NEW2)
g.write_text(gs, encoding="utf-8")
ast.parse(gs)
print("② precheck 已加「两次点名矛盾 ⇒ 拒绝」")
