"""★ 一次性：调用**没调成**时不许报 agree/conservative（★ 那是假一致）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

OLD = '''def classify(declared_writes, diff, usable) -> str:
    """★★ 四类判定（★ 严格照 spec：`missed` 与 `undecided` **不许混**）✓"""
    if not usable or diff["unknown"]:
        return "undecided"'''
NEW = '''def classify(declared_writes, diff, usable, *, call_ok: bool) -> str:
    """★★ 四类判定（★ 严格照 spec：`missed` 与 `undecided` **不许混**）✓

    ★★★ 2026-10-06 **跑写工具之前必须先修的一处假结论**：★ 若那次调用**根本没调成**
      （★ 例如写工具缺前置）⇒ ★ 指纹当然不会变 ⇒ ★★ 而只指纹判定会报 **`agree`**
      ⇒ ★ **那是「假一致」**：★ 我们**根本没测到它**（★ 与事实 57「一直是绿的，
      ★ 可能只是环境恰好满足」同族）✓
    ⇒ ★ 判序把 `call_ok` 放**最前**：★ **没调成 ⇒ `undecided`**（★ 并记明原因）✓
    """
    if not call_ok:
        return "undecided"
    if not usable or diff["unknown"]:
        return "undecided"'''
assert OLD in s, "classify 没匹配上"
s = s.replace(OLD, NEW)

OLD2 = """        verdict = classify(table[name].get("writes"),
                           {"changed": diff["changed"], "unknown": diff["unknown"]},
                           bool(before.get("usable")) and bool(after.get("usable")))"""
NEW2 = """        verdict = classify(table[name].get("writes"),
                           {"changed": diff["changed"], "unknown": diff["unknown"]},
                           bool(before.get("usable")) and bool(after.get("usable")),
                           call_ok=bool(ok))"""
assert OLD2 in s, "调用点没匹配上"
s = s.replace(OLD2, NEW2)

#: ★ 统计里把"没调成"单列（★ 它是**我们没测到**，不是被测对象的问题）
s = s.replace('''    missed = [r["tool"] for r in rows if r["verdict"] == "missed"]''',
              '''    missed = [r["tool"] for r in rows if r["verdict"] == "missed"]
    #: ★★ 「调用没调成」单列 —— ★ 它**既不是通过也不是失败**，★ 是**我们没测到** ✓
    call_failed = [r["tool"] for r in rows if not r.get("writer_ok")]''')
s = s.replace('''        "counts": counts, "missed": missed, "rows": rows,''',
              '''        "counts": counts, "missed": missed, "call_failed": call_failed, "rows": rows,''')
s = s.replace('''    print("★★ 硬红门禁（声明只读却观察到指纹变化）：**%d** 条 %s"
          % (len(missed), missed[:5] if missed else ""))''',
              '''    print("★★ 硬红门禁（声明只读却观察到指纹变化）：**%d** 条 %s"
          % (len(missed), missed[:5] if missed else ""))
    print("★ 调用没调成的（★ 我们没测到，不算通过也不算失败）：**%d** 条 %s"
          % (len(call_failed), call_failed[:5] if call_failed else ""))''')

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("classify 已把「没调成」放最前（★ 修掉假一致）")
